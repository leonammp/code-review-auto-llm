"""
Service para carregar regras customizadas de code review
"""

from pathlib import Path


class RulesService:
    """Gerencia carregamento de regras customizadas por projeto/repositório"""

    def __init__(self, rules_base_path: str = "review_rules"):
        """
        Args:
            rules_base_path: Caminho base para o diretório de regras
        """
        self.base_path = Path(rules_base_path)

    def load_rules(self, project: str, repository: str) -> str | None:
        """
        Carrega regras específicas para um projeto/repositório

        Args:
            project: Nome do projeto (ex: "Portal de Boletos")
            repository: Nome do repositório (ex: "boletoonline-php8")

        Returns:
            Conteúdo do arquivo de regras ou None se não existir
        """
        # Normaliza nomes (remove espaços extras, case-insensitive no FS)
        project_clean = project.strip()
        repo_clean = repository.strip()

        # Monta caminho: review_rules/[projeto]/[repositorio].md
        rules_file = self.base_path / project_clean / f"{repo_clean}.md"

        if not rules_file.exists():
            return None

        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                return None

            return content

        except Exception as e:
            # Em caso de erro, retorna None (não quebra o fluxo)
            print(f"⚠️  Erro ao carregar regras de {rules_file}: {e}")
            return None

    def has_rules(self, project: str, repository: str) -> bool:
        """
        Verifica se existem regras para um projeto/repositório

        Args:
            project: Nome do projeto
            repository: Nome do repositório

        Returns:
            True se existem regras, False caso contrário
        """
        return self.load_rules(project, repository) is not None
