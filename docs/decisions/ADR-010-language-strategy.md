# ADR-010 — Estratégia de idiomas

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0
- **Histórico:** decisão equivalente aprovada pelo mantenedor em 2026-09-26 no plano anterior (com critérios); reapresentada no plano Cloud-First.

## Contexto

O produto é para empresas brasileiras, mas o código será aberto a contribuidores de
qualquer lugar. Termos fiscais brasileiros não têm tradução natural.

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

## Riscos

- Mistura de idiomas em identificadores: revisão de código e glossário em
  `docs/data-model.md`.

## Possibilidade de revisão

Se o projeto passar a atender outros países ou a comunidade pedir documentação técnica em
inglês.
