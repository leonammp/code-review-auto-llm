"""
Testes para funções da CLI.
"""

from __future__ import annotations

import importlib

import pytest
import src.cli as cli


def test_preview_runs_in_preview_mode(monkeypatch: pytest.MonkeyPatch):
    """Testa que preview chama run_review com post_comments=False."""
    called = {}

    def fake_run(repo_id: str, pr_id: int, project: str, post_comments: bool) -> None:
        called["args"] = (repo_id, pr_id, project, post_comments)

    monkeypatch.setattr(cli, "run_review", fake_run)
    cli.preview(["--repo", "repo", "--pr", "7", "--project", "proj"])

    assert called["args"] == ("repo", 7, "proj", False)


def test_preview_uses_sys_argv_when_none(monkeypatch: pytest.MonkeyPatch):
    """Testa que preview usa sys.argv quando argv não é fornecido."""
    called = {}

    def fake_run(repo_id: str, pr_id: int, project: str, post_comments: bool) -> None:
        called["args"] = (repo_id, pr_id, project, post_comments)

    monkeypatch.setattr(cli, "run_review", fake_run)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["prog", "--repo", "repo", "--pr", "9", "--project", "proj"],
    )

    cli.preview()

    assert called["args"] == ("repo", 9, "proj", False)


def test_review_respects_no_post(monkeypatch: pytest.MonkeyPatch):
    """Testa que review respeita flag --no-post."""
    called = {}

    def fake_run(repo_id: str, pr_id: int, project: str, post_comments: bool) -> None:
        called["args"] = (repo_id, pr_id, project, post_comments)

    monkeypatch.setattr(cli, "run_review", fake_run)
    cli.review(["--repo", "repo", "--pr", "7", "--project", "proj", "--no-post"])

    assert called["args"] == ("repo", 7, "proj", False)


def test_review_defaults_to_posting(monkeypatch: pytest.MonkeyPatch):
    """Testa que review posta comentários por padrão."""
    called = {}

    def fake_run(repo_id: str, pr_id: int, project: str, post_comments: bool) -> None:
        called["args"] = (repo_id, pr_id, project, post_comments)

    monkeypatch.setattr(cli, "run_review", fake_run)
    cli.review(["--repo", "repo", "--pr", "7", "--project", "proj"])

    assert called["args"] == ("repo", 7, "proj", True)


def test_review_uses_sys_argv_when_none(monkeypatch: pytest.MonkeyPatch):
    """Testa que review usa sys.argv quando argv não é fornecido."""
    called = {}

    def fake_run(repo_id: str, pr_id: int, project: str, post_comments: bool) -> None:
        called["args"] = (repo_id, pr_id, project, post_comments)

    monkeypatch.setattr(cli, "run_review", fake_run)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "prog",
            "--repo",
            "repo",
            "--pr",
            "12",
            "--project",
            "proj",
            "--no-post",
        ],
    )

    cli.review()

    assert called["args"] == ("repo", 12, "proj", False)


def test_run_tests_passes_args_to_pytest(monkeypatch: pytest.MonkeyPatch):
    """Testa que run_tests delega argumentos ao pytest."""
    recorded = {}

    def fake_pytest(args: list[str]) -> int:
        recorded["args"] = args
        return 0

    monkeypatch.setattr("pytest.main", fake_pytest)

    with pytest.raises(SystemExit) as excinfo:
        cli.run_tests(["tests/unit"])

    assert excinfo.value.code == 0
    assert recorded["args"] == ["tests/unit"]


def test_run_tests_defaults_to_sys_argv(monkeypatch: pytest.MonkeyPatch):
    """Testa que run_tests utiliza sys.argv quando nenhum argv é passado."""
    recorded = {}

    def fake_pytest(args: list[str]) -> int:
        recorded["args"] = args
        return 0

    monkeypatch.setattr("pytest.main", fake_pytest)
    monkeypatch.setattr(cli.sys, "argv", ["prog", "-k", "core"])

    with pytest.raises(SystemExit) as excinfo:
        cli.run_tests()

    assert excinfo.value.code == 0
    assert recorded["args"] == ["-k", "core"]


def test_run_tests_cov_uses_defaults(monkeypatch: pytest.MonkeyPatch):
    """Testa que run_tests_cov usa defaults quando não há argumentos."""
    recorded = {}

    def fake_pytest(args: list[str]) -> int:
        recorded["args"] = args
        return 0

    monkeypatch.setattr("pytest.main", fake_pytest)

    with pytest.raises(SystemExit) as excinfo:
        cli.run_tests_cov([])

    assert excinfo.value.code == 0
    assert recorded["args"] == [
        "--cov=src",
        "--cov-report=term-missing",
        "tests/",
    ]


def test_run_tests_cov_appends_custom_args(monkeypatch: pytest.MonkeyPatch):
    """Testa que run_tests_cov acrescenta argumentos extras ao default."""
    recorded = {}

    def fake_pytest(args: list[str]) -> int:
        recorded["args"] = args
        return 0

    monkeypatch.setattr("pytest.main", fake_pytest)

    with pytest.raises(SystemExit) as excinfo:
        cli.run_tests_cov(["-k", "slow"])

    assert excinfo.value.code == 0
    assert recorded["args"] == [
        "--cov=src",
        "--cov-report=term-missing",
        "tests/",
        "-k",
        "slow",
    ]


def test_cli_module_reload(monkeypatch: pytest.MonkeyPatch):
    """Testa que o módulo cli pode ser recarregado."""
    monkeypatch.setattr(cli.sys, "argv", ["prog"])
    reloaded = importlib.reload(cli)

    assert hasattr(reloaded, "preview")
    assert hasattr(reloaded, "review")
