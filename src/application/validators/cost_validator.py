"""
Validador de custos - estima e valida custos antes de executar
"""

from src.infrastructure.config.settings import ReviewLimits


class CostValidator:
    """Valida custos antes de executar review"""

    TOKEN_TO_CHAR_RATIO = 4  # ~4 chars = 1 token

    def __init__(self, limits: ReviewLimits, model_cost_per_1k: float = 0.002):
        self.limits = limits
        self.cost_per_token = model_cost_per_1k / 1000

    def estimate_cost(self, text: str) -> tuple[int, float]:
        """Retorna (tokens_estimados, custo_usd)"""
        tokens = len(text) // self.TOKEN_TO_CHAR_RATIO
        cost = tokens * self.cost_per_token
        return tokens, cost

    def validate_cost(self, diff_text: str) -> tuple[bool, str, int, float]:
        """
        Retorna (pode_executar, mensagem, tokens, custo)
        """
        tokens, cost = self.estimate_cost(diff_text)

        if tokens > self.limits.max_tokens_per_pr:
            return (
                False,
                f"Excede limite de tokens ({tokens:,} > {self.limits.max_tokens_per_pr:,})",
                tokens,
                cost,
            )

        if cost > self.limits.max_cost_per_pr_usd:
            return (
                False,
                f"Excede limite de custo (${cost:.4f} > ${self.limits.max_cost_per_pr_usd})",
                tokens,
                cost,
            )

        return True, f"{tokens:,} tokens (~${cost:.4f})", tokens, cost
