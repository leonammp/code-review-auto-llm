"""
Port (Interface) para serviços de Large Language Model (LLM)
Define o contrato que qualquer LLM adapter deve implementar
"""

from typing import Protocol

from src.core.domain.pull_request import PullRequestInfo


class LLMPort(Protocol):
    """Interface para serviços de LLM (OpenAI, Anthropic, LiteLLM, etc)"""

    def generate_review(
        self, diff_text: str, pr_info: PullRequestInfo, custom_rules: str | None = None
    ) -> str:
        """
        Gera review de código usando LLM

        Args:
            diff_text: Diff unificado da PR
            pr_info: Informações da Pull Request
            custom_rules: Regras customizadas do projeto/repositório (opcional)

        Returns:
            Review em formato JSON estruturado
        """
        ...
