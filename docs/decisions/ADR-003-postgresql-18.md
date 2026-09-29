# ADR-003 — PostgreSQL 18 como banco de metadados

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0
- **Histórico:** decisão equivalente aprovada pelo mantenedor em 2026-09-26 no plano anterior; reapresentada no plano Cloud-First.

## Contexto

Precisamos de banco relacional com transações fortes, tipo `NUMERIC` exato, constraints,
bloqueios e bom suporte gerenciado no Azure (Azure Database for PostgreSQL Flexible Server).

## Decisão

- **PostgreSQL 18** no MVP (Azure Database for PostgreSQL Flexible Server, versão 18 em
  GA) e no ambiente local (imagem `postgres:18.6-alpine3.24`). Mesma major nos dois.
- Database da aplicação no MVP: **`guardiao_financeiro`**.
- MVP: SKU econômica (Burstable `Standard_B1ms`, 32 GB), **sem alta disponibilidade**,
  backup automático com retenção de 7 dias, TLS obrigatório, rede conforme
  [ADR-011](ADR-011-mvp-networking.md).
- Autenticação Microsoft Entra habilitada no servidor. Para o bootstrap, a aplicação usa
  a credencial administrativa gerada pelo script de deploy e guardada **somente** no Key
  Vault (lida pelo Container Apps via identidade gerenciada). **Débito técnico:** migrar a
  aplicação para identidade gerenciada com usuário de menor privilégio (Sprint 1/7).
- Migrations exclusivamente via **Alembic**; nada de `create_all()` fora de testes.
- Valores monetários em `NUMERIC` (ver ADR-009). Timestamps em `timestamptz`,
  sempre gravados em **UTC**.
- Chaves primárias **UUID** geradas pela aplicação (evita enumeração e facilita
  idempotência e futura federação).
- Documentos binários **não** ficam no banco (ADR-005); o banco guarda metadados e SHA-256.
- Driver: **psycopg 3**, com SQLAlchemy 2 síncrono ([ADR-020](ADR-020-backend-foundations.md)).

## Alternativas consideradas

- **PostgreSQL 17** — mais tempo de mercado; porém 18 já é GA no Azure e evita upgrade
  major logo após o MVP. Algumas extensões ainda não têm suporte no 18 no
  Azure; o projeto não depende de extensões além das nativas.
- **SQL Server / Azure SQL** — bom encaixe Microsoft, mas custo maior e menos comum em
  projetos open source Python.
- **SQLite para desenvolvimento** — divergência de comportamento (NUMERIC, locks);
  rejeitado: o ambiente local usa PostgreSQL via Docker.

## Consequências

- Imagem local fixada por tag de minor; fixação por digest na Sprint 9.
- Testes de integração rodam contra PostgreSQL real (container), não SQLite.
- Se alguma extensão necessária não existir no PG 18 do Azure, reavaliar via nova ADR.

## Riscos

- Credencial administrativa usada pela aplicação no bootstrap (privilégio maior que o
  necessário): mitigado por segredo só no Key Vault, rede privada e débito registrado.
- SKU Burstable pode esgotar créditos de CPU sob carga contínua: monitorado no Azure
  Monitor; troca de SKU é parâmetro (`sku.postgres`).
- Assinaturas de avaliação podem ter restrição de SKU/região para PostgreSQL: o `what-if`
  e o deploy revelam; nenhuma troca de região é feita sem autorização.

## Possibilidade de revisão

- Se uma extensão necessária não existir no PG 18 do Azure, ou se o volume exigir outra
  SKU/HA (decisão da Sprint 8).
