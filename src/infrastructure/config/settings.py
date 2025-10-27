"""
Configurações centralizadas usando Pydantic Settings
"""

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureDevOpsConfig(BaseSettings):
    """Configurações do Azure DevOps"""

    model_config = SettingsConfigDict(env_prefix="AZDO_", case_sensitive=False)

    org: str = Field(default="finnetbrasil")
    project: str = Field(default="")
    pat: str = Field(default="")
    api_version: str = Field(default="7.0")

    def get_token(self) -> str:
        """Prioriza SYSTEM_ACCESSTOKEN (pipeline), fallback para PAT"""
        return os.getenv("SYSTEM_ACCESSTOKEN") or self.pat


class LLMConfig(BaseSettings):
    """Configurações do LLM"""

    model_config = SettingsConfigDict(env_prefix="LITELLM_", case_sensitive=False)

    api_base: str
    api_key: str
    model: str = Field(default="gpt-4.1-nano")
    model_cost_per_1k: float = Field(default=0.002)
    max_tokens: int = Field(default=2500)
    temperature: float = Field(default=0.2)


class ReviewLimits(BaseSettings):
    """Limites para controle de custos e qualidade"""

    model_config = SettingsConfigDict(env_prefix="REVIEW_", case_sensitive=False)

    max_files_to_analyze: int = Field(default=30)
    max_tokens_per_pr: int = Field(default=50000)
    max_cost_per_pr_usd: float = Field(default=0.50)
    min_pr_size_lines: int = Field(default=10)
    max_pr_size_lines: int = Field(default=2000)
    max_diff_lines_per_file: int = Field(default=400)
    max_comment_length: int = Field(default=150000)


class ReviewBehavior(BaseSettings):
    """Comportamento do review"""

    model_config = SettingsConfigDict(env_prefix="REVIEW_", case_sensitive=False)

    skip_drafts: bool = Field(default=True)
    skip_label: str = Field(default="skip-review")
    context_lines: int = Field(default=6)
    post_summary_comment: bool = Field(default=True)

    ignored_extensions: list[str] = Field(
        default=[
            ".lock",
            ".min.js",
            ".min.css",
            ".svg",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".pdf",
            "package-lock.json",
            "yarn.lock",
            "poetry.lock",
        ]
    )

    ignored_paths: list[str] = Field(
        default=[
            "node_modules/",
            "dist/",
            "build/",
            ".next/",
            "vendor/",
            "__pycache__/",
            ".pytest_cache/",
        ]
    )


class Config(BaseSettings):
    """Configuração principal - agrega todas as configs"""

    azure: AzureDevOpsConfig = Field(default_factory=AzureDevOpsConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig) # pyright: ignore[reportUnknownVariableType, reportArgumentType]
    limits: ReviewLimits = Field(default_factory=ReviewLimits)
    behavior: ReviewBehavior = Field(default_factory=ReviewBehavior)


def load_config() -> Config:
    """Carrega configurações de variáveis de ambiente"""
    return Config()
