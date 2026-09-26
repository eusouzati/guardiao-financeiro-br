# Política de dados fictícios

> Obrigatória para todo conteúdo versionado: fixtures, testes, seeds, exemplos, docs,
> screenshots e issues.

## 1. Regra

**Nenhum dado real entra no repositório.** Isso inclui CPFs, CNPJs, razões sociais,
nomes de pessoas, e-mails, telefones, endereços, chaves de acesso, números de notas,
protocolos, pedidos, valores de contratos reais e documentos fiscais reais — mesmo que
"anonimizados à mão".

## 2. Como gerar dados fictícios

| Dado         | Regra                                                                                                                                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Razão social | Nomes claramente fictícios com marcador: `Fornecedor Exemplo Alfa Ltda`, `Empresa Demonstração Beta S.A.`                                                                                                                 |
| CNPJ         | Gerado por script do projeto (Sprint 2) com DV válido e registrado em `fixtures/REGISTRY.md`; preferir CNPJs **alfanuméricos** fictícios. Nunca copiar CNPJ de consulta pública.                                          |
| CPF          | Evitar. Se indispensável, gerar com DV válido pelo script e marcar como fictício.                                                                                                                                         |
| E-mail       | Somente domínios reservados (RFC 2606/6761): `@example.com`, `@example.org`, `*.test`, `*.example`                                                                                                                        |
| Telefone     | `(00) 0000-0000` ou sequências obviamente falsas                                                                                                                                                                          |
| Endereço     | `Rua Exemplo, 100 — Cidade Fictícia/UF`                                                                                                                                                                                   |
| NF-e         | `tpAmb=2` (homologação); `xNome` do destinatário conforme padrão de homologação ("NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"); chave de acesso montada a partir dos dados fictícios; sem assinatura real |
| NFS-e        | Ambiente de produção restrita/homologação; município e códigos fictícios quando possível                                                                                                                                  |
| Valores      | Arbitrários, sem relação com contratos reais                                                                                                                                                                              |

> Observação honesta: um CNPJ gerado com DV válido **pode** coincidir com uma inscrição
> real. Por isso, além do DV, todo documento fictício usa nomes com marcador "Exemplo" /
> "Demonstração", e-mails em domínios reservados e ambiente de homologação — e o registro
> em `REGISTRY.md` permite substituir rapidamente qualquer identificador reportado.

## 3. Onde ficam

- `backend/tests/fixtures/` — fixtures de teste (Sprint 2+).
- `demo/` — dataset de demonstração (≥ 20 cenários, Sprint 4/5).
- Qualquer outro diretório com dados precisa ser aprovado em PR e listado aqui.

## 4. Verificação

- Revisão obrigatória em PR que adiciona fixtures.
- gitleaks (pre-commit/CI) para segredos.
- Revisão completa antes da publicação (Sprint 10).
- Dados de clientes, se algum dia usados para diagnóstico, ficam **fora** do repositório,
  em diretórios ignorados (`/data/`, `/real-data/`, `/uploads/`).

## 5. Incidente

Se dado real for commitado: não fazer push; remover do histórico local; se já publicado,
tratar como incidente (reescrita de histórico, rotação/notificação conforme o caso) e
registrar em `SECURITY.md`/issue privada.
