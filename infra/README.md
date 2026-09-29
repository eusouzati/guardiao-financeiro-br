# Infraestrutura

Infraestrutura como código do **único ambiente do projeto: MVP**
([ADR-001](../docs/decisions/ADR-001-mvp-cloud-first.md),
[ADR-019](../docs/decisions/ADR-019-infrastructure-as-code.md)).

```text
infra/
├── azure/                       # Bicep (escopo de assinatura)
│   ├── main.bicep               # grupo de recursos + módulos
│   ├── types.bicep              # tipo dos SKUs (parâmetro genérico "sku")
│   ├── bicepconfig.json         # regras do linter
│   ├── parameters/
│   │   └── mvp.bicepparam       # valores dinâmicos chegam por variáveis de ambiente
│   └── modules/
│       ├── network.bicep
│       ├── identities.bicep
│       ├── container-apps-environment.bicep
│       ├── container-apps.bicep # aplicações de bootstrap (api, web) e job de migração
│       ├── registry.bicep
│       ├── postgres.bicep
│       ├── storage.bicep
│       ├── keyvault.bicep
│       ├── monitoring.bicep
│       └── cost-management.bicep
└── m365/                        # PowerShell idempotente (Exchange Online + Entra ID)
```

Os módulos aceitam parâmetros genéricos (`environment`, `location`, `resourcePrefix`,
`tags`, `sku`); não existem arquivos de outros ambientes.

- Deploy, validação e custos: [`docs/deployment-azure.md`](../docs/deployment-azure.md) e
  [`docs/cost-management.md`](../docs/cost-management.md).
- Microsoft 365: [`m365/README.md`](m365/README.md).
- Remoção: [`docs/teardown-mvp.md`](../docs/teardown-mvp.md) (nunca automática).
