# Backup e restauração do MVP

> Escopo: o único ambiente, **MVP**. Não é uma política empresarial de disaster recovery;
> o objetivo é recuperação coerente do MVP. Restauração testada: Sprint 8.
> **Redundância do provedor não é backup.**

## 1. O que precisa ser protegido

| Ativo                                             | Onde                             | Criticidade | Proteção no MVP                                               |
| ------------------------------------------------- | -------------------------------- | ----------- | ------------------------------------------------------------- |
| Metadados, regras executadas, decisões, auditoria | PostgreSQL `guardiao_financeiro` | Alta        | Backup automático com PITR, retenção 7 dias                   |
| Documentos originais e derivados                  | Blob Storage                     | Alta        | Versionamento + soft delete de blobs e containers (7 dias)    |
| Segredos                                          | Key Vault                        | Alta        | Soft delete (7 dias) + purge protection                       |
| Infraestrutura                                    | Bicep e scripts no Git           | Recriável   | `infra/azure`, `infra/m365`                                   |
| Caixa de e-mail do MVP                            | Exchange Online                  | Média       | Retenção padrão do Exchange; documentos extraídos vão ao Blob |

## 2. PostgreSQL

- Backup automático do Azure Database for PostgreSQL Flexible Server com restauração
  pontual (PITR) dentro da janela de **7 dias** (parâmetro `sku.postgres.backupRetentionDays`,
  até 35). Backup local à região (sem geo-redundância no MVP).
- O backup é **removido junto com o servidor** se o servidor for excluído: por isso a
  exclusão nunca é automática ([`teardown-mvp.md`](teardown-mvp.md)).
- Segunda linha de defesa (`pg_dump` lógico periódico para storage imutável): avaliada na
  Sprint 8.

## 3. Blob Storage

- Versionamento de blobs: sobrescrita preserva a versão anterior.
- Soft delete de blobs e de containers por 7 dias.
- `documents-raw` é tratado como imutável pela aplicação (Sprint 2). Política de
  imutabilidade (WORM) e ciclo de vida: Sprint 8.

## 4. Objetivos do MVP

| Objetivo | Valor        | Base                                                     |
| -------- | ------------ | -------------------------------------------------------- |
| RPO      | ≤ 15 minutos | PITR do PostgreSQL; blobs versionados                    |
| RTO      | ≤ 4 horas    | Restauração para novo servidor + reapontamento via Bicep |

Metas do MVP, sem compromisso contratual; revisar quando houver dados reais.

## 5. Procedimento de restauração (PostgreSQL)

1. Declarar incidente; pausar ingestão/worker (quando existirem).
2. Restaurar por PITR para **novo** servidor na mesma VNet:
   `az postgres flexible-server restore -g rg-gfbr-mvp -n <novo-servidor> --source-server <servidor> --restore-time <UTC>`.
3. Validar integridade (contagens, último `audit_event`, `alembic_version`).
4. Conferir que os blobs referenciados existem e que o SHA-256 confere.
5. Reapontar a aplicação para o servidor restaurado (parâmetro do Bicep/variável
   `POSTGRES_HOST`) e publicar com `deploy-mvp.ps1 -Phase apps`.
6. Reativar o processamento; jobs são idempotentes ([ADR-014](decisions/ADR-014-idempotency-dedup.md)).
7. Registrar o evento e as lições aprendidas. O servidor antigo só é removido com
   autorização explícita.

## 6. Restauração de blob

- Excluído há menos de 7 dias: `az storage blob undelete` (ou portal) no container.
- Sobrescrito: promover a versão anterior (`az storage blob copy start` da versão).

## 7. Limitações

- Restauração ainda não testada (Sprint 8).
- Sem DR multirregião.
- Exclusões por LGPD só se propagam aos backups quando estes expiram — documentar para o
  controlador.
