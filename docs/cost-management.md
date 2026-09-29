# Gestão de custos do MVP

> Estimativas de varejo, em USD, sem créditos nem serviços gratuitos da conta. Valores
> exatos da região: `./scripts/azure/estimate-cost.ps1` (API pública de preços do Azure) e
> Cost Management no portal. Preços mudam; revise antes de cada sprint.

## 1. Classificação

| Classe           | Critério (custo mensal estimado) |
| ---------------- | -------------------------------- |
| SEM CUSTO DIRETO | US$ 0                            |
| BAIXO            | até US$ 10                       |
| MÉDIO            | de US$ 10 a US$ 50               |
| ALTO             | acima de US$ 50                  |

## 2. Recursos da Sprint 0

| Recurso                                | SKU / configuração                           | Cobrança contínua?                   | Estimativa mensal                                  | Classe           |
| -------------------------------------- | -------------------------------------------- | ------------------------------------ | -------------------------------------------------- | ---------------- |
| PostgreSQL Flexible Server             | Burstable B1ms, 32 GB, backup 7 dias, sem HA | **Sim** (computação + storage, 24×7) | ≈ US$ 30–35                                        | **MÉDIO**        |
| Container Registry                     | Basic                                        | **Sim** (diária)                     | ≈ US$ 5–7                                          | BAIXO            |
| Zona DNS privada                       | 1 zona                                       | Sim                                  | ≈ US$ 0,50                                         | BAIXO            |
| Log Analytics + Application Insights   | 30 dias, limite 0,2 GB/dia                   | Por uso                              | US$ 0–3 (5 GB/mês gratuitos por conta de cobrança) | BAIXO            |
| Container Apps (api, web, job)         | Consumption, escala a zero                   | Por uso                              | ≈ US$ 0 (dentro da cota gratuita mensal)           | BAIXO            |
| Storage Account                        | Standard LRS, pouco volume                   | Por uso                              | < US$ 1                                            | BAIXO            |
| Key Vault                              | Standard, poucas operações                   | Por uso                              | < US$ 1                                            | BAIXO            |
| VNet e sub-redes                       | —                                            | Não                                  | US$ 0                                              | SEM CUSTO DIRETO |
| Identidades gerenciadas, RBAC          | —                                            | Não                                  | US$ 0                                              | SEM CUSTO DIRETO |
| Budget                                 | —                                            | Não                                  | US$ 0                                              | SEM CUSTO DIRETO |
| Workload profiles (só Consumption)     | sem perfil dedicado                          | Não                                  | US$ 0                                              | SEM CUSTO DIRETO |
| Shared Mailbox                         | sem licença (até 50 GB)                      | Não                                  | US$ 0                                              | SEM CUSTO DIRETO |
| App Registrations / Service Principals | —                                            | Não                                  | US$ 0                                              | SEM CUSTO DIRETO |
| **Total estimado**                     |                                              |                                      | **≈ US$ 37–47/mês**                                | MÉDIO            |

O item dominante é o PostgreSQL (≈ 70% do total).

## 3. O que reduz custo

- **Parar o PostgreSQL** quando o MVP não estiver em uso (a computação para de ser cobrada;
  o storage continua; o Azure religa automaticamente após 7 dias):
  `az postgres flexible-server stop -g rg-gfbr-mvp -n <servidor>` e `... start ...`.
- Container Apps já escalam a zero sem tráfego (primeira requisição mais lenta).
- Log Analytics tem limite diário de ingestão; aumentar só com justificativa.
- Não usar Private Endpoints, NAT Gateway, perfis dedicados, HA ou backup geo-redundante
  sem nova decisão ([ADR-011](decisions/ADR-011-mvp-networking.md)).

## 4. Orçamento e alertas

- `budget-gfbr-mvp`: orçamento mensal no grupo de recursos (padrão 50 na moeda de cobrança
  da assinatura), alertas por e-mail em 50%, 80% e 100% do gasto real e 100% do previsto.
- Criado pelo Bicep quando o deploy recebe `-BudgetEmails`. O e-mail de alerta é passado
  na sessão, nunca versionado.
- **Passo manual** (se a assinatura não suportar budgets via API, como algumas ofertas de
  avaliação, ou se nenhum e-mail for informado): Portal → Cost Management → Budgets →
  escopo `rg-gfbr-mvp` → mensal, valor definido pelo responsável → alertas 50/80/100% →
  e-mail do responsável.
- Assinaturas Free Trial têm limite de gastos e crédito com prazo: ao fim, sem migração
  para pay-as-you-go, a assinatura é desativada e os recursos param.

## 5. Protocolo para novos recursos

Antes de criar qualquer recurso novo: classificar (tabela da seção 1), informar se há
cobrança contínua, preferir a opção mais econômica que preserve os requisitos do MVP e
registrar a justificativa em ADR quando o custo for relevante.
