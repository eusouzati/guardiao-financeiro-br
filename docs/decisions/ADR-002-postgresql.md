# ADR-002 — PostgreSQL como banco de metadados

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26
- **Data:** 2026-09-26
- **Sprint:** 0

## Contexto

Precisamos de banco relacional com transações fortes, tipo `NUMERIC` exato, constraints,
bloqueios e bom suporte gerenciado no Azure (Azure Database for PostgreSQL Flexible Server).

## Decisão

- **PostgreSQL 18** localmente (imagem `postgres:18.6-alpine3.24`) e no Azure Flexible
  Server, que oferece a versão 18 em GA. Manter a mesma major em todos os ambientes.
- Migrations exclusivamente via **Alembic**; nada de `create_all()` fora de testes.
- Valores monetários em `NUMERIC` (ver ADR-007). Timestamps em `timestamptz`,
  sempre gravados em **UTC**.
- Chaves primárias **UUID** geradas pela aplicação (evita enumeração e facilita
  idempotência e futura federação).
- Documentos binários **não** ficam no banco (ADR-003); o banco guarda metadados e SHA-256.
- Driver: **psycopg 3** (definição final na Sprint 1).

### Aprovação

PostgreSQL 18 aprovado pelo mantenedor (2026-09-26): é suportado em GA pelo Azure Database
for PostgreSQL Flexible Server, inclusive para produção.

## Alternativas consideradas

- **PostgreSQL 17** — mais tempo de mercado; porém 18 já é GA no Azure e evita upgrade
  major logo após o lançamento do MVP. Algumas extensões ainda não têm suporte no 18 no
  Azure; o projeto não depende de extensões além das nativas.
- **SQL Server / Azure SQL** — bom encaixe Microsoft, mas custo maior e menos comum em
  projetos open source Python.
- **SQLite para desenvolvimento** — divergência de comportamento (NUMERIC, locks);
  rejeitado: o ambiente local usa PostgreSQL via Docker.

## Consequências

- Imagem local fixada por tag de minor; fixação por digest na Sprint 9.
- Testes de integração rodam contra PostgreSQL real (container), não SQLite.
- Se alguma extensão necessária não existir no PG 18 do Azure, reavaliar via nova ADR.
