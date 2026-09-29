# Motor de regras e three-way match

> Especificação inicial (Sprint 0). Implementação e testes na Sprint 4. Ver ADR-016.

## 1. Princípios

1. Determinístico, sem LLM, sem score opaco.
2. Toda regra é pura (sem I/O), versionada e com testes unitários independentes.
3. Toda execução grava `ruleset_version` e snapshot da configuração.
4. Nenhuma exceção crítica desaparece automaticamente; reprocessamento cria nova
   `MatchingRun` e exceções antigas só mudam de estado por decisão humana registrada.
5. O resultado responde: **"Por que este documento recebeu este status?"**

## 2. Contrato de regra

```text
Rule
  code: str               # estável, ex. AMOUNT_MISMATCH
  version: str            # SemVer da regra
  title / description     # pt-BR
  default_severity        # INFO | WARNING | CRITICAL
  evaluate(ctx: MatchingContext) -> RuleResult

RuleResult
  id, rule_code, rule_version, title, description,
  outcome: PASSED | FAILED | NOT_APPLICABLE | ERROR,
  severity, evidence: {campo: valor comparado...},
  explanation: str (pt-BR), evaluated_at (UTC)
```

## 3. Regras iniciais

| #     | Código                      | Descrição                                                                        | Severidade        |
| ----- | --------------------------- | -------------------------------------------------------------------------------- | ----------------- |
| 11.1  | `DUPLICATE_EXACT`           | Mesma chave de acesso já existente na organização                                | CRITICAL          |
| 11.2  | `DUPLICATE_FISCAL`          | Mesmo CNPJ emitente + número + série (+ modelo)                                  | CRITICAL          |
| 11.3  | `DUPLICATE_POSSIBLE`        | Mesmo fornecedor + mesmo valor em janela `duplicate_window_days`                 | WARNING           |
| 11.4  | `RECIPIENT_MISMATCH`        | CNPJ destinatário ≠ organização configurada                                      | CRITICAL          |
| 11.5  | `SUPPLIER_MISMATCH`         | Emitente ≠ fornecedor do pedido (CNPJ tem precedência sobre nome)                | CRITICAL          |
| 11.6  | `PURCHASE_ORDER_MISSING`    | Sem pedido quando `purchase_order_required`                                      | configurável      |
| 11.7  | `AMOUNT_MISMATCH`           | Total do documento × pedido fora da tolerância                                   | WARNING/CRITICAL* |
| 11.8  | `ITEM_MISMATCH`             | Quantidade, unitário, total ou correspondência de item                           | WARNING/CRITICAL* |
| 11.9  | `RECEIPT_MISSING`           | Pedido existe sem recebimento, quando `receipt_required`                         | WARNING/CRITICAL* |
| 11.10 | `QUANTITY_EXCEEDS_RECEIVED` | Quantidade faturada > quantidade recebida                                        | CRITICAL          |
| 11.11 | `TOTAL_INCONSISTENT`        | Soma de itens/descontos/frete/outras ≠ total informado, dentro da regra definida | CRITICAL          |
| 11.12 | `FUTURE_DOCUMENT`           | Emissão posterior ao processamento (+ tolerância de relógio)                     | WARNING           |
| 11.13 | `OLD_DOCUMENT`              | Emissão anterior a `old_document_threshold_days`                                 | INFO/WARNING*     |

\* Severidade a calibrar na Sprint 4 e tornar configurável quando fizer sentido; a escolha
final será registrada em ADR.

`TOTAL_INCONSISTENT` confere **somente aritmética** dos valores presentes no XML
(ex.: Σ `vProd` dos itens − descontos + frete + seguro + outras + tributos que compõem o
total, conforme regra documentada). Não recalcula tributos nem afirma valor fiscal correto.

## 4. Tolerância monetária

Diferença aceitável se `|doc − pedido| ≤ tolerance_absolute` **ou**
`|doc − pedido| / pedido × 100 ≤ tolerance_percentage` (política exata — "ou" vs "e" —
confirmada na Sprint 4 e registrada em ADR). Evidência sempre mostra valores, diferença
absoluta e percentual:

```text
CRITICAL — Valor superior ao pedido.
NF-e: R$ 15.780,00 | Pedido: R$ 14.900,00 | Diferença: R$ 880,00 (5,91%)
```

## 5. Agregação de status (proposta inicial)

| Condição (avaliada em ordem)                                                                                    | Status                  |
| --------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Alguma regra `FAILED` com `CRITICAL` do grupo **bloqueante** (duplicidade exata/fiscal, destinatário incorreto) | `BLOCKED`               |
| Alguma regra `FAILED` com `CRITICAL`, ou alguma regra em `ERROR`                                                | `NEEDS_REVIEW`          |
| Alguma regra `FAILED` com `WARNING`                                                                             | `MATCHED_WITH_WARNINGS` |
| Demais casos (apenas `PASSED`, `NOT_APPLICABLE` ou `INFO`)                                                      | `MATCHED`               |

`BLOCKED` significa "não deve seguir no processo sem decisão humana explícita"; o sistema
não executa nenhuma ação financeira em nenhum caso.

## 6. Seleção de candidatos

1. Fornecedor: por CNPJ normalizado do emitente; aliases apenas como apoio visual.
2. Pedido: referência explícita no XML (`xPed`/`nItemPed` na NF-e, informações adicionais)
   → pedido aberto do mesmo fornecedor com valor compatível → nenhum (`PURCHASE_ORDER_MISSING`).
3. Recebimento(s): vinculados ao pedido; entregas parciais somam quantidades.
4. Ambiguidade (mais de um candidato) nunca é resolvida silenciosamente: gera exceção.
