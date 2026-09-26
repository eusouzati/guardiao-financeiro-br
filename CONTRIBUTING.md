# Como contribuir

Obrigado pelo interesse no Guardião Financeiro BR!

## Antes de começar

1. Leia o [Código de Conduta](CODE_OF_CONDUCT.md).
2. Leia as [convenções](docs/conventions.md) e a [arquitetura](ARCHITECTURE.md).
3. Leia a [política de dados fictícios](docs/synthetic-data-policy.md): **nunca** inclua
   documentos, CNPJs, CPFs, e-mails ou nomes reais.
4. Para mudanças grandes, abra uma issue para discussão antes do PR.

## Ambiente

Veja [docs/environment-setup.md](docs/environment-setup.md). Opcionalmente instale os
hooks: `uvx pre-commit install`.

## Fluxo

1. Crie uma branch a partir de `main` (`feat/…`, `fix/…`, `docs/…`).
2. Commits no padrão [Conventional Commits](https://www.conventionalcommits.org/).
3. Rode localmente lint, type check e testes (backend: `uv run ruff check .`,
   `uv run ruff format --check .`, `uv run mypy`, `uv run pytest`).
4. Atualize documentação, ADRs e `CHANGELOG.md` quando aplicável.
5. Abra o PR preenchendo o template.

## Critérios de aceite de um PR

- Testes relevantes existem e passam; lint e type check passam.
- Sem segredos e sem dados reais.
- Regras financeiras: `Decimal`, tolerâncias configuráveis, testes de comportamento.
- Autorização aplicada no backend.
- Mensagens ao usuário em pt-BR, sem detalhes técnicos internos.

## Licença das contribuições

Ao contribuir, você concorda que sua contribuição será licenciada sob a
[Apache License 2.0](LICENSE) (seção 5 da licença).
