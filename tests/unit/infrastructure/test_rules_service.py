"""
Testes para RulesService
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from src.infrastructure.rules_service import RulesService


@pytest.fixture
def temp_rules_dir():
    """Cria diretório temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_rules_service_creation(temp_rules_dir: str):
    """Testa criação do RulesService"""
    service = RulesService(rules_base_path=temp_rules_dir)

    assert service.base_path == Path(temp_rules_dir)


def test_load_rules_nonexistent(temp_rules_dir: str):
    """Testa carregamento de regras inexistentes"""
    service = RulesService(rules_base_path=temp_rules_dir)

    rules = service.load_rules("NonExistent Project", "nonexistent-repo")

    assert rules is None


def test_load_rules_existing(temp_rules_dir: str):
    """Testa carregamento de regras existentes"""
    # Cria estrutura de diretórios e arquivo
    project_dir = Path(temp_rules_dir) / "Test Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "test-repo.md"
    rules_content = "# Custom Rules\n\n- Rule 1\n- Rule 2"
    rules_file.write_text(rules_content, encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)
    rules = service.load_rules("Test Project", "test-repo")

    assert rules is not None
    assert "# Custom Rules" in rules
    assert "- Rule 1" in rules
    assert "- Rule 2" in rules


def test_load_rules_empty_file(temp_rules_dir: str):
    """Testa carregamento de arquivo de regras vazio"""
    project_dir = Path(temp_rules_dir) / "Empty Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "empty-repo.md"
    rules_file.write_text("", encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)
    rules = service.load_rules("Empty Project", "empty-repo")

    assert rules is None


def test_load_rules_whitespace_only(temp_rules_dir: str):
    """Testa carregamento de arquivo com apenas espaços em branco"""
    project_dir = Path(temp_rules_dir) / "Whitespace Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "whitespace-repo.md"
    rules_file.write_text("   \n\n  \t  \n", encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)
    rules = service.load_rules("Whitespace Project", "whitespace-repo")

    assert rules is None


def test_has_rules_true(temp_rules_dir: str):
    """Testa verificação de existência de regras (existente)"""
    project_dir = Path(temp_rules_dir) / "Valid Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "valid-repo.md"
    rules_file.write_text("Valid rules content", encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)

    assert service.has_rules("Valid Project", "valid-repo") is True


def test_has_rules_false(temp_rules_dir: str):
    """Testa verificação de existência de regras (inexistente)"""
    service = RulesService(rules_base_path=temp_rules_dir)

    assert service.has_rules("Invalid Project", "invalid-repo") is False


def test_load_rules_with_special_characters(temp_rules_dir: str):
    """Testa carregamento de regras com caracteres especiais"""
    project_dir = Path(temp_rules_dir) / "Special Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "special-repo.md"
    rules_content = "# Regras com acentuação\n\nÁÉÍÓÚ àèìòù ñ ç"
    rules_file.write_text(rules_content, encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)
    rules = service.load_rules("Special Project", "special-repo")

    assert rules is not None
    assert "acentuação" in rules
    assert "ÁÉÍÓÚ" in rules


def test_load_rules_strips_project_and_repo(temp_rules_dir: str):
    """Testa que load_rules remove espaços extras dos nomes"""
    project_dir = Path(temp_rules_dir) / "Trim Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "trim-repo.md"
    rules_file.write_text("Content", encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)
    rules = service.load_rules("  Trim Project  ", "  trim-repo  ")

    assert rules is not None
    assert "Content" in rules


def test_load_rules_handles_read_error(temp_rules_dir: str):
    """Testa que erros de leitura retornam None sem quebrar"""
    service = RulesService(rules_base_path=temp_rules_dir)

    # Tenta carregar de um caminho que causaria erro
    rules = service.load_rules("../../../", "invalid")

    assert rules is None


def test_load_rules_multiline_content(temp_rules_dir: str):
    """Testa carregamento de regras com múltiplas linhas"""
    project_dir = Path(temp_rules_dir) / "Multiline Project"
    project_dir.mkdir(parents=True)

    rules_file = project_dir / "multi-repo.md"
    rules_content = """# Title

## Section 1
Content line 1
Content line 2

## Section 2
More content
"""
    rules_file.write_text(rules_content, encoding="utf-8")

    service = RulesService(rules_base_path=temp_rules_dir)
    rules = service.load_rules("Multiline Project", "multi-repo")

    assert rules is not None
    assert "# Title" in rules
    assert "## Section 1" in rules
    assert "## Section 2" in rules
