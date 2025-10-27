"""
Testes para Config Settings
"""

import importlib

from pytest import MonkeyPatch
from src.infrastructure.config.settings import (
    AzureDevOpsConfig,
    Config,
    LLMConfig,
    ReviewBehavior,
    ReviewLimits,
    load_config,
)


def test_azure_devops_config_defaults(monkeypatch: MonkeyPatch) -> None:
    """Testa valores padrão do AzureDevOpsConfig"""
    # Limpa variáveis de ambiente que podem interferir
    monkeypatch.delenv("AZDO_PAT", raising=False)
    monkeypatch.delenv("AZDO_ORG", raising=False)
    monkeypatch.delenv("AZDO_PROJECT", raising=False)
    monkeypatch.delenv("AZDO_API_VERSION", raising=False)

    config = AzureDevOpsConfig()

    assert config.org == "finnetbrasil"
    assert config.project == ""
    assert config.pat == ""
    assert config.api_version == "7.0"


def test_azure_devops_config_get_token_from_env(monkeypatch: MonkeyPatch) -> None:
    """Testa get_token usando SYSTEM_ACCESSTOKEN"""
    monkeypatch.setenv("SYSTEM_ACCESSTOKEN", "system-token-123")

    config = AzureDevOpsConfig()
    token = config.get_token()

    assert token == "system-token-123"


def test_azure_devops_config_get_token_fallback_to_pat(monkeypatch: MonkeyPatch) -> None:
    """Testa get_token com fallback para PAT"""
    monkeypatch.delenv("SYSTEM_ACCESSTOKEN", raising=False)
    monkeypatch.setenv("AZDO_PAT", "personal-token-456")

    config = AzureDevOpsConfig()
    token = config.get_token()

    assert token == "personal-token-456"


def test_azure_devops_config_get_token_empty(monkeypatch: MonkeyPatch) -> None:
    """Testa get_token quando não há token configurado"""
    monkeypatch.delenv("SYSTEM_ACCESSTOKEN", raising=False)
    monkeypatch.delenv("AZDO_PAT", raising=False)

    config = AzureDevOpsConfig()
    token = config.get_token()

    assert token == ""


def test_llm_config_requires_api_base(monkeypatch: MonkeyPatch) -> None:
    """Testa que LLMConfig requer api_base"""
    monkeypatch.setenv("LITELLM_API_BASE", "https://api.example.com")
    monkeypatch.setenv("LITELLM_API_KEY", "key123")

    config = LLMConfig()  # type: ignore

    assert config.api_base == "https://api.example.com"
    assert config.api_key == "key123"


def test_llm_config_defaults(monkeypatch: MonkeyPatch) -> None:
    """Testa valores padrão do LLMConfig"""
    monkeypatch.setenv("LITELLM_API_BASE", "https://api.example.com")
    monkeypatch.setenv("LITELLM_API_KEY", "key123")

    config = LLMConfig()  # type: ignore

    assert config.model == "gpt-4.1-nano"
    assert config.max_tokens == 2500
    assert config.temperature == 0.2


def test_llm_config_custom_values(monkeypatch: MonkeyPatch) -> None:
    """Testa LLMConfig com valores customizados"""
    monkeypatch.setenv("LITELLM_API_BASE", "https://custom.api.com")
    monkeypatch.setenv("LITELLM_API_KEY", "custom-key")
    monkeypatch.setenv("LITELLM_MODEL", "gpt-4-turbo")
    monkeypatch.setenv("LITELLM_MAX_TOKENS", "5000")
    monkeypatch.setenv("LITELLM_TEMPERATURE", "0.5")

    config = LLMConfig()  # type: ignore

    assert config.model == "gpt-4-turbo"
    assert config.max_tokens == 5000
    assert config.temperature == 0.5


