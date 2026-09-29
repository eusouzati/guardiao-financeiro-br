# Privacidade e LGPD

> Documento inicial (Sprint 0). Não constitui parecer jurídico; cada organização que
> implantar o sistema deve validar com seu encarregado (DPO) e assessoria jurídica.

## 1. Papéis

| Cenário                                               | Controlador       | Operador                                                          |
| ----------------------------------------------------- | ----------------- | ----------------------------------------------------------------- |
| Autoimplantação (empresa roda o software open source) | A empresa usuária | A própria empresa (e seus provedores de nuvem como suboperadores) |
| SaaS futuro                                           | Empresa cliente   | Provedor do serviço SaaS                                          |

Os mantenedores do projeto open source **não** tratam dados das implantações.

## 2. Dados tratados

| Categoria                              | Exemplos                                                              | Pessoal?                        | Finalidade                           |
| -------------------------------------- | --------------------------------------------------------------------- | ------------------------------- | ------------------------------------ |
| Dados de empresas                      | CNPJ, razão social, endereço, valores, itens                          | Em regra não (PJ)               | Conferência de contas a pagar        |
| Dados de pessoas físicas em documentos | CPF de prestador PF, nome, endereço, e-mail em informações adicionais | **Sim**                         | Conferência — minimizar              |
| Usuários do sistema                    | nome, e-mail corporativo, Entra object ID, ações                      | **Sim**                         | Autenticação, autorização, auditoria |
| Metadados de e-mail                    | remetente, assunto, data                                              | **Sim** (remetente pode ser PF) | Rastreabilidade da ingestão          |
| Logs técnicos                          | request ID, IP, user ID                                               | **Sim** (IP)                    | Segurança e operação                 |

Base legal típica (a validar pelo controlador): execução de contrato, cumprimento de
obrigação legal/regulatória, legítimo interesse (prevenção a fraude e erro).

## 3. Privacy by Design — controles

- **Minimização:** extrair apenas campos necessários à conferência; não copiar
  informações adicionais inteiras para logs/telemetria.
- **Controle de acesso:** RBAC no backend; auditor com leitura.
- **Registro de acessos importantes:** eventos de auditoria para visualização de
  documento, exportação e mudança de configuração (Sprint 5/7).
- **Segregação lógica:** `organization_id` em todas as entidades.
- **Proteção de arquivos:** storage privado, criptografia em repouso (Azure), acesso por
  Managed Identity, chave gerada pelo sistema.
- **Mascaramento:** CPF e e-mails mascarados em logs (ex.: `***.456.789-**`).
- **Retenção configurável:** política por tipo de dado (documentos, anexos, e-mails,
  logs, auditoria), respeitando prazos legais de guarda aplicáveis à organização.
- **Exclusão:** mecanismo de exclusão/anonimização conforme política da organização,
  registrado em auditoria; auditoria pseudonimizada em vez de apagada quando houver
  obrigação de guarda.
- **Backup:** ver [`backup-restore.md`](backup-restore.md); exclusões respeitam o ciclo
  de expiração dos backups (documentado).
- **Telemetria:** nunca envia documentos fiscais completos nem dados pessoais
  desnecessários.
- **Repositório público:** somente dados fictícios ([`synthetic-data-policy.md`](synthetic-data-policy.md)).

## 4. Localização dos dados

A região Azure é parâmetro de infraestrutura. Sugere-se `brazilsouth` quando técnica e
economicamente adequado, mas a LGPD **não** exige, por si só, armazenamento físico no
Brasil; transferências internacionais seguem os mecanismos dos arts. 33 a 36 da LGPD e a
regulamentação da ANPD.

## 5. Pendências (roadmap)

- Relatório de dados tratados exportável por organização (Sprint 7).
- Procedimento de atendimento a titulares (Sprint 7/10).
- Política de retenção padrão com valores sugeridos (Sprint 7).
