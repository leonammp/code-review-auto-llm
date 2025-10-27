"""
Parser da resposta da LLM
"""

import json

from src.core.domain.file_review import FileReview, Issue


class ReviewParser:
    """Parse da resposta JSON estruturada da LLM"""

    def parse(self, review_text: str) -> list[FileReview]:
        """
        Converte resposta JSON da LLM em lista de FileReview
        """
        return self._parse_json(review_text)

    def _parse_json(self, review_text: str) -> list[FileReview]:
        """Parse de resposta JSON estruturada"""
        # Remove possíveis markdown code blocks
        cleaned = review_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        files: list[FileReview] = []

        for file_data in data.get("files", []):
            filepath = file_data["filepath"]

            # Converte issues do JSON para objetos Issue
            critical: list[Issue] = [
                Issue(text=issue["message"], line=issue.get("line"))
                for issue in file_data.get("critical_issues", [])
            ]

            important: list[Issue] = [
                Issue(text=issue["message"], line=issue.get("line"))
                for issue in file_data.get("important_issues", [])
            ]

            suggestions: list[Issue] = [
                Issue(text=issue["message"], line=issue.get("line"))
                for issue in file_data.get("suggestions", [])
            ]

            # Extrai linhas referenciadas
            all_lines: set[int] = set()
            for issue in critical + important + suggestions:
                if issue.line:
                    all_lines.add(issue.line)

            file_review = FileReview(
                filepath=filepath,
                critical_issues=critical,
                important_issues=important,
                suggestions=suggestions,
                referenced_lines=sorted(all_lines),
            )

            if file_review.total_issues > 0:
                files.append(file_review)

        return files
