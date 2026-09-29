# Teardown do MVP

> **Nunca executado automaticamente.** Cada passo destrutivo abaixo exige autorização
> explícita do responsável pelo projeto, dada para aquela execução. Nenhum script do
> repositório remove recursos.

## 1. Recursos existentes

| Onde            | Recurso                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Azure           | Grupo `rg-gfbr-mvp` com todos os recursos do MVP (tabela em [`deployment-azure.md`](deployment-azure.md) §3)               |
| Azure           | Grupo gerenciado `rg-gfbr-mvp-cae-infra` (criado e removido pela plataforma junto com o ambiente do Container Apps)        |
| Azure           | Orçamento `budget-gfbr-mvp` (dentro do grupo de recursos)                                                                  |
| Microsoft Entra | `guardiao-financeiro-web-mvp` e `guardiao-financeiro-mail-mvp` (App Registrations e Service Principals)                    |
| Exchange Online | Shared Mailbox do MVP, Management Scope `gfbr-mvp-mailbox-scope`, atribuição de papel e service principal do app de e-mail |
| Local           | `.azure/mvp.json` e `.azure/m365-mvp.json` (sem segredos)                                                                  |

## 2. O que se perde

- **PostgreSQL:** todos os dados **e os backups automáticos** (são excluídos junto com o
  servidor). Se os dados importarem, faça antes um `pg_dump` por um job na VNet ou uma
  restauração para outro servidor.
- **Blob Storage:** todos os documentos, versões e itens em soft delete (a conta excluída
  pode ser recuperável por tempo limitado, sem garantia).
- **Key Vault:** entra em soft delete por 7 dias; com **purge protection**, não pode ser
  purgado nesse período — o nome fica reservado e um novo deploy na mesma assinatura
  precisa esperar o prazo ou recuperar o vault (`az keyvault recover`).
- **Shared Mailbox:** mensagens da caixa (retenção de itens excluídos do Exchange conforme
  a política do tenant).

## 3. Ordem segura de remoção

1. **Congelar o uso:** avisar usuários; parar ingestão/worker (quando existirem).
2. **Exportar o que precisa ser mantido:** dump do banco, documentos do Blob, evidências
   de auditoria. Confirmar que nenhum dado real ficará sem cópia exigida por lei.
3. **Microsoft 365 — remover o acesso antes de remover a identidade** (Exchange Online
   PowerShell):
   ```powershell
   Get-ManagementRoleAssignment -RoleAssignee <mailAppId> | Remove-ManagementRoleAssignment
   Remove-ManagementScope -Identity gfbr-mvp-mailbox-scope
   Remove-ServicePrincipal -Identity <mailAppId>
   ```
4. **Entra ID:**
   ```powershell
   az ad app delete --id <mailAppId>
   az ad app delete --id <webAppId>
   ```
   (Exclui também os Service Principals; ficam 30 dias na lixeira do Entra.)
5. **Shared Mailbox:** `Remove-Mailbox -Identity <alias>@<dominio>` (recuperável por 30 dias
   como caixa excluída, conforme o tenant).
6. **Azure:**
   ```powershell
   az group delete --name rg-gfbr-mvp          # pede confirmação; remove tudo do grupo
   ```
   Aguarde a remoção do grupo gerenciado `rg-gfbr-mvp-cae-infra` (automática).
7. **Key Vault:** permanece em soft delete por 7 dias; não é possível purgar (purge
   protection). Nenhuma ação necessária.
8. **Local:** remover `.azure/mvp.json` e `.azure/m365-mvp.json`.
9. Registrar em `docs/sprint-0/` (ou no relatório da sprint) data, responsável e
   motivo.

## 4. Remoção parcial para economizar

Em vez de remover, é possível **parar o PostgreSQL** e deixar os Container Apps escalarem
a zero ([`cost-management.md`](cost-management.md) §3). O ACR Basic continua com custo
diário baixo.
