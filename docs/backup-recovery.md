# Backup e recuperação

> Documento inicial (Sprint 0). Procedimentos testados serão adicionados na Sprint 8.
> **Redundância do provedor não é backup.**

## 1. O que precisa ser protegido

| Ativo                                             | Onde                         | Criticidade |
| ------------------------------------------------- | ---------------------------- | ----------- |
| Metadados, regras executadas, decisões, auditoria | PostgreSQL                   | Alta        |
| Arquivos originais (XML/PDF/CSV/XLSX)             | Blob Storage / storage local | Alta        |
| Configurações por empresa                         | PostgreSQL                   | Média       |
| Segredos/certificados                             | Key Vault                    | Alta        |
| Infraestrutura                                    | Bicep no Git                 | Recriável   |

## 2. Estratégia proposta

**PostgreSQL (Azure Flexible Server)**

- Backups automáticos com PITR; retenção sugerida de 14 dias (hml) e 35 dias (prod).
- Backup geo-redundante em produção quando o custo for aprovado.
- `pg_dump` lógico periódico (ex.: semanal) para storage separado com imutabilidade, como
  segunda linha de defesa contra erro lógico ou exclusão da instância.

**Blob Storage**

- Soft delete de blobs e containers, versionamento e proteção contra exclusão de conta
  (resource lock).
- Considerar política de imutabilidade para documentos originais, alinhada à retenção.

**Key Vault**

- Soft delete e purge protection habilitados.

**Local (desenvolvimento)**

- Dados locais são descartáveis e fictícios; volume Docker `db-data`.

## 3. Objetivos iniciais sugeridos

| Ambiente    | RPO             | RTO          |
| ----------- | --------------- | ------------ |
| Produção    | ≤ 15 min (PITR) | ≤ 4 h        |
| Homologação | ≤ 24 h          | ≤ 1 dia útil |

Valores a validar com cada organização e com o custo aprovado.

## 4. Procedimento de restauração (esboço)

1. Declarar incidente e congelar ingestão (desabilitar worker/ingestão de e-mail).
2. Restaurar PostgreSQL por PITR para nova instância; validar integridade (contagens,
   última `audit_event`).
3. Verificar blobs referenciados por `attachment.storage_key` e seus SHA-256.
4. Reapontar a aplicação (parâmetro/segredo) para a instância restaurada.
5. Reativar worker; reprocessar jobs pendentes (idempotentes — ADR-011).
6. Registrar o evento e lições aprendidas.

## 5. Limitações do MVP

- Sem testes automatizados de restauração até a Sprint 8.
- Sem DR multirregião ativo.
- Exclusões LGPD só se propagam aos backups quando estes expiram — documentar para o controlador.
