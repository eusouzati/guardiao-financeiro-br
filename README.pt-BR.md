# Guardião Financeiro BR

> Plataforma open source de **conferência inteligente de contas a pagar** para o mercado brasileiro.

**Status:** 🚧 Sprint 0 — fundação cloud do MVP (Azure + Microsoft 365). Funcionalidades de negócio começam na Sprint 2.
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
- Ambiente único **MVP** no Azure (Container Apps, PostgreSQL 18, Blob Storage, Key Vault)
  e no Microsoft 365, provisionado por Bicep e scripts idempotentes.

## Arquitetura

Cloud-First: SPA React + TypeScript → monólito modular FastAPI (API + worker) no Azure
Container Apps → Azure PostgreSQL 18 e Azure Blob Storage, com segredos no Key Vault e uma
Shared Mailbox dedicada no Microsoft 365. Existe um único ambiente, o **MVP**. Veja
[ARCHITECTURE.md](ARCHITECTURE.md), [docs/cloud-architecture.md](docs/cloud-architecture.md)
e as [ADRs](docs/decisions/README.md).

## Desenvolvimento local

O ambiente oficial é o MVP no Azure ([docs/deployment-azure.md](docs/deployment-azure.md));
a máquina local serve para desenvolver e testar. Requisitos: Git e Docker Desktop.

```bash
cp .env.example .env         # defina POSTGRES_PASSWORD; para uso local, DEV_AUTH_ENABLED=true
docker compose up --build    # PostgreSQL + migrations + API + interface
```

Acesse <http://localhost:8080> (documentação da API em <http://localhost:8000/api/docs>).
O login local é simulado e só funciona com `APP_ENV=local`; no MVP a autenticação é o
Microsoft Entra ID.

Detalhes em [docs/environment-setup.md](docs/environment-setup.md).

## Docker

`docker compose up` sobe PostgreSQL 18, migrations (serviço `migrate`), API FastAPI e a
interface servida por Nginx. Todas as portas ficam publicadas somente em `127.0.0.1`, com
health checks, containers somente leitura e sem privilégios adicionais.

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
