"""
Model para resultado completo do review
"""

from pydantic import BaseModel, Field

from src.core.domain.file_review import FileReview
from src.core.domain.pull_request import PullRequestInfo


class ReviewResult(BaseModel):
    """Resultado completo do review"""

    pr_info: PullRequestInfo
    files: list[FileReview] = Field(default_factory=list)
    total_tokens_used: int
    estimated_cost_usd: float
    review_text: str  # Raw text da LLM

    @property
    def stats(self) -> dict[str, int]:
        """Estatísticas do review para exibição"""
        return {
            "files_reviewed": len(self.files),
            "critical": sum(len(f.critical_issues) for f in self.files),
            "important": sum(len(f.important_issues) for f in self.files),
            "suggestions": sum(len(f.suggestions) for f in self.files),
        }
