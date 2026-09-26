# Guardião Financeiro BR

> Open source, exception-based **accounts payable verification** for the Brazilian market.

**Status:** 🚧 Sprint 0 — foundation & architecture. No business features yet.
Leia em português: [README.pt-BR.md](README.pt-BR.md).

## The problem

Small and mid-sized Brazilian companies still check supplier invoices by hand: NF-e/NFS-e
XML files arrive by e-mail, analysts compare them against purchase orders in spreadsheets
and confirm receipt with other teams. Duplicates, wrong amounts, wrong recipients and
invoices without purchase orders slip through.

## The solution

Guardião Financeiro BR receives fiscal documents, extracts their data from the XML
(the authoritative source), matches them against **purchase orders and receipts
(three-way match)** and runs a **deterministic, versioned rule engine**:

> Process the normal cases automatically. Send only the exceptions to a human — and
> explain why.

Out of 150 documents, the analyst should only need to look at the 24 with exceptions
(possible duplicates, amount or supplier mismatches, missing PO or receipt, math
inconsistencies…).

What it is **not**: an ERP, a payment system, a tax/accounting engine, or an authority
on whether a document is fiscally or legally correct. It never takes irreversible
financial decisions and its core uses **no LLM**.

## Planned features (MVP v0.1.0)

- NF-e (model 55) and national-standard NFS-e XML parsing, ready for the IBS/CBS tax
  reform fields and the new alphanumeric CNPJ.
- Supplier, purchase order and receipt import via CSV/XLSX.
- 13 initial rules (exact/fiscal/possible duplicates, recipient/supplier mismatch,
  missing PO/receipt, amount and item mismatch with configurable tolerance, quantity
  above received, inconsistent totals, future/old dates).
- Explainable statuses: `MATCHED`, `MATCHED_WITH_WARNINGS`, `NEEDS_REVIEW`, `BLOCKED`.
- Exception workbench with side-by-side comparison, human review and append-only audit trail.
- Microsoft 365 mailbox ingestion via Microsoft Graph, scoped to a single mailbox.
- Microsoft Entra ID authentication, backend-enforced RBAC, LGPD by design.
- Azure deployment (Container Apps, PostgreSQL Flexible Server, Blob, Key Vault) via Bicep.

## Architecture

React + TypeScript SPA → FastAPI modular monolith (API + worker) → PostgreSQL and
document storage (local disk or Azure Blob). See [ARCHITECTURE.md](ARCHITECTURE.md),
[docs/architecture.md](docs/architecture.md) and the [ADRs](docs/decisions/README.md).

## Quick start (Sprint 0)

Requirements: Git, Docker Desktop, [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env      # set POSTGRES_PASSWORD to any local value
docker compose up -d      # starts PostgreSQL only (API/frontend arrive in Sprint 1)
cd backend && uv sync && uv run pytest
```

Details: [docs/environment-setup.md](docs/environment-setup.md).

## Security

See [SECURITY.md](SECURITY.md) to report vulnerabilities and
[docs/security.md](docs/security.md) / [docs/threat-model.md](docs/threat-model.md) for
the security design. The repository contains **only fictitious data**
([policy](docs/synthetic-data-policy.md)).

## Roadmap

[docs/roadmap.md](docs/roadmap.md) · [PROJECT_PLAN.md](PROJECT_PLAN.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

[Apache License 2.0](LICENSE).
