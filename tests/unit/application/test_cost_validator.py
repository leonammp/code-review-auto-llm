"""
Testes unitários para CostValidator
"""

import importlib

import pytest
from src.application.validators.cost_validator import CostValidator
from src.infrastructure.config.settings import ReviewLimits


@pytest.fixture
def default_limits() -> ReviewLimits:
    """Configuração padrão de limites"""
    return ReviewLimits(
        max_files_to_analyze=30,
        max_tokens_per_pr=50000,
        max_cost_per_pr_usd=0.50,
        min_pr_size_lines=10,
        max_pr_size_lines=2000,
        max_diff_lines_per_file=400,
        max_comment_length=150000,
    )


@pytest.fixture
def validator(default_limits: ReviewLimits) -> CostValidator:
    """Validator configurado com custo padrão"""
    return CostValidator(default_limits, model_cost_per_1k=0.002)


def test_estimate_cost_small_text(validator: CostValidator):
    """Testa estimativa de custo para texto pequeno"""
    text = "a" * 400  # 400 chars = ~100 tokens

    tokens, cost = validator.estimate_cost(text)

    assert tokens == 100
    assert cost == pytest.approx(0.0002, rel=1e-6)  # type: ignore  # 100 * 0.000002


def test_estimate_cost_large_text(validator: CostValidator):
    """Testa estimativa de custo para texto grande"""
    text = "a" * 200000  # 200k chars = ~50k tokens

    tokens, cost = validator.estimate_cost(text)

    assert tokens == 50000
    assert cost == pytest.approx(0.1, rel=1e-6)  # type: ignore  # 50000 * 0.000002


def test_validate_cost_within_limits(validator: CostValidator):
    """Testa que texto dentro dos limites passa"""
    text = "a" * 40000  # 40k chars = ~10k tokens, custo ~$0.02

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is True
    assert "10,000 tokens" in msg
    assert tokens == 10000
    assert cost == pytest.approx(0.02, rel=1e-6)  # type: ignore


def test_validate_cost_exceeds_token_limit(validator: CostValidator):
    """Testa que texto excedendo limite de tokens falha"""
    # 50001 tokens > 50000 (limite)
    text = "a" * 200004  # ~50001 tokens

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is False
    assert "Excede limite de tokens" in msg
    assert "50,001" in msg
    assert "50,000" in msg
    assert tokens == 50001
    assert cost > 0.05


def test_validate_cost_exceeds_cost_limit():
    """Testa que texto excedendo limite de custo falha"""
    limits = ReviewLimits(
        max_files_to_analyze=30,
        max_tokens_per_pr=500000,  # Limite alto de tokens
        max_cost_per_pr_usd=0.10,  # Limite baixo de custo ($0.10)
        min_pr_size_lines=10,
        max_pr_size_lines=2000,
        max_diff_lines_per_file=400,
        max_comment_length=150000,
    )
    validator = CostValidator(limits, model_cost_per_1k=0.002)

    # 60k tokens custaria $0.12, excedendo $0.10
    text = "a" * 240000  # ~60k tokens

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is False
    assert "Excede limite de custo" in msg
    assert "$0.1200" in msg or "$0.12" in msg
    assert cost > 0.10
    assert tokens == 60000


def test_validate_cost_at_token_boundary(validator: CostValidator):
    """Testa exatamente no limite de tokens"""
    # Exatamente 50000 tokens (limite)
    text = "a" * 200000

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is True  # No limite deve passar
    assert tokens == 50000
    assert cost == pytest.approx(0.1, rel=1e-6)  # type: ignore  # 50000 * 0.000002
    assert "50,000 tokens" in msg


def test_validate_cost_at_cost_boundary():
    """Testa exatamente no limite de custo"""
    limits = ReviewLimits(
        max_files_to_analyze=30,
        max_tokens_per_pr=500000,
        max_cost_per_pr_usd=0.10,  # $0.10 exato
        min_pr_size_lines=10,
        max_pr_size_lines=2000,
        max_diff_lines_per_file=400,
        max_comment_length=150000,
    )
    validator = CostValidator(limits, model_cost_per_1k=0.002)

    # 50k tokens = exatamente $0.10
    text = "a" * 200000

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is True  # No limite deve passar
    assert cost == pytest.approx(0.10, rel=1e-6)  # type: ignore
    assert tokens == 50000
    assert "$0.1000" in msg or "$0.10" in msg


def test_empty_text(validator: CostValidator):
    """Testa com texto vazio"""
    text = ""

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is True
    assert tokens == 0
    assert cost == 0.0
    assert "0 tokens" in msg or "tokens" in msg


def test_custom_model_cost():
    """Testa validator com custo de modelo diferente"""
    limits = ReviewLimits(
        max_files_to_analyze=30,
        max_tokens_per_pr=50000,
        max_cost_per_pr_usd=0.50,
        min_pr_size_lines=10,
        max_pr_size_lines=2000,
        max_diff_lines_per_file=400,
        max_comment_length=150000,
    )
    # Modelo mais caro: $0.01 por 1k tokens
    validator = CostValidator(limits, model_cost_per_1k=0.01)

    text = "a" * 40000  # ~10k tokens

    tokens, cost = validator.estimate_cost(text)

    assert tokens == 10000
    assert cost == pytest.approx(0.1, rel=1e-6)  # type: ignore  # 10000 * 0.00001 = $0.10


def test_token_to_char_ratio():
    """Testa que a ratio de token/char está correta"""
    validator_with_limits = CostValidator(
        ReviewLimits(
            max_files_to_analyze=30,
            max_tokens_per_pr=50000,
            max_cost_per_pr_usd=0.50,
            min_pr_size_lines=10,
            max_pr_size_lines=2000,
            max_diff_lines_per_file=400,
            max_comment_length=150000,
        )
    )

    # 4 chars = 1 token
    text = "abcd"
    tokens, _ = validator_with_limits.estimate_cost(text)

    assert tokens == 1

    # 8 chars = 2 tokens
    text = "abcd" * 2
    tokens, _ = validator_with_limits.estimate_cost(text)

    assert tokens == 2


def test_message_format(validator: CostValidator):
    """Testa formato da mensagem de sucesso"""
    text = "a" * 4000  # ~1000 tokens

    can_proceed, msg, tokens, cost = validator.validate_cost(text)

    assert can_proceed is True
    assert "1,000 tokens" in msg  # Verifica formatação com vírgula
    assert "$" in msg
    assert "0.0020" in msg or "0.002" in msg
    assert tokens == 1000
    assert cost == pytest.approx(0.002, rel=1e-6)  # type: ignore


def test_reload_cost_validator_module():
    """Testa que módulo cost_validator pode ser recarregado."""
    import src.application.validators.cost_validator as module

    reloaded = importlib.reload(module)

    assert hasattr(reloaded, "CostValidator")
