# ADR-015 — Ingestão Microsoft 365 via Graph com escopo mínimo

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26 (com critérios)
- **Data:** 2026-09-26
- **Sprint:** 0 (implementação: Sprint 6)

## Decisão

- Leitura de **uma caixa dedicada** (ex.: `contasapagar@empresa.example`) via Microsoft
  Graph com permissão de aplicação `Mail.Read` **restrita** por **RBAC for Applications**
  do Exchange Online (Management Scope + role `Application Mail.Read`).
- A permissão `Mail.Read` **não** é concedida no Entra ID em nível de tenant: as
  permissões do Entra e do RBAC for Applications são **somadas**, então um consentimento
  amplo no Entra anularia o escopo. Application Access Policies (mecanismo legado) não são
  usadas.
- Estratégia inicial: **polling** periódico com _delta query_ por pasta, marcando
  progresso (`deltaLink`) no banco. Webhooks (subscriptions) ficam para depois.
- Registro por mensagem/anexo: message ID, remetente, assunto, recebimento, attachment ID,
  SHA-256, resultado. Deduplicação conforme ADR-011.
- Adapter `MailboxClient` com implementação `MockMailboxClient` para desenvolvimento e
  testes, sem tenant real.
- Autenticação do app preferencialmente por **certificado** (ou Managed Identity/federação
  quando suportado), guardado no Key Vault — nunca client secret em arquivo.

### Critérios do mantenedor (2026-09-26)

Polling aprovado para o MVP, priorizando simplicidade, idempotência e segurança. A
evolução para notificações/webhooks não pode exigir reescrita do domínio: a detecção de
novas mensagens fica atrás de uma interface (`MailboxChangeSource`, com implementação
`PollingChangeSource` no MVP e, no futuro, `WebhookChangeSource`) que entrega eventos ao
mesmo serviço de ingestão idempotente.

## Alternativas consideradas

- **Webhooks do Graph** — exigem endpoint público, renovação de assinaturas e validação;
  complexidade desnecessária no MVP.
- **Permissão delegada de um usuário** — acopla o sistema a uma conta humana.

## Consequências

- `docs/microsoft-365.md` documenta o passo a passo de escopo antes de qualquer uso real.
