"""
Testes que garantem importação dos módulos de domínio sob cobertura.
"""

from __future__ import annotations

import importlib


def test_reload_file_review_module():
    """Testa que módulo file_review pode ser recarregado."""
    import src.core.domain.file_review as module

    reloaded = importlib.reload(module)

    assert hasattr(reloaded, "FileReview")
    assert hasattr(reloaded, "Issue")


def test_reload_pull_request_module():
    """Testa que módulo pull_request pode ser recarregado."""
    import src.core.domain.pull_request as module

    reloaded = importlib.reload(module)

    assert hasattr(reloaded, "PullRequestInfo")


def test_reload_review_result_module():
    """Testa que módulo review_result pode ser recarregado."""
    import src.core.domain.review_result as module

    reloaded = importlib.reload(module)

    assert hasattr(reloaded, "ReviewResult")
