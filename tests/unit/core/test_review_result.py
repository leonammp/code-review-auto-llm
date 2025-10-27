"""
Testes para ReviewResult
"""

from src.core.domain.file_review import FileReview, Issue
from src.core.domain.pull_request import PullRequestInfo
from src.core.domain.review_result import ReviewResult


def test_review_result_creation():
    """Testa criação de ReviewResult"""
    pr_info = PullRequestInfo(
        id=123,
        title="Test PR",
        source_branch="feature",
        target_branch="main",
        additions=50,
        deletions=20,
        is_draft=False,
        changed_files_count=3,
    )

    result = ReviewResult(
        pr_info=pr_info,
        total_tokens_used=1000,
        estimated_cost_usd=0.02,
        review_text="Review completed",
    )

    assert result.pr_info.id == 123
    assert result.total_tokens_used == 1000
    assert result.estimated_cost_usd == 0.02
    assert result.review_text == "Review completed"
    assert len(result.files) == 0


def test_review_result_with_files():
    """Testa ReviewResult com arquivos revisados"""
    pr_info = PullRequestInfo(
        id=456,
        title="Feature PR",
        source_branch="feature",
        target_branch="main",
        additions=100,
        deletions=50,
        is_draft=False,
        changed_files_count=2,
    )

    files = [
        FileReview(filepath="src/main.py", critical_issues=[Issue(text="Critical bug", line=10)]),
        FileReview(
            filepath="src/utils.py", important_issues=[Issue(text="Important issue", line=20)]
        ),
    ]

    result = ReviewResult(
        pr_info=pr_info,
        files=files,
        total_tokens_used=2500,
        estimated_cost_usd=0.05,
        review_text="Review with files",
    )

    assert len(result.files) == 2
    assert result.files[0].filepath == "src/main.py"
    assert result.files[1].filepath == "src/utils.py"


def test_review_result_stats_empty():
    """Testa estatísticas com review vazio"""
    pr_info = PullRequestInfo(
        id=789,
        title="Empty PR",
        source_branch="test",
        target_branch="main",
        additions=0,
        deletions=0,
        is_draft=False,
        changed_files_count=0,
    )

    result = ReviewResult(
        pr_info=pr_info, total_tokens_used=100, estimated_cost_usd=0.001, review_text="Empty review"
    )

    stats = result.stats
    assert stats["files_reviewed"] == 0
    assert stats["critical"] == 0
    assert stats["important"] == 0
    assert stats["suggestions"] == 0


def test_review_result_stats_with_issues():
    """Testa estatísticas com múltiplos issues"""
    pr_info = PullRequestInfo(
        id=999,
        title="Complex PR",
        source_branch="develop",
        target_branch="main",
        additions=200,
        deletions=100,
        is_draft=False,
        changed_files_count=2,
    )

    files = [
        FileReview(
            filepath="src/api.py",
            critical_issues=[Issue(text="Critical 1", line=10), Issue(text="Critical 2", line=20)],
            important_issues=[Issue(text="Important", line=30)],
            suggestions=[Issue(text="Suggestion", line=40)],
        ),
        FileReview(
            filepath="src/models.py",
            critical_issues=[Issue(text="Critical 3", line=50)],
            suggestions=[Issue(text="Suggestion 1", line=60), Issue(text="Suggestion 2", line=70)],
        ),
    ]

    result = ReviewResult(
        pr_info=pr_info,
        files=files,
        total_tokens_used=5000,
        estimated_cost_usd=0.10,
        review_text="Complex review",
    )

    stats = result.stats
    assert stats["files_reviewed"] == 2
    assert stats["critical"] == 3
    assert stats["important"] == 1
    assert stats["suggestions"] == 3
