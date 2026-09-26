# ADR-007 — Representação de valores monetários e quantidades

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26 (com critérios)
- **Data:** 2026-09-26
- **Sprint:** 0

## Contexto

Erros de ponto flutuante são inaceitáveis em conferência financeira. A NF-e admite valores
unitários com até 10 casas decimais e quantidades com até 4 casas.

## Decisão

- Backend: `decimal.Decimal` em todo o código; `float` proibido para dinheiro e quantidade
  (verificado por lint customizado/teste a partir da Sprint 1 e por revisão).
- Construção de `Decimal` sempre a partir de `str`, nunca de `float`.
- Banco: `NUMERIC` com precisão explícita por natureza do campo. Referência: leiaute da
  NF-e 4.00 (formato `inteiros v decimais`), a revalidar contra o MOC/NT vigente na Sprint 2:

| Natureza                                                                        | Exemplos                                                         | Formato no leiaute | Tipo no banco    |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------ | ---------------- |
| Valores monetários (totais, itens, tributos, bases de cálculo, frete, desconto) | `vProd`, `vNF`, `vICMS`, `vBC`, valores IBS/CBS, total do pedido | 13v2               | `NUMERIC(18,2)`  |
| Preço/valor unitário                                                            | `vUnCom`, `vUnTrib`, preço unitário do pedido                    | 11v0-10            | `NUMERIC(23,10)` |
| Quantidade                                                                      | `qCom`, `qTrib`, quantidade pedida/recebida                      | 11v0-4             | `NUMERIC(19,4)`  |
| Alíquota                                                                        | `pICMS`, `pIPI`, alíquotas IBS/CBS                               | 3v2-4              | `NUMERIC(9,4)`   |
| Percentual de negócio                                                           | `tolerance_percentage`, divergência %                            | —                  | `NUMERIC(9,4)`   |
| Tolerância absoluta                                                             | `tolerance_absolute`                                             | —                  | `NUMERIC(18,2)`  |

- **Preservar a precisão original do documento fiscal.** O parser converte o texto do XML
  diretamente para `Decimal` (sem passar por `float`) e **não arredonda**: campos unitários
  e quantidades mantêm todas as casas informadas; nenhum campo é forçado a 2 casas se o
  leiaute admite mais. Se um valor exceder a precisão da coluna, o documento gera erro
  explícito de validação — nunca truncamento ou arredondamento silencioso.
- Moeda explícita (`currency`, padrão `BRL`) junto a todo valor persistido de pedido.
- Nada de arredondamento em cálculos intermediários. Quando necessário, `quantize` com
  **ROUND_HALF_EVEN** (alinhado à ABNT NBR 5891), em um único módulo (`app/domain/money.py`).
- Comparações sempre com tolerância configurável: `tolerance_absolute` (R$) e
  `tolerance_percentage` (%); a configuração efetiva é gravada em cada `MatchingRun`.
- API: valores trafegam como **string decimal** em JSON (`"15780.00"`), nunca number.
- Frontend: formatação `pt-BR` (`R$ 12.345,67`) apenas para exibição; nenhum cálculo
  decisório no frontend.

### Critérios do mantenedor (2026-09-26)

Toda manipulação financeira usa `Decimal`/`NUMERIC`, nunca `float`; a precisão original dos
documentos fiscais é preservada; as precisões acima valem para valores monetários,
quantidades, preços unitários, percentuais e alíquotas.

## Alternativas consideradas

- **Inteiros em centavos** — não comporta 10 casas do valor unitário sem outra escala.
- **ROUND_HALF_UP** — comum em sistemas comerciais; poderá ser adotado por regra específica
  caso uma NT/regra fiscal o exija, documentando a exceção.

## Consequências

- Serializadores Pydantic configurados para `Decimal` → string.
- Testes de propriedade para operações monetárias na Sprint 4.
