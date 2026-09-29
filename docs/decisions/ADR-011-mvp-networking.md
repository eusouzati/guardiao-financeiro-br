# ADR-011 — Rede do MVP

- **Status:** ACCEPTED — opção A escolhida pelo responsável em 2026-09-29
- **Data:** 2026-09-29
- **Sprint:** 0
- **Histórico:** no plano anterior, o ambiente `dev` usaria PostgreSQL público restrito a
  serviços do Azure; o plano Cloud-First pede reavaliar, com a restrição de não adotar
  regras amplas como permanentes e de não criar Private Endpoints sem justificativa.

## Contexto

Os recursos com dados são o PostgreSQL (metadados), o Storage (documentos) e o Key Vault
(segredos). O frontend precisa ser público; a API, não. É preciso equilibrar segurança,
custo e complexidade, e a decisão de rede do PostgreSQL Flexible Server **não pode ser
trocada depois da criação** (acesso público ↔ integração à VNet exige recriar o servidor).

## Decisão (opção A)

Uma VNet pequena, sem Private Endpoints:

| Item             | Valor                                                                                    | Finalidade                                                       |
| ---------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| VNet             | `vnet-gfbr-mvp` — `10.60.0.0/22`                                                         | Rede do MVP (espaço para crescer sem renumerar)                  |
| Sub-rede         | `snet-container-apps` — `10.60.0.0/24`, delegada a `Microsoft.App/environments`          | Ambiente do Container Apps (workload profiles; mínimo /27)       |
| Sub-rede         | `snet-postgres` — `10.60.1.0/28`, delegada a `Microsoft.DBforPostgreSQL/flexibleServers` | PostgreSQL com integração à VNet                                 |
| Zona DNS privada | `gfbr-mvp.private.postgres.database.azure.com` + link                                    | Resolução do nome do PostgreSQL dentro da VNet                   |
| Reservado        | `10.60.1.16` – `10.60.3.255`                                                             | Futuro (ex.: worker dedicado, Private Endpoints se justificados) |

- **PostgreSQL sem endpoint público** (`publicNetworkAccess = Disabled`), alcançável apenas
  pelas aplicações e jobs do Container Apps na VNet; TLS obrigatório.
- **Container Apps:** ambiente com workload profiles (perfil **Consumption**, escala a
  zero), ingress externo **somente** no frontend; a API tem ingress interno; tráfego entre
  aplicações criptografado pelo ambiente. A plataforma cria o grupo gerenciado
  `rg-gfbr-mvp-cae-infra`.
- **Storage e Key Vault:** endpoints públicos, mas sem acesso anônimo nem chave
  compartilhada — toda operação exige token Entra e papel RBAC. Private Endpoints não são
  criados no MVP (custo mensal por endpoint + zonas DNS, sem ganho proporcional agora).
- **ACR:** endpoint público com pull somente por identidade gerenciada (`AcrPull`); push
  somente por quem faz o deploy (`AcrPush`); sem admin user nem pull anônimo.
- Sem NSG customizado, NAT Gateway, Azure Firewall, VPN ou peering.
- Custo direto da rede: VNet e sub-redes sem custo; zona DNS privada ≈ US$ 0,50/mês.

**Opção B (alternativa):** sem VNet — PostgreSQL com endpoint público, regra especial
`0.0.0.0`–`0.0.0.0` (somente serviços hospedados no Azure, **não** é `0.0.0.0/0`), TLS e
senha forte; nenhum IP externo liberado. O Bicep suporta as duas opções pelo parâmetro
`enablePrivateNetwork` (padrão `true`).

## Alternativas consideradas

- **Opção B (PostgreSQL público restrito a serviços do Azure)** — mais simples, mas a
  regra permite conexões de qualquer serviço hospedado no Azure (inclusive de outros
  clientes), protegidas apenas por senha e TLS; trocar depois exige recriar o servidor.
- **Private Endpoints para PostgreSQL, Storage, Key Vault e ACR** — mais isolamento, mas
  custo mensal por endpoint, várias zonas DNS e ACR Premium para endpoint privado;
  desproporcional ao MVP.
- **Ambiente do Container Apps interno + Application Gateway/Front Door** — custo alto
  para expor um frontend simples.

## Consequências

- Administradores **não** conectam ao PostgreSQL a partir da própria máquina: migrations
  rodam pelo job `caj-gfbr-migrate-mvp` dentro da VNet. Acesso administrativo pontual
  (consulta, restore) exige um job/contêiner na VNet ou liberação temporária documentada.
- Migrar para opção B (ou vice-versa) depois exige recriar o PostgreSQL (restore de backup).

## Riscos

- **Opção A:** mais peças para o deploy (delegações de sub-rede, DNS privado); falhas
  aparecem no `what-if`/deploy e são corrigíveis sem perda de dados antes do uso.
- **Opção A:** sub-rede do Container Apps não pode ser trocada sem recriar o ambiente;
  `/24` dá margem para o MVP.
- **Endpoints públicos de Storage e Key Vault:** mitigados por Entra ID/RBAC; restrição de
  rede reavaliada na Sprint 8.

## Possibilidade de revisão

Na Sprint 8 (Reliability & Cloud Hardening): restrição de rede de Storage/Key Vault/ACR e
Private Endpoints se a análise de risco e custo justificar.
