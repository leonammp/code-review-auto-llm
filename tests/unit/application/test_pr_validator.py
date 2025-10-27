"""
Testes unitários para PRValidator
"""

import importlib

import pytest
from src.application.validators.pr_validator import PRValidator
from src.core.domain.pull_request import PullRequestInfo
from src.infrastructure.config.settings import ReviewBehavior, ReviewLimits


@pytest.fixture
def default_behavior() -> ReviewBehavior:
    """Configuração padrão de comportamento"""
    return ReviewBehavior(
        skip_drafts=True,
        skip_label="skip-review",
        context_lines=6,
        post_summary_comment=True,
    )


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
def validator(
    default_behavior: ReviewBehavior, default_limits: ReviewLimits
) -> PRValidator:
    """Validator configurado"""
    return PRValidator(default_behavior, default_limits)


def create_pr(
    additions: int = 50,
    deletions: int = 20,
    is_draft: bool = False,
    labels: list[str] | None = None,
) -> PullRequestInfo:
    """Helper para criar PRs de teste"""
    return PullRequestInfo(
        id=1,
        title="Test PR",
        source_branch="feature/test",
        target_branch="main",
        is_draft=is_draft,
        additions=additions,
        deletions=deletions,
        changed_files_count=3,
        labels=labels or [],
    )


def test_should_review_normal_pr(validator: PRValidator):
    """Testa que PR normal deve ser revisada"""
    pr = create_pr(additions=100, deletions=50)

    should_review, reason = validator.should_review(pr)

    assert should_review is True
    assert "150 linhas" in reason
    assert "validada" in reason.lower()


def test_should_skip_draft_pr(validator: PRValidator):
    """Testa que PR draft é pulada"""
    pr = create_pr(is_draft=True)

    should_review, reason = validator.should_review(pr)

    assert should_review is False
    assert "draft" in reason.lower()


def test_should_skip_pr_with_skip_label(validator: PRValidator):
    """Testa que PR com label skip-review é pulada"""
    pr = create_pr(labels=["skip-review", "bug"])

    should_review, reason = validator.should_review(pr)

    assert should_review is False
    assert "skip-review" in reason


def test_should_skip_too_small_pr(validator: PRValidator):
    """Testa que PR muito pequena é pulada"""
    pr = create_pr(additions=3, deletions=2)  # 5 linhas, menos que min (10)

    should_review, reason = validator.should_review(pr)

    assert should_review is False
    assert "muito pequena" in reason.lower()
    assert "5 linhas" in reason


def test_should_review_but_warn_large_pr(validator: PRValidator):
    """Testa que PR grande é revisada mas com warning"""
    pr = create_pr(additions=1500, deletions=600)  # 2100 linhas, mais que max (2000)

    should_review, reason = validator.should_review(pr)

    assert should_review is True  # Não pula, mas avisa
    assert "⚠️" in reason or "grande" in reason.lower()
    assert "2100 linhas" in reason


def test_should_skip_draft_even_with_good_size(validator: PRValidator):
    """Testa que draft é pulado mesmo com tamanho bom"""
    pr = create_pr(additions=100, deletions=50, is_draft=True)

    should_review, reason = validator.should_review(pr)

    assert should_review is False
    assert "draft" in reason.lower()


def test_minimum_boundary_size(validator: PRValidator):
    """Testa boundary exato do tamanho mínimo"""
    # Exatamente no limite inferior (10 linhas)
    pr = create_pr(additions=6, deletions=4)  # Exatamente 10

    should_review, reason = validator.should_review(pr)

    assert should_review is True  # 10 linhas é o mínimo, deve passar
    assert "10 linhas" in reason
    assert "validada" in reason.lower()


def test_below_minimum_boundary(validator: PRValidator):
    """Testa logo abaixo do limite mínimo"""
    # 1 linha a menos que o mínimo
    pr = create_pr(additions=5, deletions=4)  # 9 linhas

    should_review, reason = validator.should_review(pr)

    assert should_review is False  # Menor que 10, deve falhar
    assert "muito pequena" in reason.lower()
    assert "9 linhas" in reason


def test_maximum_boundary_size(validator: PRValidator):
    """Testa boundary exato do tamanho máximo"""
    # Exatamente no limite superior (2000 linhas)
    pr = create_pr(additions=1200, deletions=800)  # Exatamente 2000

    should_review, reason = validator.should_review(pr)

    assert should_review is True  # No limite, sem warning
    assert "⚠️" not in reason


def test_above_maximum_boundary(validator: PRValidator):
    """Testa logo acima do limite máximo"""
    # 1 linha a mais que o máximo
    pr = create_pr(additions=1200, deletions=801)  # 2001 linhas

    should_review, reason = validator.should_review(pr)

    assert should_review is True  # Ainda revisa
    assert "⚠️" in reason or "grande" in reason.lower()


def test_custom_skip_label():
    """Testa validator com label customizada"""
    behavior = ReviewBehavior(
        skip_drafts=True,
        skip_label="no-review",  # Label diferente
        context_lines=6,
        post_summary_comment=True,
    )
    limits = ReviewLimits(
        max_files_to_analyze=30,
        max_tokens_per_pr=50000,
        max_cost_per_pr_usd=0.50,
        min_pr_size_lines=10,
        max_pr_size_lines=2000,
        max_diff_lines_per_file=400,
        max_comment_length=150000,
    )
    validator = PRValidator(behavior, limits)

    pr = create_pr(labels=["no-review"])

    should_review, reason = validator.should_review(pr)

    assert should_review is False
    assert "no-review" in reason


def test_skip_drafts_disabled():
    """Testa que com skip_drafts=False, drafts são revisados"""
    behavior = ReviewBehavior(
        skip_drafts=False,  # Não pula drafts
        skip_label="skip-review",
        context_lines=6,
        post_summary_comment=True,
    )
    limits = ReviewLimits(
        max_files_to_analyze=30,
        max_tokens_per_pr=50000,
        max_cost_per_pr_usd=0.50,
        min_pr_size_lines=10,
        max_pr_size_lines=2000,
        max_diff_lines_per_file=400,
        max_comment_length=150000,
    )
    validator = PRValidator(behavior, limits)

    pr = create_pr(additions=100, deletions=50, is_draft=True)

    should_review, _ = validator.should_review(pr)

    assert should_review is True  # Draft não é mais bloqueante


def test_reload_pr_validator_module():
    """Testa que módulo pr_validator pode ser recarregado."""
    import src.application.validators.pr_validator as module

    reloaded = importlib.reload(module)

    assert hasattr(reloaded, "PRValidator")
