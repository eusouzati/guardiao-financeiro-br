# Preparação do ambiente de desenvolvimento

## Ferramentas necessárias

| Ferramenta                       | Versão           | Obrigatória a partir de | Para quê                                     |
| -------------------------------- | ---------------- | ----------------------- | -------------------------------------------- |
| Git                              | 2.40+            | Sprint 0                | Versionamento                                |
| Docker Desktop (com Compose v2+) | recente          | Sprint 0                | PostgreSQL local e, depois, a stack completa |
| uv                               | 0.8+             | Sprint 0                | Python 3.13 + dependências do backend        |
| Node.js                          | 24 LTS (≥ 22.22) | Sprint 1                | Frontend (npm incluso)                       |
| Azure CLI + Bicep                | recente          | Sprint 8                | Validação de IaC (sem criar recursos)        |
| GitHub CLI                       | opcional         | Sprint 9                | PRs/Actions                                  |

## Instalação do uv

- Windows: `winget install --id=astral-sh.uv -e` (ou o instalador oficial em
  <https://docs.astral.sh/uv/getting-started/installation/>). Abra um **novo** terminal
  depois de instalar para o `PATH` ser atualizado.
- Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Não é preciso instalar Python separadamente: `uv sync` baixa o Python 3.13 definido em
`.python-version`.

## Verificação rápida

Windows (PowerShell):

```powershell
./scripts/check-env.ps1
```

Linux/macOS/WSL:

```bash
./scripts/check-env.sh
```

## Subir a aplicação completa (Docker)

```bash
cp .env.example .env            # defina POSTGRES_PASSWORD; para usar localmente, DEV_AUTH_ENABLED=true
docker compose up --build -d    # db → migrate → backend → frontend
docker compose ps               # aguarde backend e frontend "healthy"
```

- Aplicação: <http://localhost:8080>
- API / OpenAPI: <http://localhost:8000/api/docs>
- O serviço `migrate` aplica as migrations e cria a organização padrão (fictícia) e termina
  com status `Exited (0)` — isso é esperado.
- Logs: `docker compose logs -f backend` (JSON, com `request_id`).

## Desenvolvimento com recarga automática

Com o banco do Compose rodando (`docker compose up -d db`):

```bash
# Backend (terminal 1)
cd backend
uv sync
# PowerShell: $env:APP_ENV="local"; $env:DEV_AUTH_ENABLED="true"; $env:POSTGRES_PASSWORD="<senha do .env>"
export APP_ENV=local DEV_AUTH_ENABLED=true POSTGRES_PASSWORD=<senha do .env>
uv run alembic upgrade head
uv run python -m app.cli bootstrap
uv run uvicorn app.main:create_app --factory --reload --port 8000

# Frontend (terminal 2) — proxy de /api para http://localhost:8000
cd frontend
npm ci
npm run dev                     # http://localhost:5173
```

## Qualidade e testes

```bash
# Backend
cd backend
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest                   # unitários; integração é pulada sem TEST_DATABASE_URL

# Integração (PostgreSQL real). O nome do banco DEVE conter "test": ele é recriado.
docker compose exec db createdb -U guardiao guardiao_test
# PowerShell: $env:TEST_DATABASE_URL="postgresql://guardiao:<senha>@localhost:5432/guardiao_test"
export TEST_DATABASE_URL=postgresql://guardiao:<senha>@localhost:5432/guardiao_test
uv run pytest --cov

# Frontend
cd frontend
npm run lint && npm run typecheck && npm run format:check
npm test
npm run build

# E2E (com a stack rodando via Compose e DEV_AUTH_ENABLED=true)
npx playwright install chromium
npm run e2e
```

## Observações para Windows

- O repositório força finais de linha LF (`.gitattributes`); configure o editor para LF.
- Execute Docker Desktop com backend WSL 2. O erro `open //./pipe/dockerDesktopLinuxEngine`
  significa que o Docker Desktop está fechado ou o engine ainda não terminou de iniciar.
- Se o Git reclamar de _dubious ownership_ na pasta, use
  `git config --global --add safe.directory C:/Projetos/guardiao-financeiro-br`.
