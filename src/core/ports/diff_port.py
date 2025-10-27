"""
Port (Interface) para serviços de geração de diff
Define o contrato que qualquer diff adapter deve implementar
"""

from typing import Protocol, TypedDict


class FileChange(TypedDict):
    """Representa uma mudança em um arquivo"""

    item: dict[str, str]
    changeType: str


class DiffPort(Protocol):
    """Interface para serviços de geração de diff"""

    def generate_diff(
        self, repo_id: str, files: list[FileChange], source_branch: str, target_branch: str
    ) -> tuple[str, int, int]:
        """
        Gera diff unificado para review

        Args:
            repo_id: Identificador do repositório
            files: Lista de arquivos modificados
            source_branch: Branch de origem
            target_branch: Branch de destino

        Returns:
            Tupla (diff_text, additions, deletions)
        """
        ...
