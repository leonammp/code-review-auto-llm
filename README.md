# 🤖 Code Review Bot

Bot automatizado de code review para Pull Requests no Azure DevOps usando LLM.

## 📋 Características

- Review automático em PRs
- Foco em issues críticos e importantes
- Regras customizadas por projeto/repositório
- Controle de custos com limites configuráveis

## 🏗️ Arquitetura

Segue **Domain-Driven Design (DDD)** com arquitetura hexagonal:

```
code-review-bot/
├── src/                           # Código-fonte
│   ├── main.py                    # Entry point
│   ├── bootstrap.py               # DI container
│   │
│   ├── core/                      # 🔵 DOMÍNIO
│   │   └── domain/                # Entidades de negócio
│   │       ├── pull_request.py    # PullRequestInfo
│   │       ├── file_review.py     # Issue, FileReview
│   │       └── review_result.py   # ReviewResult
│   │
│   ├── adapters/                  # 🔌 ADAPTADORES
│   │   ├── azure_devops.py        # Azure DevOps API
│   │   ├── llm_service.py         # LLM (LiteLLM)
│   │   └── diff_service.py        # Geração de diffs
│   │
│   ├── application/               # 📋 APLICAÇÃO
│   │   ├── validators/            # Validações
│   │   │   ├── pr_validator.py
│   │   │   └── cost_validator.py
│   │   └── parsers/               # Conversão de dados
│   │       └── review_parser.py   # Parse JSON da LLM
│   │
│   └── infrastructure/            # 🛠️ INFRAESTRUTURA
│       ├── config/
│       │   └── settings.py        # Configurações
│       ├── rules_service.py       # Carregamento de regras
│       └── utils/
│           ├── formatting.py
│           └── output.py
│
├── prompts/                       # Templates de prompt
│   ├── system.txt
│   └── user_review.txt
│
└── review_rules/                  # Regras por projeto/repo
    └── [Projeto]/
        └── [repositorio].md
```

### Princípios da Arquitetura

- **Core/Domain**: Sem dependências externas, lógica de negócio pura
- **Adapters**: Implementações de serviços externos (substituíveis)
- **Application**: Orquestração e casos de uso
- **Infrastructure**: Configuração e utilitários

## 🚀 Setup

### 1. Clonar o repositório

```bash
git clone <link_do_repo>
cd code-review-bot
```

### 2. Instalar dependências com Poetry

```bash
# Certifique-se que você tem Poetry instalado
# Se não tiver: curl -sSL https://install.python-poetry.org | python3 -

# Configure o Poetry para usar Python 3.12
poetry env use 3.12

# Instale as dependências
poetry install
```

### 3. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e ajuste:

```bash
cp .env.example .env
```

```env
# Azure DevOps
AZDO_ORG=sua_org_devops
AZDO_PAT=seu-pat  # Apenas local

# LLM
LITELLM_API_BASE=https://your-litellm-instance
LITELLM_API_KEY=your-key
LITELLM_MODEL=gpt-4.1-nano

# Opcional
REVIEW_MAX_COST_USD=0.50
REVIEW_MAX_TOKENS=50000
```

### 4. Executar localmente

```bash
# Preview (sem postar comentários)
poetry run preview --repo voxkey --pr 4967 --project "VoxKey"

# Review completo (posta comentários)
poetry run review --repo voxkey --pr 4967 --project "VoxKey"

# Review sem postar (modo dry-run)
poetry run review --repo voxkey --pr 4967 --project "VoxKey" --no-post
```

### 5. Scripts Úteis

```bash
# Executar todos os testes
poetry run test

# Executar testes com cobertura
poetry run test-cov

# Análise estática e lint
poetry run ruff check

# Type checking
poetry run mypy src/
```

## 📋 Regras Customizadas

Você pode definir regras específicas de code review para cada projeto/repositório:

```bash
# Criar regras customizadas
mkdir -p "review_rules/VoxKey"
nano "review_rules/VoxKey/voxkey.md"
```

📖 **Documentação completa:** [`review_rules/README.md`](review_rules/README.md)

## 📊 Exemplo de Output

```
============================================================
🔍 CODE REVIEW AUTOMÁTICO
============================================================
Project: VoxKey | Repo: vox-key | PR: #4967
Postar comentários: ❌ NÃO

→ Buscando informações da PR...
→ Buscando mudanças da PR...
  • 3 arquivos modificados
→ Gerando diff...
  • +6 -8 linhas
  • PR validada (14 linhas)

📋 Regras customizadas: VoxKey/vox-key

💰 Custo estimado: 512 tokens (~$0.0010)

🤖 Gerando review...
→ Processando resposta...
  • 1 arquivo(s) com comentários

============================================================
📊 RESUMO DO REVIEW
============================================================

🔍 PR #4967: task finalizada
   azure-feature11303 → master
   Alterações: 14 linhas

📝 Arquivos revisados: 1
   🔴 Críticos: 0
   🟡 Importantes: 1
   🟢 Sugestões: 1

💰 Custo estimado: $0.0010
   Tokens usados: 512
```

## 🏷️ Como Pular Review

Adicione a label/tag `skip-review` na criação da PR.
Ou configure `REVIEW_SKIP_DRAFTS=false` para revisar drafts também.
