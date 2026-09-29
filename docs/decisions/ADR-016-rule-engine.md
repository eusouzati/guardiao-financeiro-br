# ADR-016 — Motor de regras determinístico e versionado

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (implementação: Sprint 4)
- **Histórico:** decisão aprovada pelo mantenedor em 2026-09-26 no plano anterior; reapresentada no plano Cloud-First.

## Contexto

O núcleo do produto é detectar divergências de forma explicável e reproduzível. O escopo
proíbe LLM para cálculos, comparações ou decisões e exige versionamento das regras.

## Decisão

- Regras implementadas como **classes Python puras**, sem acesso a banco ou rede. Recebem
  um `MatchingContext` imutável (documento normalizado, pedido(s), recebimento(s),
  configuração efetiva, `processed_at`) e devolvem `RuleResult`.
- Cada regra declara: `code` (ex.: `DUPLICATE_EXACT`), `version` (SemVer),
  título, descrição e severidade padrão.
- `RuleResult` contém: id, código, título, descrição, resultado
  (`PASSED | FAILED | NOT_APPLICABLE | ERROR`), severidade (`INFO | WARNING | CRITICAL`),
  dados encontrados (valores comparados), explicação em pt-BR, timestamp, versão da regra.
- Um **ruleset** agrupa regras e tem versão própria (`ruleset_version`, SemVer). Cada
  `MatchingRun` grava a versão do ruleset e um **snapshot da configuração** usada
  (tolerâncias, janelas, políticas).
- Status do three-way match derivado **deterministicamente** dos resultados (sem score
  opaco): qualquer `CRITICAL` falho → `BLOCKED` ou `NEEDS_REVIEW` conforme tabela
  documentada em `docs/matching-engine.md`.
- Regra que lança erro gera `ERROR` explícito e força `NEEDS_REVIEW` — nunca é ignorada.
- Cada regra tem testes unitários independentes.

## Alternativas consideradas

- **Motor genérico (Drools/json-rules-engine/DSL)** — flexível, porém opaco, difícil de
  testar e desnecessário para 13 regras; rejeitado no MVP.
- **Score ponderado** — contraria o requisito de explicabilidade; rejeitado.

## Consequências

- Alterar comportamento de regra exige bump de versão da regra e do ruleset.
- Execuções antigas permanecem explicáveis pelo snapshot gravado.

## Riscos

- Regras mal calibradas geram excesso de exceções: tolerâncias configuráveis e
  versionadas por organização.

## Possibilidade de revisão

Quando uma regra precisar de dados externos ou de aprendizado estatístico (sempre
explicável e sem substituir as regras determinísticas).
