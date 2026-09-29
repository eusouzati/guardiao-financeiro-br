# ADR-005 — Armazenamento de documentos em Azure Blob Storage

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (recursos) — uso pela aplicação a partir da Sprint 2
- **Histórico:** abstração de armazenamento aprovada no plano anterior; destino oficial
  atualizado para o Blob Storage do MVP.

## Contexto

Documentos originais (XML, PDF, CSV, XLSX) precisam ser guardados com integridade,
deduplicação e trilha de auditoria. No plano Cloud-First, o armazenamento oficial é o
Azure Blob Storage do MVP; arquivo local não é storage oficial.

## Decisão

- Uma Storage Account **Standard LRS** no MVP, com **HTTPS obrigatório**, **TLS 1.2+**,
  **acesso público a blobs desabilitado**, **chave compartilhada desabilitada** (acesso só
  por Entra ID/RBAC), versionamento de blobs e soft delete de blobs e containers (7 dias).
- Containers privados:

| Container           | Conteúdo                                                     |
| ------------------- | ------------------------------------------------------------ |
| `documents-raw`     | documentos originais recebidos (upload ou e-mail), imutáveis |
| `documents-derived` | artefatos derivados (ex.: texto extraído, representações)    |
| `imports`           | arquivos de importação (CSV/XLSX de pedidos e recebimentos)  |
| `exports`           | relatórios gerados para download                             |

- Acesso pela identidade gerenciada da API (`Storage Blob Data Contributor` na conta).
- Interface `DocumentStorage` (porta) com implementações `AzureBlobStorage` (MVP) e
  `LocalFileStorage` (somente testes e desenvolvimento local).
- **SHA-256 calculado em streaming** antes da persistência — integridade, deduplicação
  ([ADR-014](ADR-014-idempotency-dedup.md)) e auditoria.
- Chave de armazenamento **gerada pelo sistema**, nunca derivada do nome enviado:
  `{organization_id}/{sha256[0:2]}/{sha256}`. O nome original é metadado sanitizado —
  elimina path traversal por construção.
- O banco guarda apenas metadados (chave, hash, tamanho, MIME detectado, nome sanitizado,
  origem); documentos binários nunca vão para o PostgreSQL nem para logs.

## Alternativas consideradas

- **BYTEA no PostgreSQL** — incha banco e backup; rejeitado.
- **Private Endpoint para o Storage** — custo mensal e DNS adicional sem necessidade no
  MVP, já que o acesso exige Entra ID/RBAC (ver [ADR-011](ADR-011-mvp-networking.md)).
- **Chave por nome de arquivo** — risco de colisão e traversal; rejeitado.

## Consequências

- Todo acesso a arquivo passa pela interface; nenhum módulo usa caminho de disco direto.
- Remoção de blobs só por política de retenção documentada; nunca automática sem
  autorização ([`teardown-mvp.md`](../teardown-mvp.md)).

## Riscos

- Endpoint público do Storage (plano de dados exige token Entra; sem chave nem acesso
  anônimo). Revisar restrição de rede na Sprint 8.
- Versionamento aumenta o volume armazenado: acompanhar em `cost-management.md` e criar
  política de ciclo de vida quando houver volume.

## Possibilidade de revisão

Na Sprint 8 (hardening): restrição de rede do Storage, imutabilidade (WORM) para
documentos fiscais e política de ciclo de vida.
