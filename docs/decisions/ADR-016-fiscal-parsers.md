# ADR-016 — Parsers fiscais versionados e XML seguro

- **Status:** Aceita (princípios); biblioteca XML: a decidir na Sprint 2
- **Data:** 2026-09-26
- **Sprint:** 0 (implementação: Sprint 2)

## Decisão

- Interface `FiscalDocumentParser` com `can_parse(root_info) -> ParserMatch` e
  `parse(bytes) -> ParsedFiscalDocument` (estrutura normalizada, sem dependência de ORM).
- Implementações iniciais: `NFeParser` (modelo 55, layout 4.00, incluindo grupos
  IBS/CBS da Reforma Tributária) e `NFSeNationalParser` (padrão nacional).
  `NFSeMunicipalParser` fica como extensão futura.
- Um `ParserRegistry` escolhe o parser por namespace/elemento raiz/versão do layout.
  Layout não reconhecido → erro explícito `UNSUPPORTED_LAYOUT` com detalhes; **nunca**
  interpretação "melhor esforço" silenciosa.
- Campos não mapeados de layouts conhecidos são preservados em estrutura controlada
  (`unmapped_fields`) ou registrados como `unsupported`, nunca descartados em silêncio.
- **XML seguro:** DTD e entidades externas desabilitadas, sem acesso à rede, limite de
  tamanho antes do parse, limites de profundidade/expansão (proteção contra XXE e XML
  bomb). Validação por XSD oficial quando os schemas puderem ser redistribuídos.
- O XML é a fonte autoritativa; PDF/DANFE é complementar. OCR/LLM nunca substitui dado
  disponível no XML.

## Alternativas consideradas

- **Bibliotecas prontas de NF-e** — geralmente focadas em emissão, com licenças variadas;
  avaliar caso a caso na Sprint 2.

## Consequências

- Fixtures XML sintéticas para cada layout/versão suportados (ver política de dados
  fictícios).