def test_review_limits_defaults(monkeypatch: MonkeyPatch) -> None:
    """Testa valores padrão do ReviewLimits"""
    # Limpa variáveis de ambiente que podem interferir
    monkeypatch.delenv("REVIEW_MAX_FILES_TO_ANALYZE", raising=False)
    monkeypatch.delenv("REVIEW_MAX_TOKENS_PER_PR", raising=False)
    monkeypatch.delenv("REVIEW_MAX_COST_PER_PR_USD", raising=False)
    monkeypatch.delenv("REVIEW_MIN_PR_SIZE_LINES", raising=False)
    monkeypatch.delenv("REVIEW_MAX_PR_SIZE_LINES", raising=False)
    monkeypatch.delenv("REVIEW_MAX_DIFF_LINES_PER_FILE", raising=False)
    monkeypatch.delenv("REVIEW_MAX_COMMENT_LENGTH", raising=False)

    limits = ReviewLimits()

    assert limits.max_files_to_analyze == 30
    assert limits.max_tokens_per_pr == 50000
    assert limits.max_cost_per_pr_usd == 0.50
    assert limits.min_pr_size_lines == 10
    assert limits.max_pr_size_lines == 2000
    assert limits.max_diff_lines_per_file == 400
    assert limits.max_comment_length == 150000


def test_review_limits_custom_values(monkeypatch: MonkeyPatch) -> None:
    """Testa ReviewLimits com valores customizados"""
    monkeypatch.setenv("REVIEW_MAX_FILES_TO_ANALYZE", "50")
    monkeypatch.setenv("REVIEW_MAX_TOKENS_PER_PR", "100000")
    monkeypatch.setenv("REVIEW_MAX_COST_PER_PR_USD", "1.00")

    limits = ReviewLimits()

    assert limits.max_files_to_analyze == 50
    assert limits.max_tokens_per_pr == 100000
    assert limits.max_cost_per_pr_usd == 1.00


def test_review_behavior_defaults():
    """Testa valores padrão do ReviewBehavior"""
    behavior = ReviewBehavior()

    assert behavior.skip_drafts is True
    assert behavior.skip_label == "skip-review"
    assert behavior.context_lines == 6
    assert behavior.post_summary_comment is True


def test_review_behavior_ignored_extensions():
    """Testa lista de extensões ignoradas"""
    behavior = ReviewBehavior()

    assert ".lock" in behavior.ignored_extensions
    assert ".min.js" in behavior.ignored_extensions
    assert ".png" in behavior.ignored_extensions
    assert "package-lock.json" in behavior.ignored_extensions


def test_review_behavior_ignored_paths():
    """Testa lista de paths ignorados"""
    behavior = ReviewBehavior()

    assert "node_modules/" in behavior.ignored_paths
    assert "dist/" in behavior.ignored_paths
    assert "__pycache__/" in behavior.ignored_paths


def test_review_behavior_custom_skip_label(monkeypatch: MonkeyPatch) -> None:
    """Testa customização do skip label"""
    monkeypatch.setenv("REVIEW_SKIP_LABEL", "no-review")

    behavior = ReviewBehavior()

    assert behavior.skip_label == "no-review"


def test_review_behavior_disable_skip_drafts(monkeypatch: MonkeyPatch) -> None:
    """Testa desabilitar skip de drafts"""
    monkeypatch.setenv("REVIEW_SKIP_DRAFTS", "false")

    behavior = ReviewBehavior()

    assert behavior.skip_drafts is False


def test_config_aggregation(monkeypatch: MonkeyPatch) -> None:
    """Testa agregação de todas as configs"""
    monkeypatch.setenv("LITELLM_API_BASE", "https://api.test.com")
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")

    config = Config()

    assert isinstance(config.azure, AzureDevOpsConfig)
    assert isinstance(config.llm, LLMConfig)
    assert isinstance(config.limits, ReviewLimits)
    assert isinstance(config.behavior, ReviewBehavior)


def test_load_config_function(monkeypatch: MonkeyPatch) -> None:
    """Testa função load_config"""
    monkeypatch.setenv("LITELLM_API_BASE", "https://api.test.com")
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")

    config = load_config()

    assert isinstance(config, Config)
    assert config.azure.org == "finnetbrasil"


def test_reload_settings_module(monkeypatch: MonkeyPatch) -> None:
    """Testa recarregamento do módulo settings para garantir cobertura."""
    import src.infrastructure.config.settings as module

    monkeypatch.delenv("SYSTEM_ACCESSTOKEN", raising=False)
    monkeypatch.setenv("LITELLM_API_BASE", "https://api.reload.com")
    monkeypatch.setenv("LITELLM_API_KEY", "reload-key")

    reloaded = importlib.reload(module)

    assert hasattr(reloaded, "AzureDevOpsConfig")
    assert hasattr(reloaded, "LLMConfig")
