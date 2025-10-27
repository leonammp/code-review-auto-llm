"""
Service de integração com Azure DevOps
"""

import base64
from typing import Any, TypedDict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.domain.pull_request import PullRequestInfo
from src.infrastructure.config.settings import AzureDevOpsConfig


class CommentDict(TypedDict):
    content: str
    commentType: int


class LineOffset(TypedDict):
    line: int
    offset: int


class ThreadContext(TypedDict, total=False):
    filePath: str
    rightFileStart: LineOffset
    rightFileEnd: LineOffset


class ThreadPayload(TypedDict, total=False):
    comments: list[CommentDict]
    status: int
    threadContext: ThreadContext


class AzureDevOpsAdapter:
    """Gerencia toda comunicação com Azure DevOps"""

    def __init__(self, config: AzureDevOpsConfig):
        self.config = config
        self.base_url = f"https://dev.azure.com/{config.org}/{config.project}/_apis"
        self._setup_session()

    def _setup_session(self):
        """Configura session com retry automático"""
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        token = self.config.get_token()
        auth = base64.b64encode(f":{token}".encode()).decode()
        self.session.headers.update(
            {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        )

    def get_pr_info(self, repo_id: str, pr_id: int) -> PullRequestInfo:
        """Busca informações da PR e retorna model"""
        url = f"{self.base_url}/git/repositories/{repo_id}/pullrequests/{pr_id}"
        params = {"api-version": self.config.api_version}

        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        pr_data = resp.json()

        # Busca labels se houver
        labels = []
        if "labels" in pr_data:
            labels = [label.get("name", "") for label in pr_data.get("labels", [])]

        return PullRequestInfo(
            id=pr_data["pullRequestId"],
            title=pr_data.get("title", ""),
            source_branch=pr_data["sourceRefName"].replace("refs/heads/", ""),
            target_branch=pr_data["targetRefName"].replace("refs/heads/", ""),
            is_draft=pr_data.get("isDraft", False),
            additions=0,  # Será calculado no diff
            deletions=0,  # Será calculado no diff
            changed_files_count=0,  # Será calculado no diff
            labels=labels,
        )

    def get_pr_files(self, repo_id: str, pr_id: int) -> list[dict[str, Any]]:
        """
        Busca lista de arquivos modificados na PR
        Retorna changeEntries da última iteração
        """
        params = {"api-version": self.config.api_version}

        # Busca iterações da PR
        iter_url = f"{self.base_url}/git/repositories/{repo_id}/pullrequests/{pr_id}/iterations"
        iterations_resp = self.session.get(iter_url, params=params, timeout=30)
        iterations_resp.raise_for_status()
        iterations = iterations_resp.json().get("value", [])

        if not iterations:
            return []

        # Busca mudanças da última iteração
        last_iteration = iterations[-1]["id"]
        changes_url = (
            f"{self.base_url}/git/repositories/{repo_id}/pullrequests/"
            f"{pr_id}/iterations/{last_iteration}/changes"
        )
        changes_resp = self.session.get(changes_url, params=params, timeout=30)
        changes_resp.raise_for_status()
        changes = changes_resp.json()

        return changes.get("changeEntries", [])

    def post_comment(
        self, repo_id: str, pr_id: int, file_path: str, start_line: int, end_line: int, comment: str
    ) -> bool:
        """Posta um comentário em um arquivo específico"""

        # Valida tamanho do comentário
        if len(comment) > 150000:
            comment = comment[:150000] + "\n\n[... truncado]"

        payload: ThreadPayload = {
            "comments": [{"content": comment, "commentType": 1}],
            "status": 1,
            "threadContext": {
                "filePath": file_path,
                "rightFileStart": {"line": start_line, "offset": 1},
                "rightFileEnd": {"line": end_line, "offset": 999},
            },
        }

        url = f"{self.base_url}/git/repositories/{repo_id}/pullRequests/{pr_id}/threads"
        params = {"api-version": self.config.api_version}

        resp = self.session.post(url, json=payload, params=params, timeout=30)
        resp.raise_for_status()

        print(f"   ✅ Comentário postado: {file_path}:{start_line}-{end_line}")
        return True

    def post_summary_comment(self, repo_id: str, pr_id: int, stats: dict[str, int]) -> bool:
        """Posta comentário resumo inicial"""

        comment = f"""🤖 **Code Review Automático**

📊 **Estatísticas:**
- Arquivos analisados: {stats['files_reviewed']}
- Comentários: {stats['critical']}🔴 {stats['important']}🟡 {stats['suggestions']}🟢

💡 Este é um review automatizado. Sempre valide as sugestões com seu julgamento técnico.
"""

        payload: ThreadPayload = {"comments": [{"content": comment, "commentType": 1}], "status": 1}

        url = f"{self.base_url}/git/repositories/{repo_id}/pullRequests/{pr_id}/threads"
        params = {"api-version": self.config.api_version}

        resp = self.session.post(url, json=payload, params=params, timeout=30)
        resp.raise_for_status()

        return True
