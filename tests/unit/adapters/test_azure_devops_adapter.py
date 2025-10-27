"""
Testes para AzureDevOpsAdapter
"""

from __future__ import annotations

import base64
from collections import deque
from collections.abc import Callable
from typing import Any

import pytest
import requests
from pytest import MonkeyPatch
from src.adapters.azure_devops_adapter import AzureDevOpsAdapter
from src.infrastructure.config.settings import AzureDevOpsConfig


class FakeResponse:
    """Resposta fake com suporte a json/raise_for_status."""

    def __init__(self, json_data: Any, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code

    def json(self) -> Any:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status: {self.status_code}")


class FakeSession:
    """Session fake para capturar chamadas HTTP."""

    def __init__(self):
        self.headers: dict[str, str] = {}
        self.mounted: dict[str, Any] = {}
        self.get_calls: list[dict[str, Any]] = []
        self.post_calls: list[dict[str, Any]] = []
        self._get_responses: deque[FakeResponse] = deque()
        self._post_responses: deque[FakeResponse] = deque()

    def mount(self, prefix: str, adapter: Any) -> None:
        self.mounted[prefix] = adapter

    def queue_get(self, response: FakeResponse) -> None:
        self._get_responses.append(response)

    def queue_post(self, response: FakeResponse) -> None:
        self._post_responses.append(response)

    def get(self, url: str, params: dict[str, Any] | None = None, timeout: int | None = None):
        self.get_calls.append({"url": url, "params": params, "timeout": timeout})
        if not self._get_responses:
            raise AssertionError("Sem resposta fake para GET")
        return self._get_responses.popleft()

    def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ):
        self.post_calls.append(
            {"url": url, "json": json, "params": params, "timeout": timeout}
        )
        if not self._post_responses:
            raise AssertionError("Sem resposta fake para POST")
        return self._post_responses.popleft()


def make_config() -> AzureDevOpsConfig:
    """Cria config dummy para os testes."""
    return AzureDevOpsConfig(
        org="test-org",
        project="test-project",
        pat="token-123",
        api_version="7.0",
    )


@pytest.fixture
def make_adapter(monkeypatch: MonkeyPatch) -> AdapterFactory:
    """Factory que retorna adapter e session fake."""

    def _make() -> tuple[AzureDevOpsAdapter, FakeSession, AzureDevOpsConfig]:
        monkeypatch.delenv("SYSTEM_ACCESSTOKEN", raising=False)
        session = FakeSession()
        monkeypatch.setattr(
            "src.adapters.azure_devops_adapter.requests.Session", lambda: session
        )
        config = make_config()
        adapter = AzureDevOpsAdapter(config)
        return adapter, session, config

    return _make


def test_setup_session_configures_auth_and_retry(make_adapter: AdapterFactory):
    """Testa que a session tem auth e retry configurados."""
    adapter, session, config = make_adapter()

    assert adapter.base_url == f"https://dev.azure.com/{config.org}/{config.project}/_apis"
    expected_auth = base64.b64encode(f":{config.get_token()}".encode()).decode()
    assert session.headers["Authorization"] == f"Basic {expected_auth}"
    assert session.headers["Content-Type"] == "application/json"
    assert "https://" in session.mounted


def test_get_pr_info_returns_normalized_pull_request(make_adapter: AdapterFactory):
    """Testa que get_pr_info normaliza dados da PR."""
    adapter, session, _ = make_adapter()
    session.queue_get(
        FakeResponse(
            {
                "pullRequestId": 42,
                "title": "Improve login",
                "sourceRefName": "refs/heads/feature/login",
                "targetRefName": "refs/heads/main",
                "isDraft": True,
                "labels": [{"name": "bug"}, {"name": "important"}],
            }
        )
    )

    pr_info = adapter.get_pr_info("repo", 42)

    assert pr_info.id == 42
    assert pr_info.title == "Improve login"
    assert pr_info.source_branch == "feature/login"
    assert pr_info.target_branch == "main"
    assert pr_info.is_draft is True
    assert pr_info.labels == ["bug", "important"]
    assert session.get_calls[0]["url"].endswith("/pullrequests/42")


def test_get_pr_files_returns_last_iteration_changes(make_adapter: AdapterFactory):
    """Testa que get_pr_files usa a última iteração da PR."""
    adapter, session, _ = make_adapter()
    session.queue_get(FakeResponse({"value": [{"id": 1}, {"id": 8}]}))
    session.queue_get(
        FakeResponse(
            {
                "changeEntries": [
                    {"item": {"path": "/src/app.py"}, "changeType": "edit"},
                    {"item": {"path": "/src/utils.py"}, "changeType": "add"},
                ]
            }
        )
    )

    files = adapter.get_pr_files("repo", 99)

    assert files == [
        {"item": {"path": "/src/app.py"}, "changeType": "edit"},
        {"item": {"path": "/src/utils.py"}, "changeType": "add"},
    ]
    assert session.get_calls[0]["url"].endswith("/pullrequests/99/iterations")
    assert session.get_calls[1]["url"].endswith("/pullrequests/99/iterations/8/changes")


def test_get_pr_files_returns_empty_when_no_iterations(make_adapter: AdapterFactory):
    """Testa que get_pr_files retorna lista vazia sem iterações."""
    adapter, session, _ = make_adapter()
    session.queue_get(FakeResponse({"value": []}))

    files = adapter.get_pr_files("repo", 77)

    assert files == []
    assert len(session.get_calls) == 1


def test_post_comment_truncates_long_payload(make_adapter: AdapterFactory):
    """Testa que post_comment trunca comentários grandes."""
    adapter, session, _ = make_adapter()
    session.queue_post(FakeResponse({}, status_code=200))

    huge_comment = "A" * 150500
    result = adapter.post_comment("repo", 5, "src/app.py", 10, 20, huge_comment)

    assert result is True
    payload = session.post_calls[0]["json"]
    content = payload["comments"][0]["content"]
    assert content.endswith("[... truncado]")
    assert len(content) == 150000 + len("\n\n[... truncado]")
    assert payload["threadContext"]["filePath"] == "src/app.py"
    assert payload["threadContext"]["rightFileStart"]["line"] == 10
    assert payload["threadContext"]["rightFileEnd"]["line"] == 20


def test_post_summary_comment_formats_stats(make_adapter: AdapterFactory):
    """Testa que post_summary_comment monta texto com estatísticas."""
    adapter, session, _ = make_adapter()
    session.queue_post(FakeResponse({}, status_code=200))

    stats = {"files_reviewed": 2, "critical": 1, "important": 3, "suggestions": 4}
    result = adapter.post_summary_comment("repo", 12, stats)

    assert result is True
    payload = session.post_calls[0]["json"]
    content = payload["comments"][0]["content"]
    assert "Arquivos analisados: 2" in content
    assert "Comentários: 1🔴 3🟡 4🟢" in content
AdapterFactory = Callable[
    [], tuple[AzureDevOpsAdapter, "FakeSession", AzureDevOpsConfig]
]
