"""
Port (Interface) para serviços de controle de versão (VCS)
Define o contrato que qualquer VCS adapter deve implementar
"""

from typing import Any, Protocol

from src.core.domain.pull_request import PullRequestInfo


class VCSPort(Protocol):
    """Interface para serviços de controle de versão (Azure DevOps, GitHub, GitLab)"""

    def get_pr_info(self, repo_id: str, pr_id: int) -> PullRequestInfo:
        """
        Busca informações de uma Pull Request

        Args:
            repo_id: Identificador do repositório
            pr_id: ID da Pull Request

        Returns:
            Informações da PR
        """
        ...

    def get_pr_files(self, repo_id: str, pr_id: int) -> list[Any]:
        """
        Busca lista de arquivos modificados na PR

        Args:
            repo_id: Identificador do repositório
            pr_id: ID da Pull Request

        Returns:
            Lista de arquivos modificados (estrutura específica do VCS)
        """
        ...

    def post_comment(
        self, repo_id: str, pr_id: int, file_path: str, start_line: int, end_line: int, comment: str
    ) -> bool:
        """
        Posta um comentário em um arquivo específico da PR

        Args:
            repo_id: Identificador do repositório
            pr_id: ID da Pull Request
            file_path: Caminho do arquivo
            start_line: Linha inicial do comentário
            end_line: Linha final do comentário
            comment: Texto do comentário (pode conter Markdown)

        Returns:
            True se postado com sucesso
        """
        ...

    def post_summary_comment(self, repo_id: str, pr_id: int, stats: dict[str, int]) -> bool:
        """
        Posta comentário resumo da PR

        Args:
            repo_id: Identificador do repositório
            pr_id: ID da Pull Request
            stats: Estatísticas do review (files_reviewed, critical, important, suggestions)

        Returns:
            True se postado com sucesso
        """
        ...
