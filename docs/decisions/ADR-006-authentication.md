# ADR-006 — Autenticação e autorização

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (App Registration) — Sprint 1 (autenticação base Entra) — Sprint 7 (completa)
- **Histórico:** consolida a decisão de autenticação do plano anterior e o modelo Easy Auth
  - App Roles escolhido pelo mantenedor em 2026-09-26.

## Contexto

O MVP roda na internet desde a Sprint 0. A identidade oficial é o Microsoft Entra ID, com
os perfis `ADMIN`, `ANALYST`, `APPROVER` e `AUDITOR`. A autorização precisa acontecer no
backend: o frontend não é mecanismo de segurança. O desenvolvimento local precisa
funcionar sem tenant.

## Decisão

- **App Registration `guardiao-financeiro-web-mvp`** (Sprint 0): single-tenant, App Roles
  `ADMIN`/`ANALYST`/`APPROVER`/`AUDITOR`, atribuição obrigatória de usuário no Service
  Principal e nenhuma permissão do Microsoft Graph além do necessário ao login.
- **Autenticação base (Sprint 1):** autenticação integrada do Azure Container Apps
  (**Easy Auth**) no frontend, com o registro acima. O sidecar remove cabeçalhos `X-MS-*`
  enviados pelo cliente e injeta `X-MS-CLIENT-PRINCIPAL`; o Nginx o repassa à API, que
  **não tem ingress externo**. O backend só confia nesse cabeçalho com
  `EASY_AUTH_ENABLED=true`, que:
  - só é aceito com `APP_ENV=mvp` (a aplicação não inicia em `local`/`test`);
  - é mutuamente exclusivo com a autenticação DEV;
  - exige `ENTRA_TENANT_ID` e rejeita principal de outro tenant, malformado ou maior que
    16 KB (401). Usuário sem App Role não recebe permissões (403).
    O suporte no backend e no frontend já está implementado e testado; a Sprint 0 não o
    ativa no ambiente.
- **Autenticação completa (Sprint 7):** validação de access token JWT (issuer, audience,
  assinatura via JWKS, expiração) com as mesmas App Roles.
- **Autorização sempre no backend:** dependência por endpoint declarando a permissão
  (`require(Permission.X)`), matriz perfil → permissão versionada e testada
  (`app/security/permissions.py`), e todo acesso filtrado por `organization_id`
  ([ADR-013](ADR-013-multitenancy.md)). Cadeia: autenticado? → permissão? → pertence à
  organização? → pode executar a operação?
- **Autenticação DEV simulada** (somente máquina local), com quatro travas:
  1. só é considerada com `APP_ENV=local`;
  2. exige `DEV_AUTH_ENABLED=true` (padrão `false`);
  3. em qualquer outro `APP_ENV`, `DEV_AUTH_ENABLED=true` faz a aplicação **falhar na
     inicialização**;
  4. warning em log e banner visível na UI.
- A imagem Docker define `APP_ENV=mvp` como padrão: fora do Compose local, a autenticação
  DEV é impossível.
- **Sprint 0 no MVP:** sem autenticação ativa, toda rota que não seja health check responde
  **401**; só a página pública `/status` e as sondas `/health`/`/ready` respondem.

## Alternativas consideradas

- **Autenticação própria com senha** — aumenta a superfície de ataque; rejeitada.
- **Grupos do Entra em vez de App Roles** — risco de overage no token; App Roles são
  específicos da aplicação.
- **MSAL + JWT já na Sprint 1** — mais trabalho no frontend antes de haver funcionalidade;
  fica para a Sprint 7, preservando as App Roles.

## Consequências

- Testes cobrem a matriz de permissões, a recusa da autenticação DEV fora de `local` e a
  leitura/rejeição do principal do Easy Auth.
- O segredo de cliente do Easy Auth (Sprint 1) terá validade curta, ficará só no Key Vault
  e será lido por referência pela identidade gerenciada.

## Riscos

- A confiança no cabeçalho do Easy Auth depende de a API continuar **sem ingress
  externo**; mudar isso exige desligar `EASY_AUTH_ENABLED` ou adotar JWT.
- Segredo de cliente do Easy Auth expira: rotação documentada na Sprint 1; avaliar
  credencial federada quando suportada.

## Possibilidade de revisão

Na Sprint 7, ao implementar a validação JWT completa, ou se o Container Apps passar a
suportar credencial federada para o Easy Auth.
