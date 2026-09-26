# Frontend — Guardião Financeiro BR

SPA em **React 19 + TypeScript + Vite + Tailwind CSS 4** (Node 24 LTS, npm).

## Execução

```bash
npm ci
npm run dev        # http://localhost:5173 — proxy de /api para http://localhost:8000
```

Em containers, o Nginx serve o build e encaminha `/api/` ao backend (mesma origem, sem CORS).

## Qualidade e testes

```bash
npm run lint           # ESLint strict type-checked + jsx-a11y
npm run typecheck
npm run format:check
npm test               # Vitest + Testing Library
npm run build
npm run e2e            # Playwright, com a stack rodando (docker compose up)
```

## Estrutura

```text
src/
├── app/          # rotas, layout, sessão do usuário
├── pages/        # telas
├── components/   # componentes reutilizáveis e ícones próprios
├── api/          # cliente HTTP e tipos das respostas
├── hooks/        # useApiQuery
├── i18n/         # textos pt-BR
├── lib/          # formatação pt-BR (moeda, datas) sem float
└── test/         # utilitários de teste
e2e/              # Playwright
nginx/            # configuração do Nginx sem privilégios
```

## Regras

- Nenhuma decisão de autorização ou cálculo financeiro decisório no frontend.
- Valores decimais chegam como string e são formatados sem conversão para `float`
  (o lint proíbe `parseFloat`).
- Status sempre com texto + ícone, nunca só cor (WCAG).
- Módulos ainda não implementados mostram estado vazio honesto, sem dados simulados.
