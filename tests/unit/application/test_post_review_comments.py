from types import SimpleNamespace

import pytest
from src.core.domain.file_review import FileReview, Issue
from src.core.domain.pull_request import PullRequestInfo
from src.core.domain.review_result import ReviewResult
from src.main import post_review_comments


class FakeAzure:
    def __init__(self) -> None:
        self.summary_calls: list[tuple[str, int, dict[str, int]]] = []
        self.comment_calls: list[dict[str, object]] = []

    def post_summary_comment(self, repo_id: str, pr_id: int, stats: dict[str, int]) -> bool:
        self.summary_calls.append((repo_id, pr_id, stats))
        return True

    def post_comment(
        self,
        repo_id: str,
        pr_id: int,
        file_path: str,
        start_line: int,
        end_line: int,
        comment: str,
    ) -> bool:
        self.comment_calls.append(
            {
                "repo_id": repo_id,
                "pr_id": pr_id,
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "comment": comment,
            }
        )
        return True


def make_result() -> ReviewResult:
    pr_info = PullRequestInfo(
        id=123,
        title="Add authentication checks",
        source_branch="feature/auth",
        target_branch="main",
        is_draft=False,
        additions=10,
        deletions=2,
        changed_files_count=1,
        labels=[],
    )
    file_review = FileReview(
        filepath="src/auth.py",
        critical_issues=[
            Issue(text="Na linha 42 `validate_user`: falha em validar token", line=42)
        ],
        important_issues=[Issue(text="Na linha 48 `log_event`: falta tratar exceção", line=48)],
        suggestions=[Issue(text="Na linha 50: considere extrair helper", line=50)],
        referenced_lines=[42, 48, 50],
    )
    return ReviewResult(
        pr_info=pr_info,
        files=[file_review],
        total_tokens_used=1200,
        estimated_cost_usd=0.03,
        review_text="{}",
    )


def make_app(post_summary: bool = True, context_lines: int = 6) -> SimpleNamespace:
    return SimpleNamespace(
        config=SimpleNamespace(
            behavior=SimpleNamespace(
                post_summary_comment=post_summary,
                context_lines=context_lines,
            )
        ),
        azure=FakeAzure(),
    )


def test_post_review_comments_posts_summary_and_comments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = make_app()
    result = make_result()

    post_review_comments(app, "repo", 7, result) # type: ignore

    captured = capsys.readouterr()
    assert "Resumo postado" in captured.out

    assert len(app.azure.summary_calls) == 1
    summary_repo, summary_pr, stats = app.azure.summary_calls[0]
    assert summary_repo == "repo"
    assert summary_pr == 7
    assert stats == result.stats

    assert len(app.azure.comment_calls) == 1
    comment_call = app.azure.comment_calls[0]
    assert comment_call["file_path"] == "src/auth.py"
    assert comment_call["start_line"] == 42  # Mediana 48 - 6 (context default)
    assert comment_call["end_line"] == 54  # Mediana 48 + 6
    assert "**Arquivo: `src/auth.py`**" in comment_call["comment"]


def test_post_review_comments_respects_post_summary_flag(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = make_app(post_summary=False)
    result = make_result()

    post_review_comments(app, "repo", 7, result) # type: ignore

    captured = capsys.readouterr()
    assert "Resumo postado" not in captured.out
    assert app.azure.summary_calls == []
    assert len(app.azure.comment_calls) == 1
