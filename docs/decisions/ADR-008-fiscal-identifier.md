# ADR-008 — Identificador fiscal (CNPJ) como string e alfanumérico

- **Status:** Aceita
- **Data:** 2026-09-26
- **Sprint:** 0 (implementação: Sprint 2)

## Contexto

A Receita Federal instituiu o **CNPJ alfanumérico** (IN RFB nº 2.229/2024), atribuído a
novas inscrições a partir de **julho de 2026**. CNPJs existentes permanecem numéricos.
Formato: 14 posições — as 12 primeiras (raiz + ordem) podem conter letras `A–Z` e dígitos;
as 2 últimas (dígitos verificadores) continuam numéricas. O DV é calculado por módulo 11,
convertendo cada caractere para `ord(c) - 48` (dígitos mantêm o valor; `A`=17, `B`=18…).

## Decisão

- CNPJ é **sempre string**, nunca inteiro, em todas as camadas (Python, banco, API, UI).
- Um único **value object** `FiscalId` / serviço `fiscal_id` em `app/domain/` concentra:
  normalização (remove máscara, uppercase), detecção de tipo (CNPJ numérico, CNPJ
  alfanumérico, CPF), validação de DV e formatação para exibição.
- Nenhum outro módulo implementa regex ou regra de CNPJ.
- Banco: `VARCHAR(14)` para o valor normalizado (sem máscara), com `CHECK` de padrão
  `^[0-9A-Z]{12}[0-9]{2}$` para CNPJ.
- Comparações de fornecedor usam o valor normalizado; a raiz (8 primeiras posições) é
  exposta para regras de mesmo grupo empresarial (matriz/filial) se necessário no futuro.
- Testes cobrem CNPJ numérico, alfanumérico, com máscara, minúsculas e DV inválido
  usando **somente identificadores fictícios**.

## Alternativas consideradas

- **BIGINT** — incompatível com o formato alfanumérico e perde zeros à esquerda.
- **Validação espalhada por regex** — foi explicitamente vedada no escopo.

## Consequências

- CPF (quando presente, ex.: prestador pessoa física na NFS-e) é dado pessoal: tratado
  pelo mesmo value object, com mascaramento em logs (ver `docs/lgpd.md`).
