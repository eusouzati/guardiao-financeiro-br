# Frontend — Guardião Financeiro BR

SPA em **React + TypeScript + Vite + Tailwind CSS** (Node 24 LTS, npm).

## Estado (Sprint 0)

Diretório reservado. O projeto Vite, ESLint (flat config), Vitest e Playwright serão
criados na **Sprint 1**, junto com layout, navegação e páginas iniciais
(Dashboard, Documentos, Pedidos, Fornecedores, Recebimentos, Exceções, Configurações).

## Estrutura prevista

```text
frontend/
├── src/
│   ├── app/          # rotas, layout, providers
│   ├── pages/        # telas
│   ├── components/   # componentes reutilizáveis (acessíveis)
│   ├── api/          # cliente HTTP tipado (gerado/validado a partir do OpenAPI)
│   ├── i18n/         # textos pt-BR centralizados
│   └── lib/          # formatação pt-BR (moeda, datas), utilitários
├── tests/            # Vitest
└── e2e/              # Playwright
```

## Regras

- Nenhuma decisão de autorização ou cálculo financeiro decisório no frontend.
- Valores recebidos como string decimal e formatados com `Intl` em `pt-BR`.
- Status sempre com texto + ícone, nunca só cor (WCAG).
