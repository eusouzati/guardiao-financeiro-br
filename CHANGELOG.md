# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e
versionamento [SemVer](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added

- Sprint 0 — Foundation & Architecture:
  - Estrutura do monorepo (`backend/`, `frontend/`, `infra/`, `docs/`, `.github/`, `scripts/`).
  - Documentação inicial: README (EN/pt-BR), PROJECT_PLAN, ARCHITECTURE, SECURITY,
    CONTRIBUTING, CODE_OF_CONDUCT, docs de arquitetura, modelo de domínio, motor de regras,
    documentos fiscais, segurança, LGPD, backup, threat model, roadmap, convenções e
    política de dados fictícios.
  - ADRs 001–017.
  - Docker Compose com PostgreSQL 18 (somente `127.0.0.1`, health check).
  - Ferramentas de qualidade: Ruff, mypy (strict), pytest, Prettier, pre-commit, EditorConfig.
  - Teste de arquitetura que impede dependências proibidas entre camadas.
  - Scripts de verificação de ambiente (`scripts/check-env.*`).
  - Licença Apache-2.0 e NOTICE.

### Changed

- ADRs revisadas e aprovadas pelo mantenedor, com critérios registrados: precisões por
  natureza de campo e preservação da precisão original (ADR-007), requisitos da fila em
  PostgreSQL (ADR-009), idioma (ADR-013) e polling evolutivo para webhooks (ADR-015).
- Especificação de desenvolvimento local mantida fora do versionamento.
- Ambiente `dev` no Azure antecipado para a nova Sprint 1A (ADR-017).

### Added (pós-revisão)

- `scripts/azure/check-access.ps1`: diagnóstico somente leitura de acesso ao Azure e tabela
  de acessos necessários em `docs/deployment-azure.md`.

### Fixed

- `check-env`: verifica se o engine do Docker está em execução (não só o CLI), mostra a
  versão correta do Azure CLI e orienta a instalação do uv e a troca da senha placeholder.
