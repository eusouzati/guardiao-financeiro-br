# ADR-013 — Prontidão para multi-tenancy via `organization_id`

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0
- **Histórico:** decisão aprovada pelo mantenedor em 2026-09-26 no plano anterior; reapresentada no plano Cloud-First.

## Contexto

O MVP opera com uma organização por implantação, mas deve permitir evolução para SaaS.

## Decisão

- Toda entidade empresarial possui `organization_id NOT NULL` com FK para `organization`.
- Repositórios recebem o `organization_id` do contexto autenticado e **sempre** filtram
  por ele; não há método de consulta sem escopo para entidades de negócio.
- Constraints de unicidade incluem `organization_id` (ex.: `(organization_id, sha256)`).
- Testes de "escopo de organização" garantem que dados de uma organização não aparecem
  para outra, mesmo com uma única organização no MVP.
- Row-Level Security do PostgreSQL fica como **evolução futura** (defesa em profundidade),
  não no MVP.

## Alternativas consideradas

- **Schema por tenant / banco por tenant** — complexidade prematura.
- **Ignorar tenant no MVP** — tornaria a migração para SaaS cara e arriscada.

## Consequências

- Pequeno custo de coluna/índice em todas as tabelas; benefício de segregação lógica
  (também exigida pela LGPD).

## Riscos

- Esquecer o filtro por `organization_id` em uma consulta expõe dados de outra
  organização (IDOR): mitigado por repositórios sem método sem escopo e testes de escopo.

## Possibilidade de revisão

Ao oferecer o produto como SaaS com várias organizações (avaliar Row-Level Security).
