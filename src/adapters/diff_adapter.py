"""
Adapter para processar e filtrar diffs
Implementa DiffPort
"""

import base64
import difflib

import requests

from src.core.ports.diff_port import FileChange
from src.infrastructure.config.settings import AzureDevOpsConfig, ReviewBehavior, ReviewLimits


class DiffAdapter:
    """Processa e filtra diffs"""

    def __init__(
        self, behavior: ReviewBehavior, limits: ReviewLimits, azure_config: AzureDevOpsConfig
    ):
        self.behavior = behavior
        self.limits = limits
        self.azure_config = azure_config
        self._setup_session()

    def _setup_session(self):
        """Configura session para buscar conteúdo de arquivos"""
        self.session = requests.Session()
        token = self.azure_config.get_token()
        auth = base64.b64encode(f":{token}".encode()).decode()
        self.session.headers.update(
            {
                "Authorization": f"Basic {auth}",
            }
        )

    def should_include_file(self, filepath: str) -> bool:
        """Decide se arquivo deve ser incluído no diff"""

        # Verifica extensões ignoradas
        if any(filepath.endswith(ext) for ext in self.behavior.ignored_extensions):
            return False

        # Verifica paths ignorados
        if any(ignored in filepath for ignored in self.behavior.ignored_paths):
            return False

        return True

    def truncate_diff(self, diff_lines: list[str], max_lines: int) -> list[str]:
        """Trunca diff mantendo contexto"""
        if len(diff_lines) <= max_lines:
            return diff_lines

        return diff_lines[:max_lines]

    def generate_diff(
        self, repo_id: str, files: list[FileChange], source_branch: str, target_branch: str
    ) -> tuple[str, int, int]:
        """
        Gera diff completo formatado para LLM
        Retorna (diff_text, total_additions, total_deletions)
        """
        base_url = (
            f"https://dev.azure.com/{self.azure_config.org}/{self.azure_config.project}/_apis"
        )
        diff_text = ""
        total_additions = 0
        total_deletions = 0
        files_included = 0

        for file in files[: self.limits.max_files_to_analyze]:
            path = file.get("item", {}).get("path", "")
            change_type = file.get("changeType", "")

            # Filtra arquivos irrelevantes
            if not self.should_include_file(path):
                continue
            diff_text += f"\n## Arquivo {files_included + 1}: `{path}`\n**Tipo:** {change_type}\n\n"

            try:
                item_url = f"{base_url}/git/repositories/{repo_id}/items"
                base_params: dict[str, str] = {
                    "path": path,
                    "versionDescriptor.version": target_branch,
                    "versionDescriptor.versionType": "branch",
                    "api-version": self.azure_config.api_version,
                }
                source_params: dict[str, str] = {
                    "path": path,
                    "versionDescriptor.version": source_branch,
                    "versionDescriptor.versionType": "branch",
                    "api-version": self.azure_config.api_version,
                }

                base_content = self.session.get(item_url, params=base_params, timeout=30).text
                source_content = self.session.get(item_url, params=source_params, timeout=30).text

                diff_lines = list(
                    difflib.unified_diff(
                        base_content.splitlines(keepends=True),
                        source_content.splitlines(keepends=True),
                        fromfile=f"a/{path}",
                        tofile=f"b/{path}",
                        lineterm="",
                    )
                )

                if diff_lines:
                    # Conta adições e remoções
                    for line in diff_lines:
                        if line.startswith("+") and not line.startswith("+++"):
                            total_additions += 1
                        elif line.startswith("-") and not line.startswith("---"):
                            total_deletions += 1

                    # Trunca se necessário
                    truncated = self.truncate_diff(diff_lines, self.limits.max_diff_lines_per_file)

                    diff_text += "```diff\n"
                    diff_text += "".join(truncated)

                    if len(diff_lines) > self.limits.max_diff_lines_per_file:
                        omitted = len(diff_lines) - self.limits.max_diff_lines_per_file
                        diff_text += f"\n... ({omitted} linhas omitidas)\n"

                    diff_text += "\n```\n\n"
                    files_included += 1

            except Exception as e:
                diff_text += f"⚠️ Erro lendo arquivo: {e}\n\n"

        return diff_text, total_additions, total_deletions
