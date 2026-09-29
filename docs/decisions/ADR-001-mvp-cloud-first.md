# ADR-001 — MVP Cloud-First com um único ambiente

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0
- **Substitui:** a decisão anterior de desenvolvimento local-first com ambiente `dev`
  antecipado (plano anterior, não implantado).

## Contexto

O Guardião Financeiro BR precisa ser validado em infraestrutura real desde o início:
Azure (aplicação, banco, documentos, segredos, observabilidade) e Microsoft 365 (caixa de
e-mail de entrada de documentos). O plano anterior previa desenvolvimento local e recursos
Azure somente em sprints finais, com ambientes `dev`/`hml`/`prod`; ele foi substituído pelo
plano consolidado Cloud-First. Nenhum recurso do plano anterior chegou a ser criado.

## Decisão

- Existe **um único ambiente de nuvem: `mvp`**, criado na Sprint 0 com recursos reais do
  Azure e do Microsoft 365.
- **Não** são criados ambientes de homologação, produção, pré-produção ou equivalentes —
  nem arquivos, pipelines, parâmetros, enums, ADRs ou recursos para eles.
- A infraestrutura aceita parâmetros genéricos (`environment`, `location`,
  `resourcePrefix`, `tags`, `sku`), para que outro ambiente possa ser avaliado no futuro sem
  reescrever módulos. Hoje `environment` aceita somente `mvp`; ampliar a lista é decisão
  explícita do responsável pelo projeto.
- A aplicação conhece três valores de `APP_ENV`: `local` e `test` (máquina do
  desenvolvedor e testes automatizados) e `mvp` (nuvem).
- O computador local continua sendo usado para código, testes unitários, lint, type
  checking, build de containers, Azure CLI, PowerShell e Bicep — mas **não** é a fonte
  oficial de banco, documentos, segredos, caixa de e-mail, autenticação ou ambiente
  integrado. Uma funcionalidade que dependa da nuvem só está pronta quando validada no MVP.
- Nenhum recurso é criado sem `what-if`, estimativa de custo e a autorização
  **"AUTORIZAR DEPLOY MVP DA SPRINT 0"** do responsável.

## Alternativas consideradas

- **Local-first com Azure só no fim** — sem custo inicial, mas adia a validação de rede,
  identidade, e-mail e custos reais para o fim do projeto.
- **Vários ambientes desde o início (dev/hml/prod)** — multiplica custo e manutenção sem
  necessidade real neste estágio.

## Consequências

- Custo de nuvem contínuo desde a Sprint 0 (baixo, estimado em
  [`cost-management.md`](../cost-management.md)).
- Toda sprint termina com deploy e validação no MVP ([`roadmap.md`](../roadmap.md)).
- O Docker Compose local permanece como ferramenta de desenvolvimento, não como ambiente
  oficial.
- O trabalho já feito (backend, frontend, testes e ADRs) é aproveitado; o código de
  bootstrap da Sprint 0 é a própria base existente, sem regras de negócio.

## Riscos

- **Um único ambiente recebe mudanças direto:** mitigado por testes locais, `what-if`,
  migrations reversíveis, backups do PostgreSQL e soft delete de blobs; mudanças
  destrutivas exigem autorização explícita.
- **Dados reais no MVP:** o MVP usa somente dados fictícios até decisão em contrário
  (política em [`synthetic-data-policy.md`](../synthetic-data-policy.md)).
- **Assinatura de avaliação (Free Trial):** pode ser desativada ao fim do crédito. O
  responsável decide a assinatura antes do deploy; o Bicep permite recriar tudo em outra
  assinatura trocando parâmetros.

## Possibilidade de revisão

Reavaliar quando houver usuários reais, dados reais ou exigência de janela de
homologação. Um novo ambiente só é criado por nova ADR aprovada pelo responsável.
