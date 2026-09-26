# ADR-017 — Antecipar um ambiente `dev` no Azure (Sprint 1A)

- **Status:** Aceita (decisão do mantenedor em 2026-09-26)
- **Data:** 2026-09-26
- **Sprint:** 0 (execução: Sprint 1A, logo após a Sprint 1)

## Contexto

O plano original previa toda a infraestrutura Azure somente na Sprint 8, com
desenvolvimento 100% local até lá. O mantenedor quer ver o sistema rodando no Azure desde
cedo. A seção 58 do escopo continua valendo: o projeto deve funcionar localmente sem Azure.

## Decisão

- Criar a **Sprint 1A — Azure Dev Environment**, entre as Sprints 1 e 2, antecipando
  parcialmente a Sprint 8 **apenas para o ambiente `dev`**.
- Desenvolvimento e testes continuam **locais** (Docker Compose); o Azure `dev` recebe a
  aplicação por deploy explícito.
- Escopo da Sprint 1A:
  - Bicep modular (`infra/main.bicep` + `modules/`) com parâmetros `dev`
    (`hml`/`prod` continuam na Sprint 8): Container Apps environment + apps, Container
    Registry, PostgreSQL Flexible Server (SKU mínimo), Storage Account, Key Vault,
    Log Analytics + Application Insights, Managed Identities.
  - `az bicep build`, `validate` e `what-if` **antes** de qualquer criação.
  - Estimativa de custo mensal e lista do que pode ser desligado/parado.
  - Deploy executado pelo mantenedor (ou por Claude com a CLI dele) **somente após
    autorização explícita** do custo e do what-if.
  - Procedimento para destruir o ambiente (`az group delete`) documentado.
- **Segurança do `dev` público antes da Sprint 7 (Entra ID):** a autenticação DEV
  simulada continua proibida fora de `APP_ENV=local`. Portanto o `dev` no Azure precisa de
  uma barreira na borda — opção a decidir no início da Sprint 1A, com preferência pela mais
  simples e segura:
  1. restrição de ingress do Container Apps por IP do mantenedor; ou
  2. autenticação integrada do Container Apps (Easy Auth) com Entra ID limitada ao tenant/
     usuário do mantenedor (cria app registration — exige autorização).
- Somente dados fictícios no `dev` do Azure.
- GitHub Actions/OIDC continuam na Sprint 9; na Sprint 1A o deploy é manual via CLI.

## Alternativas consideradas

- **Manter o plano original (Azure só na Sprint 8)** — zero custo, mas o mantenedor não
  veria a solução na nuvem por várias sprints.
- **Desenvolver direto no Azure, sem ambiente local** — custo contínuo, credenciais desde
  o início, ciclo de teste lento e contraria a seção 58; rejeitado.

## Atualização (2026-09-26)

A assinatura disponível para o `dev` é **Free Trial**, região `brazilsouth`, com o
mantenedor como Owner. Consequências adicionais: SKUs mínimos obrigatórios, ambiente pode
ser desativado ao fim do crédito se não houver migração para pay-as-you-go, e o Bicep deve
permitir recriar o ambiente em outra assinatura apenas trocando parâmetros. Detalhes em
`docs/deployment-azure.md` §2.1–2.2.

Decisões do mantenedor (2026-09-26):

- **Uso limitado ao período do trial:** não haverá migração para pay-as-you-go. O `dev`
  no Azure é temporário; quando a assinatura for desativada, o ambiente é recriado em outra
  assinatura trocando parâmetros do Bicep. Nenhum dado relevante vive só no Azure (apenas
  dados fictícios).
- **Barreira de acesso:** autenticação integrada do Container Apps (**Easy Auth**) com
  Entra ID, restrita ao tenant do mantenedor, até a Sprint 7. Exige um app registration
  (gratuito), criado somente com autorização no início da Sprint 1A.

## Consequências

- Custo de nuvem passa a existir a partir da Sprint 1A (baixo, estimado antes).
- A Sprint 8 passa a cobrir `hml`/`prod`, endurecimento de rede, backup testado e revisão
  de custos — reaproveitando os módulos Bicep da 1A.
- Substitui parcialmente a consequência da ADR-014 "nenhum recurso Azure antes da
  Sprint 8".
