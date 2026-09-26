# ADR-003 — Abstração de armazenamento de documentos

- **Status:** Aceita
- **Data:** 2026-09-26
- **Sprint:** 0

## Contexto

Documentos originais (XML, PDF, CSV, XLSX) precisam ser guardados com integridade,
deduplicados e auditáveis. Produção usará Azure Blob Storage; desenvolvimento não deve
depender do Azure.

## Decisão

- Interface `DocumentStorage` (porta) com implementações `LocalFileStorage` (dev/test)
  e `AzureBlobStorage` (hml/prod, Sprint 8).
- Operações mínimas: `put(stream, sha256, content_type) -> StorageKey`, `open(key)`,
  `exists(key)`, `delete(key)` (somente via política de retenção).
- **SHA-256 calculado em streaming** no upload, antes da persistência. O hash é usado
  para integridade, deduplicação (ADR-011) e auditoria.
- Chave de armazenamento **gerada pelo sistema**, nunca derivada do nome enviado pelo
  usuário: `{organization_id}/{sha256[0:2]}/{sha256}`. O nome original é metadado
  sanitizado. Isso elimina path traversal por construção.
- Banco guarda apenas metadados (`Attachment`): chave, hash, tamanho, MIME detectado,
  nome original sanitizado, origem.
- Em produção: container privado, acesso por Managed Identity, soft delete e
  versionamento de blobs habilitados (ver `docs/backup-recovery.md`).

## Alternativas consideradas

- **BYTEA no PostgreSQL** — simples, mas incha backup/restore e o banco; rejeitado.
- **Chave por nome de arquivo** — risco de colisão e traversal; rejeitado.

## Consequências

- Todo acesso a arquivo passa pela interface; nenhum módulo usa caminho de disco direto.
- Testes podem usar storage em diretório temporário.
