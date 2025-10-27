## TEMPLATE: boletoonline-php8.md
```markdown
# Code Review - Boleto Online

## Stack
PHP 8.0 / Laravel 8 / MySQL 8

## Arquivos a Ignorar
- *.lock
- .env*
- database/migrations/*.php
- config/*.php

## Critérios Específicos

### SEGURANÇA (40%)
- Nunca usar `DB::raw()` sem prepared statements
- Validar formato por código de banco
- Sanitizar inputs de formulários

### ARQUITETURA (30%)
- Controllers apenas delegam (max 3 métodos públicos)
- Lógica em Services (app/Services)
- Formatters em app/Formatters ou app/Models/GeracaoPDF
- Models sem lógica de negócio (apenas relationships/casts)

### PERFORMANCE (20%)
- Eager loading obrigatório: `->with(['relation'])`
- Cache config bancárias (1h): `Cache::remember('banco_'.$cod, 3600, ...)`
- Jobs para processamentos longos

### PADRÕES (10%)
- PSR-12 strict
- Variáveis: `snake_case`
- Métodos: `camelCase`
- Classes: `PascalCase`

## Sistema de Notas
- **9-10**: Excelente, pronto para merge
- **7-8**: Bom, ajustes menores
- **5-6**: Correções necessárias antes do merge
- **3-4**: Refatoração obrigatória
- **0-2**: BLOQUEADO - críticos de segurança
````