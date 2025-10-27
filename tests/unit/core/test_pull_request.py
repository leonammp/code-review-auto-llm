"""
Testes unitários para PullRequestInfo
"""

from src.core.domain.pull_request import PullRequestInfo


def test_pull_request_info_creation():
    """Testa criação básica de PullRequestInfo"""
    pr = PullRequestInfo(
        id=123,
        title="Test PR",
        source_branch="feature/test",
        target_branch="main",
        is_draft=False,
        additions=50,
        deletions=20,
        changed_files_count=3,
        labels=["enhancement"],
    )

    assert pr.id == 123
    assert pr.title == "Test PR"
    assert pr.source_branch == "feature/test"
    assert pr.target_branch == "main"
    assert pr.is_draft is False
    assert pr.additions == 50
    assert pr.deletions == 20
    assert pr.changed_files_count == 3
    assert pr.labels == ["enhancement"]


def test_total_changes():
    """Testa cálculo de total_changes"""
    pr = PullRequestInfo(
        id=1,
        title="Test",
        source_branch="feat/x",
        target_branch="main",
        is_draft=False,
        additions=100,
        deletions=50,
        changed_files_count=2,
    )

    assert pr.total_changes == 150  # 100 + 50


def test_should_skip_draft():
    """Testa que PRs draft devem ser puladas"""
    pr = PullRequestInfo(
        id=1,
        title="Draft PR",
        source_branch="feat/x",
        target_branch="main",
        is_draft=True,
        additions=10,
        deletions=5,
        changed_files_count=1,
    )

    assert pr.should_skip is True


def test_should_skip_label():
    """Testa que PRs com skip-review devem ser puladas"""
    pr = PullRequestInfo(
        id=1,
        title="Test PR",
        source_branch="feat/x",
        target_branch="main",
        is_draft=False,
        additions=10,
        deletions=5,
        changed_files_count=1,
        labels=["skip-review", "bug"],
    )

    assert pr.should_skip is True


def test_should_not_skip():
    """Testa que PRs normais não devem ser puladas"""
    pr = PullRequestInfo(
        id=1,
        title="Normal PR",
        source_branch="feat/x",
        target_branch="main",
        is_draft=False,
        additions=10,
        deletions=5,
        changed_files_count=1,
        labels=["enhancement"],
    )

    assert pr.should_skip is False


def test_empty_labels_default():
    """Testa que labels tem default de lista vazia"""
    pr = PullRequestInfo(
        id=1,
        title="Test",
        source_branch="feat/x",
        target_branch="main",
        is_draft=False,
        additions=10,
        deletions=5,
        changed_files_count=1,
    )

    assert pr.labels == []
