# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e
versionamento [SemVer](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Changed — Plano Cloud-First (Sprint 0 — MVP Cloud Foundation & Microsoft 365 Foundation)

- Arquitetura revista: um único ambiente de nuvem, **MVP**, com recursos reais no Azure e
  no Microsoft 365 desde a Sprint 0 (ADR-001). Nenhum ambiente de homologação/produção.
- ADRs renumeradas para a lista mínima do plano (001–011) e complementares (012–020), todas
  com status `PROPOSED`; novas ADR-001 (MVP cloud-first) e ADR-011 (rede do MVP);
  ADR-004 alinhada aos campos e estados da fila (`PENDING`/`PROCESSING`/`COMPLETED`/`FAILED`/`DEAD`).
- `APP_ENV` passa a aceitar `local`, `test` e `mvp`; a imagem do backend assume `mvp`;
  Easy Auth permitido somente em `mvp`.
- Códigos de regra alinhados ao plano (`DUPLICATE_EXACT`, `AMOUNT_MISMATCH`, …).
- `docs/backup-recovery.md` → `docs/backup-restore.md`.

### Added — Sprint 0 (Cloud-First)

- `GET /health` e `GET /ready` (sondas do Container Apps); página pública `/status`
  ("Guardião Financeiro BR", "MVP", "Status da API").
- Bicep em `infra/azure` (rede, identidades, Container Apps environment e apps de
  bootstrap, ACR, PostgreSQL 18, Storage, Key Vault, monitoramento, orçamento) e scripts
  `scripts/azure/deploy-mvp.ps1` (valida assinatura/tenant/usuário, what-if, duas fases) e
  `scripts/azure/test-mvp.ps1` (validação de segurança pós-deploy).
- Scripts idempotentes em `infra/m365`: Shared Mailbox, App Registrations web/mail,
  Exchange RBAC for Applications e teste de escopo.
- Documentação: `cloud-architecture.md`, `cost-management.md`, `teardown-mvp.md`,
  `docs/sprint-0/`, deploy Azure e Microsoft 365 reescritos.

### Added — Base de código do plano anterior (reaproveitada)

- Backend FastAPI (`uvicorn app.main:create_app --factory`) com configuração validada
  (pydantic-settings), logs JSON com `request_id` e redação de dados sensíveis, cabeçalhos
  de segurança, erros padronizados `GFB-XXXX` em pt-BR e OpenAPI em `/api/docs`.
- Health checks `/api/health/live` e `/api/health/ready` (banco + revisão do schema).
- Endpoints reais: `GET /api/v1/me`, `GET /api/v1/configurations`, `GET /api/v1/audit/events`.
- Autenticação DEV simulada com travas (somente `APP_ENV=local`; falha na inicialização em
  outros ambientes) e matriz de permissões por perfil aplicada no backend.
- PostgreSQL + SQLAlchemy 2 + Alembic: migration `0001` com `organization`,
  `configuration` (versionada) e `audit_event`; triggers append-only.
- Políticas configuráveis da empresa com padrões no domínio e sobrescritas versionadas.
- Comando `python -m app.cli bootstrap` (organização padrão fictícia, idempotente).
- Frontend React 19 + TypeScript + Vite + Tailwind CSS 4: layout responsivo, navegação,
  páginas Painel, Exceções, Documentos, Pedidos, Recebimentos, Fornecedores e Configurações;
  formatação pt-BR sem `float`; acessibilidade (skip link, foco visível, status com ícone e texto).
- Testes: pytest (unitários + integração com PostgreSQL), Vitest + Testing Library,
  Playwright (E2E); ESLint (strict + jsx-a11y) e Prettier.
- Docker: imagens do backend (usuário não-root) e frontend (Nginx sem privilégios, CSP
  estrita), serviço `migrate`, health checks e containers somente leitura.
- Documentação: ADR-020, `docs/api.md`, `docs/error-codes.md`, dependências e licenças.
- Nginx resolve o backend dinamicamente (DNS do Docker): recriar o container do backend não
  quebra mais o proxy `/api/` do frontend.

### Added — Fundação do plano anterior

- Foundation & Architecture:
  - Estrutura do monorepo (`backend/`, `frontend/`, `infra/`, `docs/`, `.github/`, `scripts/`).
  - Documentação inicial: README (EN/pt-BR), PROJECT_PLAN, ARCHITECTURE, SECURITY,
    CONTRIBUTING, CODE_OF_CONDUCT, docs de arquitetura, modelo de domínio, motor de regras,
    documentos fiscais, segurança, LGPD, backup, threat model, roadmap, convenções e
    política de dados fictícios.
  - ADRs iniciais (renumeradas em 2026-09-29).
  - Docker Compose com PostgreSQL 18 (somente `127.0.0.1`, health check).
  - Ferramentas de qualidade: Ruff, mypy (strict), pytest, Prettier, pre-commit, EditorConfig.
  - Teste de arquitetura que impede dependências proibidas entre camadas.
  - Scripts de verificação de ambiente (`scripts/check-env.*`).
  - Licença Apache-2.0 e NOTICE.

### Changed

- ADRs revisadas e aprovadas pelo mantenedor, com critérios registrados: precisões por
  natureza de campo e preservação da precisão original (ADR-009), requisitos da fila em
  PostgreSQL (ADR-004), idioma (ADR-010) e polling evolutivo para webhooks (ADR-007).
- Especificação de desenvolvimento local mantida fora do versionamento.

### Added (pós-revisão)

- `scripts/azure/check-access.ps1`: diagnóstico somente leitura de acesso ao Azure e tabela
  de acessos necessários em `docs/deployment-azure.md`.

### Fixed

- `check-env`: verifica se o engine do Docker está em execução (não só o CLI), mostra a
  versão correta do Azure CLI e orienta a instalação do uv e a troca da senha placeholder.
