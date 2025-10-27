"""
Testes para DiffAdapter
"""

import base64
from typing import Any

import pytest
from src.adapters.diff_adapter import DiffAdapter
from src.infrastructure.config.settings import AzureDevOpsConfig, ReviewBehavior, ReviewLimits


def make_adapter(max_diff_lines: int = 3) -> DiffAdapter:
    """Cria adapter configurado para testes."""
    behavior = ReviewBehavior()
    limits = ReviewLimits(max_diff_lines_per_file=max_diff_lines)
    azure_config = AzureDevOpsConfig(org="org", project="proj", pat="token")
    return DiffAdapter(behavior, limits, azure_config)


def test_should_include_file_allows_relevant_paths():
    """Testa que arquivos relevantes não são filtrados."""
    adapter = make_adapter()

    assert adapter.should_include_file("src/app.py") is True


def test_should_include_file_blocks_ignored_extensions():
    """Testa que extensões ignoradas são filtradas."""
    adapter = make_adapter()

    assert adapter.should_include_file("package-lock.json") is False
    assert adapter.should_include_file("static/logo.png") is False


def test_should_include_file_blocks_ignored_paths():
    """Testa que pastas ignoradas são filtradas."""
    adapter = make_adapter()

    assert adapter.should_include_file("node_modules/lib/index.js") is False
    assert adapter.should_include_file("src/__pycache__/main.pyc") is False


def test_truncate_diff_returns_original_when_within_limit():
    """Testa que diffs menores que o limite permanecem intactos."""
    adapter = make_adapter(max_diff_lines=5)
    diff_lines = ["line1", "line2", "line3"]

    truncated = adapter.truncate_diff(diff_lines, adapter.limits.max_diff_lines_per_file)

    assert truncated == diff_lines


def test_truncate_diff_cuts_when_exceeding_limit():
    """Testa que diffs maiores que o limite são truncados."""
    adapter = make_adapter(max_diff_lines=2)
    diff_lines = ["line1", "line2", "line3", "line4"]

    truncated = adapter.truncate_diff(diff_lines, adapter.limits.max_diff_lines_per_file)

    assert truncated == ["line1", "line2"]


class FakeResponse:
    def __init__(self, text: str):
        self.text = text


class FakeSession:
    def __init__(self):
        self.headers: dict[str, str] = {}
        self.get_calls: list[dict[str, object]] = []
        self._queue: list[object] = []

    def queue(self, response: object) -> None:
        self._queue.append(response)

    def get(self, url: str, params: dict[str, str] | None = None, timeout: int | None = None):
        self.get_calls.append({"url": url, "params": params, "timeout": timeout})
        if not self._queue:
            raise AssertionError("Sem resposta fake")
        response = self._queue.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_setup_session_configures_auth_header(monkeypatch: pytest.MonkeyPatch):
    """Testa que _setup_session adiciona header Authorization básico."""
    session = FakeSession()
    monkeypatch.setattr("src.adapters.diff_adapter.requests.Session", lambda: session)

    adapter = make_adapter()

    expected = base64.b64encode(b":token").decode()
    assert session.headers["Authorization"] == f"Basic {expected}"
    assert adapter.session is session


def test_generate_diff_builds_output(monkeypatch: pytest.MonkeyPatch):
    """Testa geração de diff com truncamento e contagem de linhas."""
    session = FakeSession()
    monkeypatch.setattr("src.adapters.diff_adapter.requests.Session", lambda: session)

    adapter = make_adapter(max_diff_lines=3)

    base_content = "line1\nline2\nline3\n"
    source_content = "line1\nline2 changed\nline3\nline4 extra\n"
    session.queue(FakeResponse(base_content))
    session.queue(FakeResponse(source_content))

    files: list[Any] = [{"item": {"path": "/src/app.py"}, "changeType": "edit"}]

    diff_text, additions, deletions = adapter.generate_diff(
        "repo", files, "feature", "main"
    )

    assert "Arquivo 1" in diff_text
    assert "```diff" in diff_text
    assert "..." in diff_text  # indica truncamento
    assert additions > 0
    assert deletions > 0


def test_generate_diff_handles_errors(monkeypatch: pytest.MonkeyPatch):
    """Testa que erros ao buscar arquivo são reportados no diff."""
    session = FakeSession()
    monkeypatch.setattr("src.adapters.diff_adapter.requests.Session", lambda: session)

    adapter = make_adapter()

    session.queue(Exception("fail"))

    files: list[Any] = [{"item": {"path": "/src/fail.py"}, "changeType": "edit"}]

    diff_text, additions, deletions = adapter.generate_diff(
        "repo", files, "source", "target"
    )

    assert "Erro lendo arquivo" in diff_text
    assert additions == 0
    assert deletions == 0
