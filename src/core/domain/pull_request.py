"""
Model para informações da Pull Request
"""

from pydantic import BaseModel, Field


class PullRequestInfo(BaseModel):
    """Informações da PR necessárias para o review"""

    id: int
    title: str
    source_branch: str
    target_branch: str
    is_draft: bool
    additions: int
    deletions: int
    changed_files_count: int
    labels: list[str] = Field(default_factory=list)

    @property
    def total_changes(self) -> int:
        """Total de linhas modificadas"""
        return self.additions + self.deletions

    @property
    def should_skip(self) -> bool:
        """Verificação rápida se deve pular (lógica completa no validator)"""
        return self.is_draft or "skip-review" in self.labels
