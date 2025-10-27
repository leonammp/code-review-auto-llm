"""
Testes para print_summary
"""

from pytest import CaptureFixture
from src.core.domain.file_review import FileReview, Issue
from src.core.domain.pull_request import PullRequestInfo
from src.core.domain.review_result import ReviewResult
from src.infrastructure.utils.output import print_summary


def make_review_result(with_details: bool = False) -> ReviewResult:
    """Cria ReviewResult para testes."""
    pr_info = PullRequestInfo(
        id=101,
        title="Improve security checks",
        source_branch="feature/security",
        target_branch="main",
        is_draft=False,
        additions=20,
        deletions=5,
        changed_files_count=1,
        labels=[],
    )
    file_review = FileReview(
        filepath="src/security.py",
        critical_issues=[Issue(text="Na linha 10 `validate`: falta sanitizar input", line=10)],
        important_issues=[Issue(text="Na linha 20 `log`: adicionar contexto de usuário", line=20)],
        suggestions=[Issue(text="Na linha 30: considerar extração de helper", line=30)],
        referenced_lines=[10, 20, 30] if with_details else [],
    )
    return ReviewResult(
        pr_info=pr_info,
        files=[file_review],
        total_tokens_used=1200,
        estimated_cost_usd=0.05,
        review_text="{}",
    )


def test_print_summary_outputs_key_information(capsys: CaptureFixture[str]):
    """Testa que o resumo apresenta informações principais."""
    result = make_review_result()

    print_summary(result, show_details=False)

    captured = capsys.readouterr().out
    assert "PR #101" in captured
    assert "Improve security checks" in captured
    assert "Críticos: 1" in captured
    assert "Sugestões: 1" in captured
    assert "$0.0500" in captured


def test_print_summary_shows_detailed_comments(capsys: CaptureFixture[str]):
    """Testa que detalhes são exibidos quando solicitado."""
    result = make_review_result(with_details=True)

    print_summary(result, show_details=True)

    captured = capsys.readouterr().out
    assert "📋 COMENTÁRIOS QUE SERIAM POSTADOS" in captured
    assert "src/security.py" in captured
    assert "Na linha 10" in captured
