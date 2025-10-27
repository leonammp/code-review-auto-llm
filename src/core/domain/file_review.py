"""
Models para review de arquivos
"""

from pydantic import BaseModel, Field


class Issue(BaseModel):
    """Um issue individual no review"""

    text: str
    line: int | None = None


class FileReview(BaseModel):
    """Review de um arquivo específico"""

    filepath: str
    critical_issues: list[Issue] = Field(default_factory=list)
    important_issues: list[Issue] = Field(default_factory=list)
    suggestions: list[Issue] = Field(default_factory=list)
    referenced_lines: list[int] = Field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        """Verifica se tem issues críticos ou importantes"""
        return bool(self.critical_issues or self.important_issues)

    @property
    def total_issues(self) -> int:
        """Total de issues de todas as severidades"""
        return len(self.critical_issues) + len(self.important_issues) + len(self.suggestions)
