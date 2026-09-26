# Documentos fiscais

> Sprint 0 — escopo e premissas. Parsers implementados na Sprint 2 (ADR-016).
> **Aviso:** o Guardião Financeiro BR confere consistência e divergências; ele **não**
> afirma que um documento está fiscal, contábil ou juridicamente correto.

## 1. Fonte autoritativa

- Com XML válido, o **XML é a fonte estruturada principal**.
- PDF/DANFE/DANFSe são representação visual ou anexo complementar.
- OCR/LLM nunca substituem dado disponível no XML.

## 2. NF-e (modelo 55)

- Layout 4.00 (`nfeProc` / `NFe`, namespace `http://www.portalfiscal.inf.br/nfe`).
- Campos a extrair: chave de acesso, número, série, modelo, emissão, emitente e
  destinatário (CNPJ/CPF, razão social, endereço), itens (código, descrição, NCM, CFOP,
  unidade, quantidade, valor unitário, valor total, desconto), tributos, frete, seguro,
  outras despesas, total da NF-e, informações adicionais, referência a pedido
  (`xPed`, `nItemPed`) quando presente, protocolo de autorização quando presente.
- **Reforma Tributária (IBS/CBS):** a NT 2025.002 (e revisões) introduziu grupos como
  `IBSCBS` por item e totalizadores `IBSCBSTot`; a partir de 2026 esses campos passaram a
  ser exigidos progressivamente pelas SEFAZ. No MVP os valores são **armazenados,
  interpretados, exibidos e comparados quando aplicável**, sem motor tributário.
  A versão exata dos grupos suportados será fixada na Sprint 2 contra a NT vigente.
- Campos desconhecidos de layout suportado → `unmapped_fields` ou `unsupported`,
  nunca descartados silenciosamente.

## 3. NFS-e — padrão nacional

- Suporte inicial ao **padrão nacional** (DPS/NFS-e do Sistema Nacional NFS-e, com
  distribuição pelo Ambiente de Dados Nacional — ADN).
- A LC 214/2025 determinou a adesão dos municípios ao padrão nacional a partir de
  01/01/2026, e as Notas Técnicas do SE/CGNFS-e (ex.: NT 007/2026, 008/2026, 009/2026)
  continuam ajustando o leiaute, inclusive para IBS/CBS. O parser será **versionado por
  leiaute** e testado com fixtures sintéticas por versão.
- Layouts municipais próprios: **fora do MVP** (`NFSeMunicipalParser` futuro). Documento
  em layout não suportado gera erro claro `UNSUPPORTED_LAYOUT`.

## 4. Identificadores fiscais

- CNPJ sempre string, preparado para o **CNPJ alfanumérico** (novas inscrições a partir de
  julho/2026). Regra centralizada no value object `FiscalId` (ADR-008).
- CPF pode aparecer (ex.: prestador pessoa física): é dado pessoal (ver `lgpd.md`).

## 5. Segurança no processamento de XML

- Tamanho máximo verificado antes do parse.
- DTD, entidades externas e acesso à rede **desabilitados** (XXE).
- Limites de expansão/profundidade (XML bomb / billion laughs).
- Nenhum conteúdo enviado é executado.
- Testes com payloads maliciosos sintéticos na Sprint 2 e Sprint 7.

## 6. Fora do escopo

Emissão de NF-e/NFS-e, consulta massiva à SEFAZ, validação de assinatura digital,
escrituração, SPED, motor tributário, suporte a todos os municípios.

## 7. Referências a acompanhar

- Portal Nacional da NF-e — Notas Técnicas (NT 2025.002 e revisões).
- Portal NFS-e Nacional — manuais, schemas e Notas Técnicas.
- Receita Federal — CNPJ alfanumérico (IN RFB nº 2.229/2024).

> Estas referências mudam com frequência. Antes de implementar cada parser, confirmar a
> versão vigente e registrar em ADR/CHANGELOG.
