# ADR-004 — Autenticação e autorização

- **Status:** Aceita
- **Data:** 2026-09-26
- **Sprint:** 0 (implementação: Sprint 1 para DEV, Sprint 7 para Entra ID)

## Contexto

Produção usa Microsoft Entra ID. O desenvolvimento local precisa funcionar sem tenant.
Perfis iniciais: `ADMIN`, `ANALYST`, `APPROVER`, `AUDITOR`. A autorização precisa ser
decidida no backend.

## Decisão

- **Produção/homologação:** OpenID Connect com Entra ID. Frontend (SPA) usa Authorization
  Code + PKCE; backend valida o access token JWT (issuer, audience, assinatura via JWKS,
  expiração) e mapeia **App Roles** do Entra para os perfis internos.
- **Autorização no backend**: dependência FastAPI por endpoint declarando a permissão
  exigida (ex.: `require(Permission.REVIEW_DECIDE)`). O frontend apenas adapta a UX.
- Matriz perfil → permissão em código versionado e testado (`app/security/`).
- Todo acesso a dados é filtrado por `organization_id` do usuário autenticado (ADR-010).
- **Autenticação DEV simulada** — protegida por quatro travas:
  1. só é considerada se `APP_ENV=local`;
  2. exige também `DEV_AUTH_ENABLED=true` (padrão `false`);
  3. em qualquer outro `APP_ENV`, `DEV_AUTH_ENABLED=true` faz a aplicação **falhar na
     inicialização** (fail-fast), não apenas ignorar;
  4. emite warning em log a cada inicialização e banner visível na UI.
- A imagem Docker de produção define `APP_ENV=production` como padrão.
- Eventos `LOGIN_SUCCESS`/`LOGIN_FAILURE` vão para a auditoria.

## Alternativas consideradas

- **Autenticação própria com senha** — aumenta superfície de ataque; rejeitado.
- **Grupos do Entra em vez de App Roles** — grupos podem vazar para o token em excesso
  (overage); App Roles são específicos da aplicação.

## Consequências

- Testes automatizados cobrem a matriz de permissões e a recusa de DEV auth fora de local.
- Documentação de registro da aplicação no Entra ID na Sprint 7.
