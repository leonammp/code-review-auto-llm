"""
Validador de Pull Request - decide se deve fazer review
"""

from src.core.domain.pull_request import PullRequestInfo
from src.infrastructure.config.settings import ReviewBehavior, ReviewLimits


class PRValidator:
    """Valida se uma PR deve ser revisada"""

    def __init__(self, behavior: ReviewBehavior, limits: ReviewLimits):
        self.behavior = behavior
        self.limits = limits

    def should_review(self, pr: PullRequestInfo) -> tuple[bool, str]:
        """
        Retorna (should_review, reason)
        Centraliza TODAS as regras de skip
        """

        # Regra 1: Draft
        if self.behavior.skip_drafts and pr.is_draft:
            return False, "PR em draft"

        # Regra 2: Label skip
        if self.behavior.skip_label in pr.labels:
            return False, f"Label '{self.behavior.skip_label}' presente"

        # Regra 3: Tamanho mínimo
        if pr.total_changes < self.limits.min_pr_size_lines:
            return False, f"PR muito pequena ({pr.total_changes} linhas)"

        # Regra 4: Tamanho máximo (WARNING, não skip)
        if pr.total_changes > self.limits.max_pr_size_lines:
            return True, f"⚠️ PR grande ({pr.total_changes} linhas), review pode ser superficial"

        return True, f"PR validada ({pr.total_changes} linhas)"
