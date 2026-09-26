# Segurança — arquitetura e controles

> Política de divulgação de vulnerabilidades: [`../SECURITY.md`](../SECURITY.md).
> Ameaças e mitigações: [`threat-model.md`](threat-model.md). Privacidade: [`lgpd.md`](lgpd.md).

## 1. Princípios

- Segurança por padrão; integrações externas **desligadas** por padrão.
- Menor privilégio em pessoas, aplicação, banco, Azure e Microsoft 365.
- Backend decide autorização; frontend só adapta a UX.
- Nenhum segredo no repositório; `.env.example` só com placeholders.
- Falhar de forma explícita e segura (fail-closed), com mensagem compreensível.

## 2. Controles por área

| Área            | Controle                                                                                                                                                                                                                         | Sprint |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| Identidade      | Entra ID (OIDC, PKCE), validação JWT, App Roles → permissões                                                                                                                                                                     | 7      |
| Auth DEV        | Só com `APP_ENV=local` + `DEV_AUTH_ENABLED=true`; fail-fast fora de local; banner/warning                                                                                                                                        | 1      |
| Autorização     | Permissão declarada por endpoint; testes da matriz perfil × permissão                                                                                                                                                            | 1/7    |
| Isolamento      | Filtro obrigatório por `organization_id` nos repositórios                                                                                                                                                                        | 1+     |
| Upload          | Tamanho máximo; tipo real por magic bytes (não só extensão/MIME declarado); lista de tipos permitidos (XML, PDF, CSV, XLSX); nome sanitizado; chave de storage gerada pelo sistema; XLSX tratado como ZIP com limites (zip bomb) | 2/7    |
| XML             | Sem DTD/entidades externas/rede; limites de profundidade e tamanho                                                                                                                                                               | 2      |
| CSV/XLSX        | Sem avaliação de fórmulas; neutralização de CSV injection em exportações (`=`, `+`, `-`, `@`)                                                                                                                                    | 3      |
| Dados           | `NUMERIC` p/ dinheiro; constraints; timestamps UTC                                                                                                                                                                               | 1+     |
| Auditoria       | Append-only com grants restritos                                                                                                                                                                                                 | 1/5    |
| Segredos        | Key Vault + Managed Identity; certificado para Graph                                                                                                                                                                             | 7/8    |
| Transporte      | HTTPS obrigatório fora de local; HSTS                                                                                                                                                                                            | 7/8    |
| Headers         | CSP restritiva, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors 'none'`                                                                                                                                            | 7      |
| Rate limit      | Em login/upload/endpoints caros, quando aplicável                                                                                                                                                                                | 7      |
| Erros           | Sem traceback/SQL/caminhos/segredos na resposta; código de erro + `request_id`                                                                                                                                                   | 1      |
| Logs            | Estruturados; sem tokens, senhas, documentos completos ou dados pessoais desnecessários                                                                                                                                          | 1      |
| Dependências    | Lockfiles, Dependabot, varredura de dependências, SBOM                                                                                                                                                                           | 9      |
| Código          | CodeQL, Ruff/mypy, ESLint                                                                                                                                                                                                        | 1/9    |
| Imagem          | Base mínima, usuário não root, Trivy, fixação por digest                                                                                                                                                                         | 1/9    |
| Segredos no Git | Secret scanning do GitHub + gitleaks no pre-commit/CI                                                                                                                                                                            | 0/9    |
| CI/CD           | OIDC para Azure; actions fixadas por SHA; produção com aprovação manual                                                                                                                                                          | 9      |
| IA              | Nenhum LLM no núcleo; LLM futuro nunca autoriza pagamento                                                                                                                                                                        | —      |

## 3. Perfis e permissões (proposta inicial)

| Permissão                                           | ADMIN | ANALYST | APPROVER |   AUDITOR   |
| --------------------------------------------------- | :---: | :-----: | :------: | :---------: |
| Ver dashboard, documentos, exceções                 |   ✔   |    ✔    |    ✔     | ✔ (leitura) |
| Enviar documentos / importar CSV-XLSX               |   ✔   |    ✔    |    —     |      —      |
| Decidir exceção WARNING (aceitar/rejeitar/resolver) |   ✔   |    ✔    |    ✔     |      —      |
| Decidir exceção CRITICAL                            |   ✔   |    —    |    ✔     |      —      |
| Solicitar nova análise                              |   ✔   |    ✔    |    ✔     |      —      |
| Alterar configurações e políticas                   |   ✔   |    —    |    —     |      —      |
| Configurar caixa Microsoft 365                      |   ✔   |    —    |    —     |      —      |
| Ver trilha de auditoria completa                    |   ✔   |    —    |    —     |      ✔      |

A matriz final é validada na Sprint 7 e coberta por testes.

## 4. Ambientes

| Ambiente             | `APP_ENV`      | Auth                    | Integrações externas   |
| -------------------- | -------------- | ----------------------- | ---------------------- |
| Local                | `local`        | DEV simulada (opcional) | mocks                  |
| Testes automatizados | `test`         | stubs de token          | mocks                  |
| Homologação          | `homologation` | Entra ID                | reais, com autorização |
| Produção             | `production`   | Entra ID                | reais, com autorização |

## 5. Verificações da Sprint 0

- Nenhum segredo, token, connection string ou credencial real no repositório.
- `.env` ignorado pelo Git; `.env.example` apenas com placeholders.
- PostgreSQL local publicado apenas em `127.0.0.1`; senha obrigatória via `.env`.
- Nenhuma integração externa ativa; nenhum recurso Azure/M365 criado.
