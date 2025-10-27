"""
Bootstrap - centraliza criação de dependências
Usa Ports (interfaces) para desacoplar core de implementações
"""

from dataclasses import dataclass

# Adapters (implementações) - injetados via DI
from src.adapters import AzureDevOpsAdapter, DiffAdapter, LiteLLMAdapter
from src.application.parsers.review_parser import ReviewParser
from src.application.validators.cost_validator import CostValidator
from src.application.validators.pr_validator import PRValidator

# Ports (interfaces) - o que o core precisa
from src.core.ports import DiffPort, LLMPort, VCSPort
from src.infrastructure.config.settings import Config, load_config

# Application layer
from src.infrastructure.rules_service import RulesService


@dataclass
class AppContainer:
    """
    Container com todas as dependências da aplicação.
    """

    config: Config
    azure: VCSPort  # Interface para VCS (Azure DevOps, GitHub, GitLab...)
    llm: LLMPort  # Interface para LLM (LiteLLM, OpenAI, Anthropic...)
    diff_service: DiffPort  # Interface para geração de diffs
    rules_service: RulesService
    parser: ReviewParser
    pr_validator: PRValidator
    cost_validator: CostValidator


def create_app(project: str | None = None) -> AppContainer:
    """
    Cria e configura todas as dependências da aplicação.
    Injeta implementações concretas (Adapters) nas interfaces (Ports).

    Args:
        project: Nome do projeto no Azure DevOps (opcional, usa env se não fornecido)
    """
    config = load_config()

    # Sobrescreve project se fornecido via CLI
    if project:
        config.azure.project = project

    return AppContainer(
        config=config,
        azure=AzureDevOpsAdapter(config.azure),  # Implementação Azure DevOps
        llm=LiteLLMAdapter(config.llm),  # Implementação LiteLLM
        diff_service=DiffAdapter(config.behavior, config.limits, config.azure),
        rules_service=RulesService(rules_base_path="review_rules"),
        parser=ReviewParser(),
        pr_validator=PRValidator(config.behavior, config.limits),
        cost_validator=CostValidator(config.limits, model_cost_per_1k=config.llm.model_cost_per_1k),
    )
