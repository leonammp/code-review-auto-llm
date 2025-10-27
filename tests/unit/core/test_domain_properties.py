"""
Testes adicionais para aumentar cobertura dos domínios
"""

from src.core.domain.file_review import FileReview, Issue
from src.core.domain.pull_request import PullRequestInfo
from src.core.domain.review_result import ReviewResult


def test_file_review_properties():
    """Testa todas as propriedades de FileReview"""
    review = FileReview(
        filepath="test.py",
        critical_issues=[Issue(text="Critical", line=1)],
        important_issues=[Issue(text="Important", line=2)],
        suggestions=[Issue(text="Suggestion", line=3)],
        referenced_lines=[1, 2, 3],
    )

    # Testa has_issues
    assert review.has_issues is True

    # Testa total_issues
    assert review.total_issues == 3

    # Testa filepath
    assert review.filepath == "test.py"

    # Testa listas
    assert len(review.critical_issues) == 1
    assert len(review.important_issues) == 1
    assert len(review.suggestions) == 1
    assert review.referenced_lines == [1, 2, 3]


def test_pull_request_properties():
    """Testa todas as propriedades de PullRequestInfo"""
    pr = PullRequestInfo(
        id=100,
        title="Test PR",
        source_branch="feature/test",
        target_branch="main",
        is_draft=False,
        additions=50,
        deletions=30,
        changed_files_count=5,
        labels=[],
    )

    # Testa total_changes
    assert pr.total_changes == 80  # 50 + 30

    # Testa should_skip
    assert pr.should_skip is False

    # Testa campos
    assert pr.id == 100
    assert pr.title == "Test PR"
    assert pr.source_branch == "feature/test"
    assert pr.target_branch == "main"
    assert pr.is_draft is False
    assert pr.additions == 50
    assert pr.deletions == 30
    assert pr.changed_files_count == 5


def test_pull_request_should_skip_draft():
    """Testa should_skip quando é draft"""
    pr = PullRequestInfo(
        id=101,
        title="Draft PR",
        source_branch="feature/draft",
        target_branch="main",
        is_draft=True,
        additions=10,
        deletions=5,
        changed_files_count=2,
    )

    assert pr.should_skip is True


def test_pull_request_should_skip_label():
    """Testa should_skip quando tem label skip-review"""
    pr = PullRequestInfo(
        id=102,
        title="Skip PR",
        source_branch="feature/skip",
        target_branch="main",
        is_draft=False,
        additions=20,
        deletions=10,
        changed_files_count=3,
        labels=["skip-review", "other-label"],
    )

    assert pr.should_skip is True


def test_review_result_properties():
    """Testa todas as propriedades de ReviewResult"""
    pr_info = PullRequestInfo(
        id=200,
        title="Review PR",
        source_branch="feature/review",
        target_branch="main",
        is_draft=False,
        additions=100,
        deletions=50,
        changed_files_count=3,
    )

    files = [
        FileReview(
            filepath="file1.py",
            critical_issues=[Issue(text="C1", line=1), Issue(text="C2", line=2)],
            important_issues=[Issue(text="I1", line=3)],
            suggestions=[],
        ),
        FileReview(
            filepath="file2.py",
            critical_issues=[],
            important_issues=[Issue(text="I2", line=4)],
            suggestions=[Issue(text="S1", line=5), Issue(text="S2", line=6)],
        ),
    ]

    result = ReviewResult(
        pr_info=pr_info,
        files=files,
        total_tokens_used=3000,
        estimated_cost_usd=0.06,
        review_text="Complete review",
    )

    # Testa stats
    stats = result.stats
    assert stats["files_reviewed"] == 2
    assert stats["critical"] == 2
    assert stats["important"] == 2
    assert stats["suggestions"] == 2

    # Testa campos
    assert result.total_tokens_used == 3000
    assert result.estimated_cost_usd == 0.06
    assert result.review_text == "Complete review"
    assert len(result.files) == 2


def test_issue_models():
    """Testa modelos Issue detalhadamente"""
    # Issue com linha
    issue1 = Issue(text="Error on line 10", line=10)
    assert issue1.text == "Error on line 10"
    assert issue1.line == 10

    # Issue sem linha
    issue2 = Issue(text="General comment")
    assert issue2.text == "General comment"
    assert issue2.line is None


def test_file_review_empty_defaults():
    """Testa valores default de FileReview"""
    review = FileReview(filepath="empty.py")

    assert review.filepath == "empty.py"
    assert review.critical_issues == []
    assert review.important_issues == []
    assert review.suggestions == []
    assert review.referenced_lines == []
    assert review.has_issues is False
    assert review.total_issues == 0


def test_pull_request_default_labels():
    """Testa label padrão vazio"""
    pr = PullRequestInfo(
        id=300,
        title="PR without labels",
        source_branch="feature",
        target_branch="main",
        is_draft=False,
        additions=10,
        deletions=5,
        changed_files_count=1,
    )

    assert pr.labels == []
    assert pr.should_skip is False


def test_review_result_empty_files():
    """Testa ReviewResult sem arquivos"""
    pr_info = PullRequestInfo(
        id=400,
        title="Empty result",
        source_branch="feature",
        target_branch="main",
        is_draft=False,
        additions=0,
        deletions=0,
        changed_files_count=0,
    )

    result = ReviewResult(
        pr_info=pr_info,
        files=[],
        total_tokens_used=100,
        estimated_cost_usd=0.002,
        review_text="No files to review",
    )

    stats = result.stats
    assert stats["files_reviewed"] == 0
    assert stats["critical"] == 0
    assert stats["important"] == 0
    assert stats["suggestions"] == 0
