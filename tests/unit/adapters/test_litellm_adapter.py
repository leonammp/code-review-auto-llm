"""
Testes para LiteLLMAdapter
"""

from typing import Any

import pytest
from src.adapters.litellm_adapter import LiteLLMAdapter
from src.core.domain.pull_request import PullRequestInfo
from src.infrastructure.config.settings import LLMConfig


class TestableLiteLLMAdapter(LiteLLMAdapter):
    """Exponibiliza helper público para testes."""

    def build_user_prompt(
        self,
        pr_info: PullRequestInfo,
        diff_text: str,
        custom_rules: str | None = None,
    ) -> str:
        return self._build_user_prompt(pr_info, diff_text, custom_rules)


def make_adapter() -> TestableLiteLLMAdapter:
    """Cria adapter configurado com valores dummy."""
    config = LLMConfig(
        api_base="https://example.com",
        api_key="dummy-key",
        model="gpt-4.1-nano",
        max_tokens=512,
        temperature=0.1,
    )
    return TestableLiteLLMAdapter(config)


def make_pr() -> PullRequestInfo:
    """Cria PullRequestInfo para os testes."""
    return PullRequestInfo(
        id=7,
        title="Add login flow",
        source_branch="feature/login",
        target_branch="main",
        is_draft=False,
        additions=10,
        deletions=2,
        changed_files_count=1,
        labels=[],
    )


def test_build_user_prompt_includes_metadata_and_rules():
    """Testa que o prompt inclui metadados e regras customizadas."""
    adapter = make_adapter()
    pr_info = make_pr()
    custom_rules = "- Regra 1\n- Regra 2"
    diff_text = "```diff\n+ def foo():\n+    return True\n```"

    prompt = adapter.build_user_prompt(pr_info, diff_text, custom_rules)

    assert "Add login flow" in prompt
    assert "feature/login" in prompt
    assert "Regra 1" in prompt
    assert diff_text in prompt


def test_build_user_prompt_uses_default_rules_when_none():
    """Testa que prompt usa texto padrão quando não há regras customizadas."""
    adapter = make_adapter()
    pr_info = make_pr()

    prompt = adapter.build_user_prompt(pr_info, diff_text="conteúdo diff", custom_rules=None)

    assert "Nenhuma regra customizada para este repositório." in prompt


def test_generate_review_calls_completion(monkeypatch: pytest.MonkeyPatch):
    """Testa que generate_review invoca litellm.completion com templates carregados."""
    adapter = make_adapter()
    adapter.system_template = "system"
    adapter.user_template = "Diff: {diff_content}"
    called: dict[str, Any] = {}

    class FakeMessage:
        def __init__(self, content: str | None):
            self.content = content

    class FakeChoice:
        def __init__(self, content: str | None):
            self.message = FakeMessage(content)

    class FakeResponse:
        def __init__(self, content: str | None):
            self.choices = [FakeChoice(content)]

    def fake_completion(**kwargs: Any) -> FakeResponse:
        called.update(kwargs)
        return FakeResponse("Review text")

    monkeypatch.setattr("src.adapters.litellm_adapter.completion", fake_completion)

    pr_info = make_pr()
    diff_text = "```diff\n+ change\n```"

    result = adapter.generate_review(diff_text, pr_info, custom_rules="rule")

    assert result == "Review text"
    assert called["messages"][1]["content"].startswith("Diff:")  # type: ignore[index]
    assert called["model"] == adapter.config.model


def test_generate_review_returns_empty_when_no_content(monkeypatch: pytest.MonkeyPatch):
    """Testa que generate_review retorna string vazia quando não há conteúdo."""
    adapter = make_adapter()
    adapter.system_template = "system"
    adapter.user_template = "Prompt"

    class FakeMessage:
        def __init__(self):
            self.content = None

    class FakeChoice:
        def __init__(self):
            self.message = FakeMessage()

    class FakeResponse:
        def __init__(self):
            self.choices = [FakeChoice()]

    def fake_completion_empty(**_: Any) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr(
        "src.adapters.litellm_adapter.completion",
        fake_completion_empty,
    )

    result = adapter.generate_review("diff", make_pr())

    assert result == ""
