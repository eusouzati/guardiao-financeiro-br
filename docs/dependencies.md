# Dependências relevantes

> Toda dependência relevante precisa de função definida e licença compatível com
> Apache-2.0. Versões fixadas em `backend/uv.lock` e `frontend/package-lock.json`.
> Atualizado a cada sprint.

## Backend — runtime

| Dependência       | Versão  | Função                                  | Licença             |
| ----------------- | ------- | --------------------------------------- | ------------------- |
| fastapi           | 0.141.1 | API HTTP, validação de entrada, OpenAPI | MIT                 |
| uvicorn           | 0.54.0  | Servidor ASGI                           | BSD-3-Clause        |
| pydantic          | 2.13.5  | Schemas e serialização                  | MIT                 |
| pydantic-settings | 2.15.0  | Configuração por variáveis de ambiente  | MIT                 |
| sqlalchemy        | 2.1.1   | ORM e acesso a dados                    | MIT                 |
| alembic           | 1.20.0  | Migrations                              | MIT                 |
| psycopg[binary]   | 3.3.6   | Driver PostgreSQL                       | **LGPL-3.0-only** ¹ |

¹ Usado sem modificação, como biblioteca carregada dinamicamente. A LGPL permite esse uso
em projeto Apache-2.0; a imagem Docker redistribui o pacote original do PyPI (código-fonte
disponível no projeto psycopg). Ver ADR-018.

Dependências transitivas principais: starlette (BSD-3), anyio (MIT), mako (MIT),
typing-extensions (PSF-2.0).

## Backend — desenvolvimento

| Dependência | Versão | Função                                   | Licença      |
| ----------- | ------ | ---------------------------------------- | ------------ |
| ruff        | 0.16.9 | Lint e formatação                        | MIT          |
| mypy        | 2.3.1  | Type checking (strict + plugin Pydantic) | MIT          |
| pytest      | 9.1.1  | Testes                                   | MIT          |
| pytest-cov  | 7.1.0  | Cobertura                                | MIT          |
| httpx2      | 2.13.1 | Cliente HTTP do `TestClient`             | BSD-3-Clause |

## Frontend — runtime (incluído no bundle)

| Dependência       | Versão | Função     | Licença |
| ----------------- | ------ | ---------- | ------- |
| react / react-dom | 19.3.0 | UI         | MIT     |
| react-router      | 8.4.0  | Roteamento | MIT     |

## Frontend — build e qualidade

| Dependência                                  | Versão                  | Função                                              | Licença    |
| -------------------------------------------- | ----------------------- | --------------------------------------------------- | ---------- |
| vite + @vitejs/plugin-react                  | 8.3.1 / 6.1.1           | Dev server e build                                  | MIT        |
| typescript                                   | 6.0.3                   | Tipagem (TS 7 aguarda suporte do typescript-eslint) | Apache-2.0 |
| tailwindcss + @tailwindcss/vite              | 4.3.3                   | Estilos (CSS gerado em build)                       | MIT        |
| eslint + @eslint/js                          | 9.39.5                  | Lint (ESLint 10 aguarda suporte do jsx-a11y)        | MIT        |
| typescript-eslint                            | 8.70.1                  | Regras TypeScript (strict type-checked)             | MIT        |
| eslint-plugin-jsx-a11y                       | 6.10.2                  | Regras de acessibilidade                            | MIT        |
| eslint-plugin-react-hooks / react-refresh    | 7.1.1 / 0.5.7           | Regras React                                        | MIT        |
| prettier                                     | 3.9.9                   | Formatação                                          | MIT        |
| vitest + @vitest/coverage-v8                 | 5.0.2                   | Testes unitários e cobertura                        | MIT        |
| @testing-library/react, jest-dom, user-event | 16.3.3 / 7.0.1 / 14.6.7 | Testes de componentes                               | MIT        |
| jsdom                                        | 30.1.1                  | DOM para testes                                     | MIT        |
| @playwright/test                             | 1.63.0                  | Testes E2E                                          | Apache-2.0 |

Árvore completa de dev (via `license-checker`): predominantemente MIT/Apache/ISC/BSD;
MPL-2.0 e CC-BY-4.0 aparecem apenas em ferramentas de build (não entram no bundle).

## Imagens de container

| Imagem               | Tag                        | Função                                         |
| -------------------- | -------------------------- | ---------------------------------------------- |
| postgres             | 18.6-alpine3.24            | Banco local                                    |
| python               | 3.13.15-slim-trixie        | Base do backend                                |
| ghcr.io/astral-sh/uv | 0.12.19                    | Instalação de dependências no build do backend |
| node                 | 24.21.0-alpine3.24         | Build do frontend                              |
| nginx                | 1.30.5-alpine3.24 (stable) | Servir a SPA e proxy `/api/`                   |

Fixação por digest, scan (Trivy) e SBOM: Sprint 9.

## Previstas (decisão na sprint correspondente)

Biblioteca XML segura (Sprint 2); leitor XLSX sem avaliação de fórmulas (Sprint 3); cliente
Microsoft Graph (Sprint 6); validação JWT/MSAL (Sprint 7); OpenTelemetry (Sprint 7/8).
