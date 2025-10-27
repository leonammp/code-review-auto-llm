"""
Testes unitários para ReviewParser
"""

import json

import pytest
from src.application.parsers.review_parser import ReviewParser
from src.core.domain.file_review import Issue


@pytest.fixture
def parser() -> ReviewParser:
    """Parser configurado"""
    return ReviewParser()


def test_parse_valid_json(parser: ReviewParser):
    """Testa parsing de JSON válido"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "src/example.py",
                "critical_issues": [{"message": "SQL Injection vulnerability", "line": 10}],
                "important_issues": [{"message": "Missing error handling", "line": 15}],
                "suggestions": [{"message": "Consider using type hints", "line": 5}],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 1
    assert files[0].filepath == "src/example.py"
    assert len(files[0].critical_issues) == 1
    assert len(files[0].important_issues) == 1
    assert len(files[0].suggestions) == 1
    assert files[0].total_issues == 3
    assert files[0].referenced_lines == [5, 10, 15]


def test_parse_json_with_markdown_wrapper(parser: ReviewParser):
    """Testa parsing de JSON envolto em markdown code block"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [],
                "important_issues": [{"message": "Issue", "line": 1}],
                "suggestions": [],
            }
        ]
    }
    review_text = f"```json\n{json.dumps(review_json)}\n```"

    files = parser.parse(review_text)

    assert len(files) == 1
    assert files[0].filepath == "test.py"


def test_parse_json_with_generic_code_block(parser: ReviewParser):
    """Testa parsing de JSON envolto em code block genérico"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [{"message": "Bug", "line": 10}],
                "important_issues": [],
                "suggestions": [],
            }
        ]
    }
    review_text = f"```\n{json.dumps(review_json)}\n```"

    files = parser.parse(review_text)

    assert len(files) == 1


def test_parse_empty_files_list(parser: ReviewParser):
    """Testa parsing com lista vazia de arquivos"""
    review_json: dict[str, list[dict[str, object]]] = {"files": []}
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 0


def test_parse_file_with_no_issues(parser: ReviewParser):
    """Testa que arquivo sem issues não é incluído"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "clean.py",
                "critical_issues": [],
                "important_issues": [],
                "suggestions": [],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 0  # Arquivo sem issues não é incluído


def test_parse_multiple_files(parser: ReviewParser):
    """Testa parsing de múltiplos arquivos"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "file1.py",
                "critical_issues": [{"message": "Critical 1", "line": 5}],
                "important_issues": [],
                "suggestions": [],
            },
            {
                "filepath": "file2.py",
                "critical_issues": [],
                "important_issues": [{"message": "Important 1", "line": 10}],
                "suggestions": [],
            },
            {
                "filepath": "file3.py",
                "critical_issues": [],
                "important_issues": [],
                "suggestions": [{"message": "Suggestion 1", "line": 15}],
            },
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 3
    assert files[0].filepath == "file1.py"
    assert files[1].filepath == "file2.py"
    assert files[2].filepath == "file3.py"


def test_parse_issue_without_line_number(parser: ReviewParser):
    """Testa parsing de issue sem número de linha"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [{"message": "General issue"}],  # Sem line
                "important_issues": [],
                "suggestions": [],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 1
    assert files[0].critical_issues[0].line is None
    assert files[0].referenced_lines == []  # Sem linhas se não tiver line


def test_parse_mixed_issues_with_and_without_lines(parser: ReviewParser):
    """Testa parsing de issues mistas (com e sem linha)"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [
                    {"message": "Issue 1", "line": 10},
                    {"message": "Issue 2"},  # Sem line
                ],
                "important_issues": [{"message": "Issue 3", "line": 20}],
                "suggestions": [],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 1
    assert files[0].referenced_lines == [10, 20]  # Só as que têm linha


def test_parse_duplicate_line_numbers(parser: ReviewParser):
    """Testa que linhas duplicadas são removidas"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [
                    {"message": "Issue 1", "line": 10},
                    {"message": "Issue 2", "line": 10},  # Mesma linha
                ],
                "important_issues": [
                    {"message": "Issue 3", "line": 10}  # Mesma linha
                ],
                "suggestions": [],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 1
    assert files[0].referenced_lines == [10]  # Sem duplicatas


def test_parse_lines_are_sorted(parser: ReviewParser):
    """Testa que linhas são ordenadas"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [{"message": "Issue 1", "line": 30}],
                "important_issues": [{"message": "Issue 2", "line": 10}],
                "suggestions": [{"message": "Issue 3", "line": 20}],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    assert len(files) == 1
    assert files[0].referenced_lines == [10, 20, 30]  # Ordenado


def test_parse_invalid_json_raises_error(parser: ReviewParser):
    """Testa que JSON inválido lança exceção"""
    invalid_json = "{ invalid json }"

    with pytest.raises(json.JSONDecodeError):
        parser.parse(invalid_json)


def test_parse_missing_files_key_raises_error(parser: ReviewParser):
    """Testa que JSON sem chave 'files' causa erro"""
    review_json: dict[str, list[dict[str, object]]] = {"other_key": []}
    review_text = json.dumps(review_json)

    # Deve funcionar mas retornar lista vazia (files default = [])
    files = parser.parse(review_text)
    assert len(files) == 0


def test_parse_whitespace_handling(parser: ReviewParser):
    """Testa que whitespace extra é tratado corretamente"""
    review_json: dict[str, list[dict[str, object]]] = {"files": []}
    review_text = f"\n\n  {json.dumps(review_json)}  \n\n"

    files = parser.parse(review_text)

    assert len(files) == 0


def test_issue_objects_created_correctly(parser: ReviewParser):
    """Testa que objetos Issue são criados corretamente"""
    review_json: dict[str, list[dict[str, object]]] = {
        "files": [
            {
                "filepath": "test.py",
                "critical_issues": [{"message": "Critical msg", "line": 5}],
                "important_issues": [],
                "suggestions": [],
            }
        ]
    }
    review_text = json.dumps(review_json)

    files = parser.parse(review_text)

    issue = files[0].critical_issues[0]
    assert isinstance(issue, Issue)
    assert issue.text == "Critical msg"
    assert issue.line == 5
