# Microsoft 365 do MVP

Scripts idempotentes que preparam o Microsoft 365 do único ambiente do projeto (MVP),
conforme [ADR-007](../../docs/decisions/ADR-007-microsoft-365-mailbox.md) e
[`docs/microsoft-365.md`](../../docs/microsoft-365.md).

> Nenhum tenant, domínio, usuário ou segredo real fica nestes arquivos: tudo chega por
> parâmetro. Nenhum script apaga caixa, App Registration ou Service Principal.
> Nenhum e-mail é lido ou processado na Sprint 0.

| Ordem | Script                     | O que faz                                                                                    | Ferramenta                  |
| ----- | -------------------------- | -------------------------------------------------------------------------------------------- | --------------------------- |
| 1     | `New-MvpMailbox.ps1`       | Cria/confere a Shared Mailbox do MVP e marca `CustomAttribute1`; bloqueia login interativo   | Exchange Online + Azure CLI |
| 2     | `New-AppRegistrations.ps1` | Cria/confere `guardiao-financeiro-web-mvp` e `guardiao-financeiro-mail-mvp` e seus SPs       | Azure CLI (Microsoft Graph) |
| 3     | `Set-ExchangeAppRbac.ps1`  | Limita o app de e-mail à caixa do MVP (RBAC for Applications, papel `Application Mail.Read`) | Exchange Online             |
| 4     | `Test-MailboxAccess.ps1`   | Prova: caixa do MVP → permitido; outra caixa → negado; nenhuma permissão Graph no Entra ID   | Exchange Online + Azure CLI |

Todos aceitam `-WhatIf` (exceto o teste, que já é somente leitura) e param (**PARE**) se o
tenant ou o domínio conectado não forem os esperados.

## Pré-requisitos

- Tenant com Exchange Online (a Shared Mailbox não exige licença até 50 GB).
- Usuário administrador (`MVP_ADMIN_USER`) com **Exchange Administrator** (ou Organization
  Management) e permissão para registrar aplicativos no Entra ID.
- Módulo `ExchangeOnlineManagement` — os scripts **não instalam** nada. Instalação, se
  aprovada: `Install-Module ExchangeOnlineManagement -Scope CurrentUser`.
- Azure CLI autenticada no mesmo tenant (`az login --tenant <tenant-id>`).
- Organização do Exchange com personalização habilitada (necessária para escopos e
  atribuições de RBAC). Tenants novos vêm "desidratados": nesse caso
  `Set-ExchangeAppRbac.ps1` para e pede autorização; com ela, execute-o uma vez com
  `-EnableOrganizationCustomization` (mudança única e permanente no tenant, pode levar
  algumas horas) e depois novamente sem o switch.

## Execução

```powershell
$domain = '<M365_TENANT_DOMAIN>'
$alias  = '<MVP_SHARED_MAILBOX_ALIAS>'   # sugerido: guardiao-financeiro-mvp
$admin  = '<MVP_ADMIN_USER>'
$env:AZURE_TENANT_ID = '<AZURE_TENANT_ID>'

./infra/m365/New-MvpMailbox.ps1 -TenantDomain $domain -MailboxAlias $alias -AdminUser $admin -WhatIf
./infra/m365/New-MvpMailbox.ps1 -TenantDomain $domain -MailboxAlias $alias -AdminUser $admin

# Redirect URI do Easy Auth: URL do frontend publicada na fase "apps" do deploy Azure.
./infra/m365/New-AppRegistrations.ps1 -WebRedirectUri 'https://<web-fqdn>/.auth/login/aad/callback'

./infra/m365/Set-ExchangeAppRbac.ps1 -TenantDomain $domain -MailboxAlias $alias -AdminUser $admin -WhatIf
./infra/m365/Set-ExchangeAppRbac.ps1 -TenantDomain $domain -MailboxAlias $alias -AdminUser $admin

# Após a propagação (30 min a 2 h):
./infra/m365/Test-MailboxAccess.ps1 -TenantDomain $domain -MailboxAlias $alias -AdminUser $admin `
    -OutOfScopeMailbox '<outra-caixa-existente>'
```

IDs públicos gerados (App IDs e Object IDs, sem segredos) ficam em `.azure/m365-mvp.json`,
ignorado pelo Git.

## Decisões de segurança

- **Duas identidades separadas:** autenticação da aplicação (web) ≠ ingestão de e-mail.
- **Sem permissão `Mail.*` no Entra ID** para o app de e-mail: permissões do Entra e do
  RBAC for Applications são somadas; um consentimento no Entra valeria para todas as caixas.
  `New-AppRegistrations.ps1` e `Test-MailboxAccess.ps1` param se encontrarem uma.
- **Escopo por atributo:** `CustomAttribute1 = guardiao-financeiro-mvp`. O script de RBAC
  confere que o filtro alcança **exatamente uma** caixa antes de atribuir o papel.
- **Sem credenciais nesta sprint:** o segredo do Easy Auth (web) nasce na Sprint 1; a
  credencial do app de e-mail (preferência: certificado no Key Vault) na Sprint 6.
- Remoção manual e ordem segura: [`docs/teardown-mvp.md`](../../docs/teardown-mvp.md).
