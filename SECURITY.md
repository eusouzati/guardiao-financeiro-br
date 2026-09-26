# Política de Segurança

## Versões suportadas

O projeto está em desenvolvimento inicial (pré-`v0.1.0`). Correções de segurança são
aplicadas apenas na branch `main` até a primeira release.

## Como reportar uma vulnerabilidade

**Não abra issue pública.** Use o recurso de _Private vulnerability reporting_ do GitHub
(aba **Security → Report a vulnerability**) quando o repositório for publicado.
<!-- TODO(mantenedor): definir um e-mail de contato de segurança antes da publicação (Sprint 10). -->

Inclua: descrição, impacto, passos para reproduzir, versão/commit afetado e, se possível,
sugestão de correção. **Não envie documentos fiscais ou dados pessoais reais** — use
dados fictícios.

## Nosso compromisso

- Confirmar o recebimento em até 5 dias úteis.
- Avaliação inicial em até 10 dias úteis.
- Divulgação coordenada após a correção, com crédito ao pesquisador se desejado.

## Escopo

Em escopo: código deste repositório, configurações padrão, imagens e IaC publicados.
Fora do escopo: implantações de terceiros, engenharia social, DoS volumétrico,
vulnerabilidades em dependências sem impacto demonstrável no projeto.

## Práticas do projeto

Desenho de segurança em [`docs/security.md`](docs/security.md), ameaças em
[`docs/threat-model.md`](docs/threat-model.md) e privacidade em [`docs/lgpd.md`](docs/lgpd.md).
