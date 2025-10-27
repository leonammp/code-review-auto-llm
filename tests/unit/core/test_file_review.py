"""
Testes para FileReview e Issue
"""

from src.core.domain.file_review import FileReview, Issue


def test_issue_creation():
    """Testa criação de Issue com linha"""
    issue = Issue(text="Missing type hint", line=42)

    assert issue.text == "Missing type hint"
    assert issue.line == 42


def test_issue_without_line():
    """Testa criação de Issue sem linha"""
    issue = Issue(text="General observation")

    assert issue.text == "General observation"
    assert issue.line is None


def test_file_review_empty():
    """Testa FileReview sem issues"""
    review = FileReview(filepath="src/main.py")

    assert review.filepath == "src/main.py"
    assert len(review.critical_issues) == 0
    assert len(review.important_issues) == 0
    assert len(review.suggestions) == 0
    assert review.has_issues is False
    assert review.total_issues == 0


def test_file_review_with_critical_issues():
    """Testa FileReview com issues críticos"""
    review = FileReview(
        filepath="src/auth.py",
        critical_issues=[
            Issue(text="SQL injection vulnerability", line=10),
            Issue(text="Hardcoded credentials", line=25),
        ],
    )

    assert len(review.critical_issues) == 2
    assert review.has_issues is True
    assert review.total_issues == 2


def test_file_review_with_important_issues():
    """Testa FileReview com issues importantes"""
    review = FileReview(
        filepath="src/utils.py", important_issues=[Issue(text="Missing error handling", line=15)]
    )

    assert len(review.important_issues) == 1
    assert review.has_issues is True
    assert review.total_issues == 1


def test_file_review_with_suggestions_only():
    """Testa FileReview apenas com sugestões (não conta como has_issues)"""
    review = FileReview(
        filepath="src/helpers.py",
        suggestions=[
            Issue(text="Consider using list comprehension", line=8),
            Issue(text="Add docstring", line=1),
        ],
    )

    assert len(review.suggestions) == 2
    assert review.has_issues is False  # Sugestões não contam
    assert review.total_issues == 2


def test_file_review_with_all_severities():
    """Testa FileReview com todos os tipos de issues"""
    review = FileReview(
        filepath="src/complex.py",
        critical_issues=[Issue(text="Critical", line=10)],
        important_issues=[Issue(text="Important", line=20)],
        suggestions=[Issue(text="Suggestion", line=30)],
    )

    assert review.has_issues is True
    assert review.total_issues == 3
    assert len(review.critical_issues) == 1
    assert len(review.important_issues) == 1
    assert len(review.suggestions) == 1


def test_file_review_referenced_lines():
    """Testa FileReview com linhas referenciadas"""
    review = FileReview(
        filepath="src/example.py",
        critical_issues=[Issue(text="Error", line=15)],
        referenced_lines=[10, 15, 20],
    )

    assert review.referenced_lines == [10, 15, 20]
    assert review.has_issues is True
