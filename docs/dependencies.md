# Dependências relevantes

> Toda dependência relevante precisa de função definida e licença compatível com
> Apache-2.0. Atualizado a cada sprint.

## Runtime

Nenhuma dependência de runtime adicionada na Sprint 0.

## Desenvolvimento (Sprint 0)

| Dependência                              | Versão | Função                        | Licença |
| ---------------------------------------- | ------ | ----------------------------- | ------- |
| ruff                                     | 0.16.x | Lint e formatação Python      | MIT     |
| mypy                                     | 2.3.x  | Type checking Python          | MIT     |
| pytest                                   | 9.1.x  | Testes Python                 | MIT     |
| pytest-cov                               | 7.1.x  | Cobertura                     | MIT     |
| prettier (via npx, versão fixada)        | 3.9.x  | Formatação Markdown/YAML/JSON | MIT     |
| pre-commit (opcional, ferramenta do dev) | 4.x    | Hooks locais                  | MIT     |

## Imagens de container

| Imagem   | Tag             | Função      |
| -------- | --------------- | ----------- |
| postgres | 18.6-alpine3.24 | Banco local |

## Previstas (decisão na sprint correspondente)

FastAPI, Uvicorn, Pydantic, pydantic-settings, SQLAlchemy 2, psycopg 3, Alembic (Sprint 1);
React, Vite, Tailwind CSS, Vitest, Playwright, ESLint (Sprint 1); biblioteca XML segura
(Sprint 2); leitor XLSX sem avaliação de fórmulas (Sprint 3); SDK Microsoft Graph ou
cliente HTTP (Sprint 6); MSAL/validação JWT (Sprint 7); OpenTelemetry (Sprint 7/8).
