# ADR-006 — Monorepo e monólito modular em camadas

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26
- **Data:** 2026-09-26
- **Sprint:** 0

## Contexto

Equipe pequena, produto único, deploy simples. O escopo pede separação clara entre API,
domínio, persistência, segurança, regras e integrações, sem arquitetura acadêmica.

## Decisão

- **Monorepo** com `backend/`, `frontend/`, `infra/`, `docs/`, `.github/`.
- Backend como **monólito modular** (um serviço FastAPI) em camadas:

```text
api ─────────► services ─────► domain
                  │  ▲            ▲
                  ▼  │            │
          repositories/models   parsers, rules, matching (puros)
                  │
          integrations (storage, Graph, Key Vault) via interfaces
```

- Regras de dependência (verificadas por teste automatizado em
  `backend/tests/architecture/`):
  - `domain` não importa nenhuma outra camada da aplicação nem SQLAlchemy/FastAPI.
  - `parsers`, `rules` e `matching` não importam `models`, `repositories`, `api`,
    `integrations` nem SQLAlchemy (parsers retornam estruturas normalizadas).
  - `models`/`repositories` não importam `api`.
  - `api` não importa `models`/`repositories` diretamente — passa por `services`.
- Processamento assíncrono roda no mesmo código, em processo worker separado (ADR-009).

## Alternativas consideradas

- **Microsserviços** — overhead operacional sem ganho no MVP; rejeitado.
- **Clean/Hexagonal completa com casos de uso por classe** — cerimônia excessiva.
- **Repositórios separados front/back** — dificulta versionamento conjunto e CI.

## Consequências

- Violações de camadas quebram o build de testes.
- Extração futura de serviços é possível porque as fronteiras já estão explícitas.
