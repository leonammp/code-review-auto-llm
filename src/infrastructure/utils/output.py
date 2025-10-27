"""
Utilitários para output e resumo
"""

import re

from src.core.domain.review_result import ReviewResult


def print_summary(result: ReviewResult, show_details: bool = False) -> None:
    """
    Imprime resumo do review no console

    Args:
        result: Resultado do review
        show_details: Se True, mostra os comentários detalhados (modo --no-post)
    """
    print("\n" + "=" * 60)
    print("📊 RESUMO DO REVIEW")
    print("=" * 60)

    print(f"\n🔍 PR #{result.pr_info.id}: {result.pr_info.title}")
    print(f"   {result.pr_info.source_branch} → {result.pr_info.target_branch}")
    print(f"   Alterações: {result.pr_info.total_changes} linhas")

    stats = result.stats
    print(f"\n📝 Arquivos revisados: {stats['files_reviewed']}")
    print(f"   🔴 Críticos: {stats['critical']}")
    print(f"   🟡 Importantes: {stats['important']}")
    print(f"   🟢 Sugestões: {stats['suggestions']}")

    print(f"\n💰 Custo estimado: ${result.estimated_cost_usd:.4f}")
    print(f"   Tokens usados: {result.total_tokens_used:,}")

    # Se show_details=True, mostra os comentários que seriam postados
    if show_details and result.files:
        print("\n" + "=" * 60)
        print("📋 COMENTÁRIOS QUE SERIAM POSTADOS")
        print("=" * 60)

        for idx, file_review in enumerate(result.files, 1):
            print(f"\n[{idx}/{len(result.files)}] 📄 {file_review.filepath}")
            print("-" * 60)

            # Críticos
            if file_review.critical_issues:
                print("\n🔴 CRÍTICO:")
                for issue in file_review.critical_issues:
                    # Remove duplicação de [Linha X] do texto
                    text = issue.text
                    if issue.line:
                        text = re.sub(
                            r"\[Linha(?: aproximad[ae]| aproximada)?\s*[:+~-]?\s*\d+\]\s*",
                            "",
                            text,
                            count=1,
                        )
                    line_ref = f" [Linha {issue.line}]" if issue.line else ""
                    print(f"   •{line_ref} {text}")

            # Importantes
            if file_review.important_issues:
                print("\n🟡 IMPORTANTE:")
                for issue in file_review.important_issues:
                    # Remove duplicação de [Linha X] do texto
                    text = issue.text
                    if issue.line:
                        text = re.sub(
                            r"\[Linha(?: aproximad[ae]| aproximada)?\s*[:+~-]?\s*\d+\]\s*",
                            "",
                            text,
                            count=1,
                        )
                    line_ref = f" [Linha {issue.line}]" if issue.line else ""
                    print(f"   •{line_ref} {text}")

            # Sugestões
            if file_review.suggestions:
                print("\n🟢 SUGESTÃO:")
                for issue in file_review.suggestions:
                    # Remove duplicação de [Linha X] do texto
                    text = issue.text
                    if issue.line:
                        text = re.sub(
                            r"\[Linha(?: aproximad[ae]| aproximada)?\s*[:+~-]?\s*\d+\]\s*",
                            "",
                            text,
                            count=1,
                        )
                    line_ref = f" [Linha {issue.line}]" if issue.line else ""
                    print(f"   •{line_ref} {text}")

    print("\n" + "=" * 60)
