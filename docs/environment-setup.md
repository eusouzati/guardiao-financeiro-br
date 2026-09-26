# Preparação do ambiente de desenvolvimento

## Ferramentas necessárias

| Ferramenta                       | Versão   | Obrigatória a partir de | Para quê                                     |
| -------------------------------- | -------- | ----------------------- | -------------------------------------------- |
| Git                              | 2.40+    | Sprint 0                | Versionamento                                |
| Docker Desktop (com Compose v2+) | recente  | Sprint 0                | PostgreSQL local e, depois, a stack completa |
| uv                               | 0.8+     | Sprint 0                | Python 3.13 + dependências do backend        |
| Node.js                          | 24 LTS   | Sprint 1                | Frontend (npm incluso)                       |
| Azure CLI + Bicep                | recente  | Sprint 8                | Validação de IaC (sem criar recursos)        |
| GitHub CLI                       | opcional | Sprint 9                | PRs/Actions                                  |

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

## Primeiros passos (Sprint 0)

```bash
cp .env.example .env            # ajuste POSTGRES_PASSWORD
docker compose up -d            # sobe apenas o PostgreSQL
docker compose ps               # aguarde status "healthy"

cd backend
uv sync                         # cria .venv com Python 3.13 e ferramentas de dev
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest
```

## Observações para Windows

- O repositório força finais de linha LF (`.gitattributes`); configure o editor para LF.
- Execute Docker Desktop com backend WSL 2. O erro `open //./pipe/dockerDesktopLinuxEngine`
  significa que o Docker Desktop está fechado ou o engine ainda não terminou de iniciar.
- Se o Git reclamar de _dubious ownership_ na pasta, use
  `git config --global --add safe.directory C:/Projetos/guardiao-financeiro-br`.
