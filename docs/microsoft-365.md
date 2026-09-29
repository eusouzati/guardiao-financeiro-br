# Microsoft 365 do MVP

> A infraestrutura Microsoft 365 existe desde a **Sprint 0** (caixa, identidades e escopo);
> a **ingestão** de e-mail é implementada na **Sprint 6**. Decisões:
> [ADR-007](decisions/ADR-007-microsoft-365-mailbox.md) e
> [ADR-008](decisions/ADR-008-mail-polling.md). Scripts: [`infra/m365`](../infra/m365/README.md).

## 1. Recursos (Sprint 0)

| Recurso                        | Nome                                                                                   | Configuração                                                                                                                 |
| ------------------------------ | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Shared Mailbox                 | `<MVP_SHARED_MAILBOX_ALIAS>@<M365_TENANT_DOMAIN>` (sugerido `guardiao-financeiro-mvp`) | sem licença; login interativo bloqueado; `CustomAttribute1 = guardiao-financeiro-mvp`                                        |
| App Registration web           | `guardiao-financeiro-web-mvp`                                                          | single-tenant; App Roles ADMIN/ANALYST/APPROVER/AUDITOR; atribuição obrigatória; redirect do Easy Auth; sem permissões Graph |
| App Registration de e-mail     | `guardiao-financeiro-mail-mvp`                                                         | single-tenant; **nenhuma** permissão de API no Entra ID                                                                      |
| Service Principals             | um para cada App Registration                                                          | —                                                                                                                            |
| Management Scope (Exchange)    | `gfbr-mvp-mailbox-scope`                                                               | `CustomAttribute1 -eq 'guardiao-financeiro-mvp'` (exatamente 1 caixa)                                                        |
| Atribuição de papel (Exchange) | `gfbr-mvp-Mail-Read`                                                                   | `Application Mail.Read` → app de e-mail, escopo acima                                                                        |

Nenhuma credencial é criada na Sprint 0. Não se usa a caixa real do financeiro.

## 2. Menor privilégio

1. Identidades separadas: autenticação da aplicação ≠ ingestão de e-mail.
2. **Não** conceder `Mail.Read`/`Mail.ReadWrite` de aplicação no Entra ID: permissões do
   Entra e do **RBAC for Applications** são **somadas** — um consentimento amplo no Entra
   anula o escopo. Application Access Policies (legado) não são usadas.
3. Escopo do Exchange limitado à caixa do MVP; o script recusa filtros que alcancem mais
   de uma caixa.
4. Validação obrigatória:

   | Teste                                     | Esperado                            |
   | ----------------------------------------- | ----------------------------------- |
   | Caixa do MVP                              | acesso permitido (`InScope = True`) |
   | Outra caixa existente do tenant           | acesso negado (`InScope = False`)   |
   | Permissões de aplicação do Graph no Entra | nenhuma                             |

5. Credencial do app de e-mail (Sprint 6): certificado no Key Vault; nunca client secret em
   arquivo.

## 3. Execução

Passo a passo e pré-requisitos (módulo `ExchangeOnlineManagement`, papel Exchange
Administrator, Azure CLI no mesmo tenant): [`infra/m365/README.md`](../infra/m365/README.md).
Ordem: Azure (fase `apps`, para obter a URL do frontend) → `New-MvpMailbox.ps1` →
`New-AppRegistrations.ps1` → `Set-ExchangeAppRbac.ps1` → aguardar propagação (30 min a
2 h) → `Test-MailboxAccess.ps1`.

## 4. Fluxo de ingestão (Sprint 6)

- Polling periódico com _delta query_; `deltaLink` persistido por caixa/pasta.
- Para cada mensagem: `internetMessageId`, ID Graph, remetente, assunto, recebimento; para
  cada anexo: ID, nome sanitizado, tamanho, SHA-256, resultado.
- Deduplicação por mensagem e por anexo ([ADR-014](decisions/ADR-014-idempotency-dedup.md));
  retry com backoff; throttling (429) respeitando `Retry-After`; dead-letter lógico.
- Somente leitura no MVP: o sistema não move, apaga ou responde e-mails.

## 5. Remoção

Ordem segura e impactos: [`teardown-mvp.md`](teardown-mvp.md).
