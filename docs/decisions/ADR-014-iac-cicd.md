# ADR-014 — IaC com Bicep e GitHub Actions com OIDC

- **Status:** Aceita
- **Data:** 2026-09-26
- **Sprint:** 0 (implementação: Sprints 8/9)

## Decisão

- Infraestrutura Azure somente por **Bicep** (`infra/main.bicep` + `infra/modules/*`),
  com parâmetros por ambiente (`dev`, `hml`, `prod`) e **região parametrizada**
  (padrão sugerido `brazilsouth`, sem presumir que a LGPD exija dados no Brasil).
- Validação com `az bicep build`, `az deployment group validate` e `what-if` antes de
  qualquer criação real — que **depende de autorização explícita do mantenedor**.
- GitHub Actions autentica no Azure por **OpenID Connect** (federated credentials),
  sem client secret permanente. GitHub Environments: `development`, `homologation`,
  `production` (com aprovação manual obrigatória).
- Actions de terceiros fixadas por **SHA**; permissões mínimas por job (`permissions:`).

## Alternativas consideradas

- **Terraform** — multi-cloud desnecessário; Bicep é nativo e sem state file a proteger.
- **Service Principal com secret** — credencial de longa duração; rejeitado.

## Consequências

- Nenhum recurso Azure é criado sem autorização explícita. O ambiente `dev` foi antecipado
  para a Sprint 1A (ADR-017); `hml`/`prod` permanecem na Sprint 8.
