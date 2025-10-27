# Review Rules - Regras Customizadas por Repositório

Este diretório contém regras específicas de code review para cada projeto/repositório.

## Estrutura

```
review_rules/
├── [projeto]/
│   └── [repositorio].md
└── README.md
```

## Como Usar

1. Crie uma pasta com o nome do projeto (ex: `Portal de Boletos`)
2. Dentro dela, crie um arquivo `.md` com o nome do repositório (ex: `boletoonline-php8.md`)
3. Escreva as regras específicas em markdown

## Exemplo

**Arquivo:** `review_rules/Portal de Boletos/boletoonline-php8.md`

```markdown
# Regras Específicas - Boleto Online PHP8

## Prioridades
- Validar compatibilidade com PHP 8.x
- Verificar uso correto de tipagem estrita
- Validar segurança em transações financeiras

## Padrões Obrigatórios
- Todo código de pagamento DEVE ter try/catch
- Logs DEVEM ser enviados para o sistema de monitoramento
- Variáveis de ambiente NUNCA devem ser commitadas

## Arquivos Críticos
- `/app/Models/Pagamento/`: Qualquer mudança aqui é CRÍTICA
- `/app/Services/Boleto/`: Revisar lógica de cálculo de juros
```

## Formato das Regras

As regras devem ser escritas em **markdown** e podem conter:
- Prioridades específicas do projeto
- Padrões de código obrigatórios
- Arquivos/diretórios críticos
- Validações específicas do domínio
- Convenções de nomenclatura
- Requisitos de segurança

O LLM irá considerar essas regras ao gerar o code review.
