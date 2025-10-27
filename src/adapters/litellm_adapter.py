"""
Service de integração com LLM
"""

from pathlib import Path
from typing import Any, Optional, cast

from litellm import completion

from src.core.domain.pull_request import PullRequestInfo
from src.infrastructure.config.settings import LLMConfig


class LiteLLMAdapter:
    """Gerencia comunicação com LLM"""

    def __init__(self, config: LLMConfig):
        self.config = config
        # Prompts estão na raiz do projeto (fora de src/)
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self._load_templates()

    def _load_templates(self) -> None:
        """Carrega templates de prompt do disco"""
        system_path = self.prompts_dir / "system.txt"
        user_path = self.prompts_dir / "user_review.txt"

        with open(system_path, "r", encoding="utf-8") as f:
            self.system_template = f.read()

        with open(user_path, "r", encoding="utf-8") as f:
            self.user_template = f.read()

    def generate_review(
        self, diff_text: str, pr_info: PullRequestInfo, custom_rules: str | None = None
    ) -> str:
        """
        Gera review via LLM

        Args:
            diff_text: Diff da PR
            pr_info: Informações da PR
            custom_rules: Regras customizadas do projeto/repositório (opcional)
        """
        user_prompt = self._build_user_prompt(pr_info, diff_text, custom_rules)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_template},
            {"role": "user", "content": user_prompt},
        ]

        response: Any = completion(
            model=self.config.model,
            messages=messages,
            api_base=self.config.api_base,
            api_key=self.config.api_key,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        content = cast(Optional[str], response.choices[0].message.content)
        return content or ""

    def _build_user_prompt(
        self, pr_info: PullRequestInfo, diff_text: str, custom_rules: str | None = None
    ) -> str:
        """
        Constrói prompt do usuário usando template e delimitadores seguros

        Delimitadores XML-style protegem contra prompt injection:
        - Mesmo que o diff contenha instruções maliciosas, elas ficam isoladas dentro de <DIFF>
        - A LLM é instruída a tratar tudo dentro dos delimitadores como dados, não instruções
        """
        # Sanitiza custom_rules se não fornecido
        rules_content = (
            custom_rules if custom_rules else "Nenhuma regra customizada para este repositório."
        )

        # Usa template com substituição de variáveis
        prompt = self.user_template.format(
            pr_title=pr_info.title,
            source_branch=pr_info.source_branch,
            target_branch=pr_info.target_branch,
            changed_files=pr_info.changed_files_count,
            custom_rules=rules_content,
            diff_content=diff_text,
        )

        return prompt
