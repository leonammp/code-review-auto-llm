#!/usr/bin/env python3
"""
Code Review Bot
"""

import sys

from dotenv import load_dotenv

from src.bootstrap import AppContainer, create_app
from src.core.domain.review_result import ReviewResult
from src.infrastructure.utils.formatting import calculate_line_range, format_file_comment
from src.infrastructure.utils.output import print_summary

load_dotenv()


def main(repo_id: str, pr_id: int, project: str, post_comments: bool = True) -> None:
    """Fluxo principal de code review"""

    print("=" * 60)
    print("🔍 CODE REVIEW AUTOMÁTICO")
    print("=" * 60)
    print(f"Project: {project} | Repo: {repo_id} | PR: #{pr_id}")
    print(f"Postar comentários: {'✅ SIM' if post_comments else '❌ NÃO'}\n")

    # Bootstrap - cria todas as dependências via DI
    app = create_app(project=project)

    # 1. Buscar informações da PR
    pr_info = app.azure.get_pr_info(repo_id, pr_id)

    # 2. Buscar arquivos modificados da PR
    print("→ Buscando mudanças da PR...")
    files = app.azure.get_pr_files(repo_id, pr_id)

    if not files:
        print("✗ Nenhum arquivo modificado encontrado")
        return

    print(f"  • {len(files)} arquivos modificados")

    # 3. Gerar diff completo para calcular linhas
    print("→ Gerando diff...")
    diff_text, additions, deletions = app.diff_service.generate_diff(
        repo_id, files, pr_info.source_branch, pr_info.target_branch
    )

    # Atualiza estatísticas da PR
    pr_info.additions = additions
    pr_info.deletions = deletions
    pr_info.changed_files_count = len(files)

    print(f"  • +{additions} -{deletions} linhas")

    # 4. Valida se deve fazer review
    should_review, reason = app.pr_validator.should_review(pr_info)
    if not should_review:
        print(f"\n⏭ Pulando review: {reason}")
        return

    print(f"  • {reason}")

    # 5. Carregar regras customizadas (se existirem)
    custom_rules = app.rules_service.load_rules(project, repo_id)
    if custom_rules:
        print(f"\n📋 Regras customizadas: {project}/{repo_id}")

    # 6. Validar custo
    can_proceed, msg, tokens, cost = app.cost_validator.validate_cost(diff_text)
    print(f"\n💰 Custo estimado: {tokens:,} tokens (~${cost:.4f})")

    if not can_proceed:
        print(f"✗ {msg}")
        return

    # 7. Gerar review via LLM
    print("\n🤖 Gerando review...")
    review_text = app.llm.generate_review(diff_text, pr_info, custom_rules)

    # 8. Parse do review
    print("→ Processando resposta...")
    file_reviews = app.parser.parse(review_text)
    print(f"  • {len(file_reviews)} arquivo(s) com comentários")

    result = ReviewResult(
        pr_info=pr_info,
        files=file_reviews,
        total_tokens_used=tokens,
        estimated_cost_usd=cost,
        review_text=review_text,
    )

    # 9. Postar comentários
    if post_comments:
        post_review_comments(app, repo_id, pr_id, result)

    # 10. Mostrar resumo (com detalhes se for --no-post)
    print_summary(result, show_details=not post_comments)


def post_review_comments(
    app: AppContainer, repo_id: str, pr_id: int, result: ReviewResult
) -> None:
    """Posta comentários na PR"""

    print("\n→ Postando comentários no Azure DevOps...")

    # Posta resumo inicial
    if app.config.behavior.post_summary_comment and result.files:
        try:
            app.azure.post_summary_comment(repo_id, pr_id, result.stats)
            print("  • Resumo postado")
        except Exception as e:
            print(f"  ✗ Erro ao postar resumo: {e}")

    # Posta comentários por arquivo
    success = 0
    for file_review in result.files:
        try:
            # Calcula intervalo de linhas
            start, end = calculate_line_range(
                file_review.referenced_lines, app.config.behavior.context_lines
            )

            # Formata comentário
            comment = format_file_comment(file_review)

            # Posta
            if app.azure.post_comment(repo_id, pr_id, file_review.filepath, start, end, comment):
                success += 1
                print(f"  • {file_review.filepath}")

        except Exception as e:
            print(f"  ✗ Erro: {file_review.filepath}: {e}")

    print(f"\n✓ {success}/{len(result.files)} comentários postados")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python main.py <repo_id> <pr_id> <project> [--no-post]")
        print("\nExemplo:")
        print("  python main.py boletoonline-php8 4967 meu-projeto")
        print("  python main.py boletoonline-php8 4967 meu-projeto --no-post")
        sys.exit(1)

    main(
        repo_id=sys.argv[1],
        pr_id=int(sys.argv[2]),
        project=sys.argv[3],
        post_comments="--no-post" not in sys.argv,
    )
