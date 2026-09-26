# ADR-013 — Idioma de código, documentação e interface

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26 (com critérios)
- **Data:** 2026-09-26
- **Sprint:** 0

## Decisão

| Artefato                                                          | Idioma                                                                                                                |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Interface do usuário, mensagens de erro, explicações de regras    | **Português do Brasil**                                                                                               |
| Identificadores de código, nomes de tabelas/colunas, rotas da API | **Inglês**                                                                                                            |
| Termos fiscais sem tradução natural                               | Mantidos em pt-BR/sigla (ex.: `access_key` para chave de acesso, `cfop`, `ncm`) com glossário em `docs/data-model.md` |
| Documentação técnica (`docs/`, ADRs)                              | Português do Brasil                                                                                                   |
| `README.md`                                                       | Inglês (alcance open source), com `README.pt-BR.md` completo                                                          |
| Mensagens de commit                                               | Conventional Commits; descrição em pt-BR ou inglês, consistente por PR                                                |

Formatos: exibição `R$ 12.345,67` e `26/09/2026`; internamente ISO 8601 e UTC.

### Critérios do mantenedor (2026-09-26)

Interface, mensagens ao usuário e documentação funcional **prioritariamente em pt-BR**.
Código, banco, APIs, classes, funções e identificadores internos **preferencialmente em
inglês**, mantendo padrão técnico e facilitando contribuição open source.

## Alternativas consideradas

- **Código em português** — dificulta contribuição externa e conflita com nomes de
  bibliotecas. **Tudo em inglês** — contraria o público-alvo.

## Consequências

- Textos da UI centralizados em arquivos de mensagens para facilitar revisão.
