# ADR-019 — Infraestrutura como código com Bicep

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (Azure e Microsoft 365) — Sprint 9 (CI/CD com OIDC)
- **Histórico:** Bicep e OIDC aprovados no plano anterior; estrutura e parâmetros
  revistos para o ambiente único MVP.

## Contexto

O MVP precisa ser reproduzível: a Sprint 0 só termina quando o ambiente pode ser
compreendido e recriado sem configurações manuais não documentadas. Microsoft 365 não é
coberto por Bicep.

## Decisão

- Azure somente por **Bicep** em `infra/azure/` (`main.bicep` em escopo de assinatura,
  `parameters/mvp.bicepparam` e módulos `network`, `identities`,
  `container-apps-environment`, `container-apps`, `registry`, `postgres`, `storage`,
  `keyvault`, `monitoring`, `cost-management`).
- Parâmetros genéricos (`environment`, `location`, `resourcePrefix`, `tags`, `sku`); nenhum
  arquivo de outro ambiente. Região parametrizada (padrão `brazilsouth`, confirmada pelo
  responsável).
- Valores dinâmicos e sensíveis chegam ao `.bicepparam` por variáveis de ambiente da
  sessão definidas pelo script de deploy; nada sensível é versionado.
- Validação obrigatória antes de criar: `bicep build`/lint e
  `az deployment sub what-if`; criação somente com autorização explícita.
- Deploy em duas fases (`scripts/azure/deploy-mvp.ps1`): **base** (fundação) e **apps**
  (imagens no ACR + aplicações + job de migração). O script confirma assinatura, tenant e
  usuário e **para** se divergirem.
- Microsoft 365 por **scripts PowerShell idempotentes** em `infra/m365/` (Exchange Online
  PowerShell + Azure CLI), parametrizados, sem tenant/domínio real, sem apagar nada.
- **Sprint 9:** GitHub Actions autentica no Azure por **OpenID Connect** (federated
  credentials), sem client secret de longa duração; actions fixadas por SHA e permissões
  mínimas por job.

## Alternativas consideradas

- **Terraform** — multi-cloud desnecessário e state file a proteger.
- **Portal/cliques manuais** — não reproduzível.
- **Service Principal com secret no CI** — credencial de longa duração; rejeitado.

## Consequências

- Todo recurso novo entra primeiro no Bicep (ou em script M365) e na documentação.
- O `what-if` é evidência obrigatória antes de cada deploy.

## Riscos

- Drift por alteração manual no portal: `what-if` antes de cada deploy revela diferenças;
  alterações manuais emergenciais devem voltar para o código.
- Scripts M365 dependem de módulos e permissões do administrador: pré-requisitos
  verificados pelo script, sem instalação silenciosa.

## Possibilidade de revisão

Se o projeto passar a gerenciar recursos fora do Azure, ou quando surgir provedor IaC
oficial para a configuração do Exchange Online usada aqui.
