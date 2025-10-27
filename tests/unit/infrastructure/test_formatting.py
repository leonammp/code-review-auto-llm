"""
Testes para formatting utilities
"""

from src.core.domain.file_review import FileReview, Issue
from src.infrastructure.utils.formatting import calculate_line_range, format_file_comment


def test_calculate_line_range_empty():
    """Testa cálculo de range com lista vazia"""
    start, end = calculate_line_range([])

    assert start == 1
    assert end == 6


def test_calculate_line_range_single_line():
    """Testa cálculo de range com uma única linha"""
    start, end = calculate_line_range([50])

    assert start == 44  # 50 - 6
    assert end == 56  # 50 + 6


def test_calculate_line_range_multiple_lines():
    """Testa cálculo de range com múltiplas linhas (usa mediana)"""
    start, end = calculate_line_range([10, 20, 30, 40, 50])

    # Mediana = 30 (elemento do meio)
    assert start == 24  # 30 - 6
    assert end == 36  # 30 + 6


def test_calculate_line_range_with_custom_context():
    """Testa cálculo de range com contexto customizado"""
    start, end = calculate_line_range([100], context=10)

    assert start == 90  # 100 - 10
    assert end == 110  # 100 + 10


def test_calculate_line_range_near_start():
    """Testa cálculo de range próximo ao início do arquivo"""
    start, end = calculate_line_range([3])

    assert start == 1  # Não pode ser negativo
    assert end == 9  # 3 + 6


def test_calculate_line_range_even_number():
    """Testa cálculo de range com número par de linhas"""
    start, end = calculate_line_range([10, 20, 30, 40])

    # Com 4 elementos, mediana é o 2º elemento (índice 2)
    assert start == 24  # 30 - 6
    assert end == 36  # 30 + 6


def test_format_file_comment_only_critical():
    """Testa formatação de comentário apenas com issues críticos"""
    review = FileReview(
        filepath="src/auth.py",
        critical_issues=[
            Issue(text="SQL injection risk", line=15),
            Issue(text="Missing input validation", line=20),
        ],
    )

    comment = format_file_comment(review)

    assert "**Arquivo: `src/auth.py`**" in comment
    assert "🔴 Crítico:" in comment
    assert "SQL injection risk" in comment
    assert "Missing input validation" in comment
    assert "🟡 Importante:" not in comment
    assert "🟢 Sugestão:" not in comment


def test_format_file_comment_only_important():
    """Testa formatação de comentário apenas com issues importantes"""
    review = FileReview(
        filepath="src/utils.py", important_issues=[Issue(text="Missing error handling", line=30)]
    )

    comment = format_file_comment(review)

    assert "**Arquivo: `src/utils.py`**" in comment
    assert "🟡 Importante:" in comment
    assert "Missing error handling" in comment
    assert "🔴 Crítico:" not in comment


def test_format_file_comment_only_suggestions():
    """Testa formatação de comentário apenas com sugestões"""
    review = FileReview(
        filepath="src/helpers.py",
        suggestions=[
            Issue(text="Consider using list comprehension", line=8),
            Issue(text="Add type hints", line=12),
        ],
    )

    comment = format_file_comment(review)

    assert "**Arquivo: `src/helpers.py`**" in comment
    assert "🟢 Sugestão:" in comment
    assert "Consider using list comprehension" in comment
    assert "Add type hints" in comment


def test_format_file_comment_all_severities():
    """Testa formatação de comentário com todas as severidades"""
    review = FileReview(
        filepath="src/main.py",
        critical_issues=[Issue(text="Critical issue", line=10)],
        important_issues=[Issue(text="Important issue", line=20)],
        suggestions=[Issue(text="Suggestion", line=30)],
    )

    comment = format_file_comment(review)

    assert "**Arquivo: `src/main.py`**" in comment
    assert "🔴 Crítico:" in comment
    assert "Critical issue" in comment
    assert "🟡 Importante:" in comment
    assert "Important issue" in comment
    assert "🟢 Sugestão:" in comment
    assert "Suggestion" in comment


def test_format_file_comment_empty():
    """Testa formatação de comentário sem issues"""
    review = FileReview(filepath="src/empty.py")

    comment = format_file_comment(review)

    assert "**Arquivo: `src/empty.py`**" in comment
    assert "🔴 Crítico:" not in comment
    assert "🟡 Importante:" not in comment
    assert "🟢 Sugestão:" not in comment


def test_format_file_comment_multiline_issues():
    """Testa formatação de comentário com issues de múltiplas linhas"""
    review = FileReview(
        filepath="src/complex.py",
        critical_issues=[
            Issue(text="Very long issue description that spans multiple words", line=100)
        ],
    )

    comment = format_file_comment(review)

    assert "Very long issue description that spans multiple words" in comment
    assert comment.count("-") >= 1  # Pelo menos um item de lista
