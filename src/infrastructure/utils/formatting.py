"""
Utilities para formatação de comentários e output
"""

from src.core.domain.file_review import FileReview


def calculate_line_range(referenced_lines: list[int], context: int = 6) -> tuple[int, int]:
    """
    Calcula intervalo de linhas para postar comentário
    Usa mediana das linhas referenciadas como centro
    """
    if not referenced_lines:
        return (1, context)

    sorted_lines = sorted(referenced_lines)
    mid = sorted_lines[len(sorted_lines) // 2]

    start = max(1, mid - context)
    end = mid + context

    return (start, end)


def format_file_comment(file_review: FileReview) -> str:
    """
    Formata um FileReview em comentário markdown para Azure DevOps
    """
    lines = [f"**Arquivo: `{file_review.filepath}`**\n"]

    # Críticos
    if file_review.critical_issues:
        lines.append("🔴 Crítico:")
        for issue in file_review.critical_issues:
            lines.append(f"- {issue.text}")

    # Importantes
    if file_review.important_issues:
        lines.append("\n🟡 Importante:")
        for issue in file_review.important_issues:
            lines.append(f"- {issue.text}")

    # Sugestões
    if file_review.suggestions:
        lines.append("\n🟢 Sugestão:")
        for issue in file_review.suggestions:
            lines.append(f"- {issue.text}")

    return "\n".join(lines)
