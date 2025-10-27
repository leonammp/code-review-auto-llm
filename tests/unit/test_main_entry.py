"""
Testes para o entry point `python -m src`.
"""

from __future__ import annotations

import runpy

import pytest


def test_module_main_invokes_review(monkeypatch: pytest.MonkeyPatch):
    """Testa que executar `python -m src` chama cli.review."""
    called: dict[str, object | None] = {"args": None}

    def fake_review() -> None:
        called["args"] = ()

    monkeypatch.setattr("src.cli.review", fake_review)

    runpy.run_module("src", run_name="__main__")

    assert called["args"] == ()
