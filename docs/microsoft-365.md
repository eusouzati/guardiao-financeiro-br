# Integração Microsoft 365

> **Status: planejado (Sprint 6).** Nenhum recurso Microsoft 365/Entra é criado na
> Sprint 0. Desenvolvimento usa `MAILBOX_INGESTION_MODE=mock` (ADR-015).

## 1. Objetivo

Ler mensagens de **uma caixa dedicada** (ex.: `contasapagar@empresa.example`), identificar
anexos compatíveis (XML, PDF) e ingeri-los com deduplicação e rastreabilidade.

## 2. Menor privilégio — modelo recomendado

1. Registrar app no Entra ID para ingestão (separado do app da SPA/API).
2. **Não** conceder `Mail.Read` de aplicação com consentimento de tenant no Entra.
3. No Exchange Online, usar **RBAC for Applications**:
   - criar _management scope_ que inclua apenas a(s) caixa(s) autorizada(s);
   - atribuir a role `Application Mail.Read` ao service principal com esse escopo
     (`New-ManagementRoleAssignment -App … -Role "Application Mail.Read" -CustomResourceScope …`).
4. Testar o escopo (`Test-ServicePrincipalAuthorization`) com uma caixa autorizada e uma
   não autorizada.
5. Credencial do app: certificado no Key Vault (ou federação/Managed Identity quando
   suportado). Nunca client secret em arquivo.

> Permissões concedidas no Entra ID e no RBAC for Applications são **somadas**: um
> `Mail.Read` amplo no Entra anula o escopo. Application Access Policies (mecanismo
> legado) foram substituídas pelo RBAC for Applications e não serão usadas.

## 3. Fluxo previsto

- Polling periódico com _delta query_ por pasta; `deltaLink` persistido.
- Para cada mensagem: registrar `internetMessageId`, ID Graph, remetente, assunto,
  recebimento; para cada anexo: ID, nome sanitizado, tamanho, SHA-256, resultado.
- Deduplicação por mensagem e por anexo (ADR-011); retry com backoff; throttling (429)
  respeitando `Retry-After`.
- Sistema **não** move, apaga ou responde e-mails no MVP (somente leitura).

## 4. A documentar na Sprint 6

Passo a passo com prints/comandos, checklist de validação de escopo, troubleshooting.
