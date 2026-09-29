import { expect, test, type Page } from '@playwright/test';

const PAGES = [
  ['Exceções', 'Exceções'],
  ['Documentos', 'Documentos'],
  ['Pedidos', 'Pedidos de compra'],
  ['Recebimentos', 'Recebimentos'],
  ['Fornecedores', 'Fornecedores'],
  ['Configurações', 'Configurações'],
  ['Painel', 'O que precisa da minha atenção agora?'],
] as const;

function collectConsoleErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') {
      errors.push(message.text());
    }
  });
  return errors;
}

test('painel carrega com a situação real do sistema', async ({ page }) => {
  const errors = collectConsoleErrors(page);
  await page.goto('/');
  await expect(
    page.getByRole('heading', { level: 1, name: 'O que precisa da minha atenção agora?' }),
  ).toBeVisible();
  await expect(page.getByText('Operacional')).toHaveCount(2);
  expect(errors).toEqual([]);
});

test('navegação pelo menu alcança todas as páginas iniciais', async ({ page }) => {
  await page.goto('/');
  const nav = page.getByRole('navigation', { name: 'Navegação principal' });
  for (const [link, heading] of PAGES) {
    await nav.getByRole('link', { name: link }).click();
    await expect(page.getByRole('heading', { level: 1, name: heading })).toBeVisible();
  }
});

test('configurações exibem políticas vindas do banco em pt-BR', async ({ page }) => {
  await page.goto('/configuracoes');
  const table = page.getByRole('table', { name: 'Políticas de conferência' });
  await expect(table.getByRole('row', { name: /Tolerância de valor \(R\$\)/ })).toContainText(
    'R$ 0,05',
  );
});

test('link para pular ao conteúdo é o primeiro foco do teclado', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('navigation', { name: 'Navegação principal' })).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Pular para o conteúdo' })).toBeFocused();
});

test('rota inexistente mostra página não encontrada (fallback da SPA)', async ({ page }) => {
  await page.goto('/rota-que-nao-existe');
  await expect(
    page.getByRole('heading', { level: 1, name: 'Página não encontrada' }),
  ).toBeVisible();
});

test('página pública de status mostra o ambiente MVP e a API operacional', async ({ page }) => {
  const errors = collectConsoleErrors(page);
  await page.goto('/status');
  await expect(
    page.getByRole('heading', { level: 1, name: 'Guardião Financeiro BR' }),
  ).toBeVisible();
  await expect(page.getByText('MVP', { exact: true })).toBeVisible();
  await expect(page.getByText('Operacional')).toBeVisible();
  expect(errors).toEqual([]);
});
