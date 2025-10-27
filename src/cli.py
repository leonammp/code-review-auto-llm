"""CLI para o Code Review Bot."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.main import main as run_review


def _base_parser(prog: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Executa os fluxos do Code Review Bot.",
    )
    parser.add_argument(
        "--repo", dest="repo_id", required=True, help="ID do repositório no Azure DevOps"
    )
    parser.add_argument(
        "--pr", dest="pr_id", type=int, required=True, help="Número do Pull Request"
    )
    parser.add_argument(
        "--project", dest="project", required=True, help="Nome do projeto no Azure DevOps"
    )
    return parser


def preview(argv: Sequence[str] | None = None) -> None:
    """Executa o review em modo preview (sem postar comentários)."""
    args = _base_parser("preview").parse_args(sys.argv[1:] if argv is None else argv)
    run_review(args.repo_id, args.pr_id, args.project, post_comments=False)


def review(argv: Sequence[str] | None = None) -> None:
    """Executa o review completo e posta comentários no Azure DevOps."""
    parser = _base_parser("review")
    parser.add_argument(
        "--no-post",
        dest="no_post",
        action="store_true",
        help="Executa o fluxo completo sem postar comentários de volta no Azure DevOps.",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    run_review(args.repo_id, args.pr_id, args.project, post_comments=not args.no_post)


def run_tests(argv: Sequence[str] | None = None) -> None:
    """Executa os testes com pytest."""
    import pytest

    args = sys.argv[1:] if argv is None else list(argv)
    raise SystemExit(pytest.main(args))


def run_tests_cov(argv: Sequence[str] | None = None) -> None:
    """Executa os testes com cobertura."""
    import pytest

    defaults = ["--cov=src", "--cov-report=term-missing", "tests/"]
    args = sys.argv[1:] if argv is None else list(argv)
    # Se não tiver argumentos, usa apenas os defaults
    if not args:
        raise SystemExit(pytest.main(defaults))
    # Se tiver argumentos, adiciona aos defaults
    raise SystemExit(pytest.main(defaults + args))
