# Guardião Financeiro BR

> Plataforma open source de **conferência inteligente de contas a pagar** para o mercado brasileiro.

**Status:** 🚧 Sprint 0 — fundação e arquitetura. Ainda sem funcionalidades de negócio.
Read in English: [README.md](README.md).

## O problema

Pequenas e médias empresas ainda conferem notas de fornecedores manualmente: XMLs de
NF-e/NFS-e chegam por e-mail, o analista compara com pedidos em planilhas e confirma o
recebimento com outras áreas. Duplicidades, valores divergentes, destinatário errado e
notas sem pedido passam despercebidos.

## A solução

O Guardião Financeiro BR recebe documentos fiscais, extrai os dados do XML (fonte
autoritativa), cruza com **pedidos e recebimentos (three-way match)** e executa um
**motor de regras determinístico e versionado**:

> Processar automaticamente os casos normais e encaminhar somente exceções para análise
> humana — explicando o porquê.

De 150 documentos recebidos, o analista deve olhar apenas os 24 com exceções (possíveis
duplicidades, valor ou fornecedor divergente, sem pedido, sem recebimento,
inconsistência matemática…).

O sistema **não** é ERP, **não** paga, **não** escritura, **não** afirma que um documento
está fiscal/contábil/juridicamente correto e **não** toma decisões financeiras
irreversíveis. O núcleo funciona **sem LLM**.

## Funcionalidades previstas (MVP v0.1.0)

- Leitura de XML de NF-e (modelo 55) e NFS-e padrão nacional, preparada para IBS/CBS e
  para o CNPJ alfanumérico.
- Importação de fornecedores, pedidos e recebimentos por CSV/XLSX.
- 13 regras iniciais (duplicidade exata, fiscal e possível; destinatário e fornecedor
  divergentes; pedido/recebimento ausente; valor e item divergentes com tolerância;
  quantidade acima do recebido; total inconsistente; datas futura/antiga).
- Status explicáveis: `MATCHED`, `MATCHED_WITH_WARNINGS`, `NEEDS_REVIEW`, `BLOCKED`.
- Bancada de exceções com comparação lado a lado, revisão humana e auditoria append-only.
- Ingestão da caixa de contas a pagar do Microsoft 365 via Graph, restrita a uma caixa.
- Microsoft Entra ID, RBAC aplicado no backend, LGPD desde a concepção.
- Implantação no Azure via Bicep.

## Arquitetura

SPA React + TypeScript → monólito modular FastAPI (API + worker) → PostgreSQL e storage de
documentos (disco local ou Azure Blob). Veja [ARCHITECTURE.md](ARCHITECTURE.md),
[docs/architecture.md](docs/architecture.md) e as [ADRs](docs/decisions/README.md).

## Início rápido (Sprint 0)

Requisitos: Git, Docker Desktop e [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env      # defina POSTGRES_PASSWORD com um valor local
docker compose up -d      # sobe apenas o PostgreSQL (API/frontend chegam na Sprint 1)
cd backend && uv sync && uv run pytest
```

Detalhes em [docs/environment-setup.md](docs/environment-setup.md).

## Docker

`docker compose up` sobe o ambiente local. Na Sprint 0 apenas o PostgreSQL 18, publicado
somente em `127.0.0.1`, com health check.

## Segurança

Como reportar vulnerabilidades: [SECURITY.md](SECURITY.md). Desenho de segurança:
[docs/security.md](docs/security.md), [docs/threat-model.md](docs/threat-model.md),
[docs/lgpd.md](docs/lgpd.md). O repositório contém **apenas dados fictícios**
([política](docs/synthetic-data-policy.md)).

## Roadmap

[docs/roadmap.md](docs/roadmap.md) · [PROJECT_PLAN.md](PROJECT_PLAN.md)

## Contribuição

[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Screenshots

Serão adicionadas a partir da Sprint 5.

## Licença

[Apache License 2.0](LICENSE).
