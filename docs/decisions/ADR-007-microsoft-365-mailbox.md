# ADR-007 — Caixa de e-mail do MVP no Microsoft 365 com escopo mínimo

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (caixa, App Registrations e escopo) — Sprint 6 (ingestão)
- **Histórico:** evolui a decisão de ingestão via Graph com escopo mínimo aprovada no plano
  anterior (com critérios).

## Contexto

Documentos fiscais chegam por e-mail. O MVP precisa de uma caixa real desde a Sprint 0,
sem usar a caixa real do financeiro e sem que a aplicação consiga ler outras caixas da
organização.

## Decisão

- **Shared Mailbox dedicada:** `<MVP_SHARED_MAILBOX_ALIAS>@<M365_TENANT_DOMAIN>` (sugerido:
  `guardiao-financeiro-mvp`), sem licença (até 50 GB), com login interativo bloqueado e
  `CustomAttribute1 = guardiao-financeiro-mvp` como marcador de escopo.
- **Identidades separadas:** `guardiao-financeiro-web-mvp` autentica usuários
  ([ADR-006](ADR-006-authentication.md)); `guardiao-financeiro-mail-mvp` é usada somente
  pela ingestão. Cada uma com seu Service Principal.
- **Exchange Online RBAC for Applications:** Management Scope filtrado por
  `CustomAttribute1` (validado para alcançar exatamente uma caixa) e papel
  `Application Mail.Read` atribuído ao app de e-mail **somente nesse escopo**.
- **Nenhuma permissão `Mail.*` no Entra ID** para o app de e-mail: as permissões do Entra e
  do RBAC for Applications são somadas, e um consentimento no Entra valeria para todas as
  caixas. Application Access Policies (mecanismo legado) não são usadas.
- Validação obrigatória: caixa do MVP → acesso permitido; outra caixa → acesso negado
  (`Test-ServicePrincipalAuthorization`) e zero permissões de aplicação do Graph no Entra.
- **Credencial do app de e-mail:** criada somente na Sprint 6, preferencialmente
  certificado guardado no Key Vault; nunca client secret em arquivo.
- Scripts idempotentes e parametrizados em `infra/m365/` — sem tenant, domínio ou usuário
  real no repositório.
- Nenhum processamento automático de e-mail na Sprint 0.

## Alternativas consideradas

- **Caixa real do financeiro** — risco de expor dados reais durante o desenvolvimento.
- **Permissão delegada de um usuário** — acopla o sistema a uma conta humana.
- **`Mail.Read` de aplicação no Entra ID** — acesso a todas as caixas; rejeitado.
- **Application Access Policies** — mecanismo legado, substituído pelo RBAC for
  Applications.

## Consequências

- O tenant precisa de Exchange Online e de um administrador com papel Exchange
  Administrator para executar os scripts.
- A propagação do RBAC for Applications leva de 30 minutos a 2 horas.

## Riscos

- Outra caixa receber o mesmo `CustomAttribute1` ampliaria o escopo: o script de RBAC
  recusa filtros que alcancem mais de uma caixa, e o teste de escopo deve ser repetido na
  Sprint 6 e na Sprint 7.
- Tenant sem Exchange Online ou sem permissão administrativa: documentar e apresentar
  alternativa; nunca ampliar escopo silenciosamente.

## Possibilidade de revisão

Na Sprint 6 (ingestão real): papéis adicionais (ex.: mover/marcar mensagens) só com
justificativa e nova validação de escopo.
