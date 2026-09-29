import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import type { Readiness } from '../api/types';
import { DEV_ME, mockFetch, renderApp } from '../test/utils';

const READY: Readiness = {
  status: 'ok',
  version: '0.1.0.dev1',
  environment: 'local',
  database: 'ok',
  schema_revision: '0001',
};

describe('aplicação', () => {
  it('exibe navegação principal com todas as páginas iniciais', async () => {
    mockFetch({ '/api/v1/me': { body: DEV_ME }, '/api/health/ready': { body: READY } });
    renderApp('/');
    const nav = await screen.findByRole('navigation', { name: 'Navegação principal' });
    const labels = within(nav)
      .getAllByRole('link')
      .map((link) => link.textContent);
    expect(labels).toEqual([
      'Painel',
      'Exceções',
      'Documentos',
      'Pedidos',
      'Recebimentos',
      'Fornecedores',
      'Configurações',
    ]);
    expect(within(nav).getByRole('link', { name: 'Painel' })).toHaveAttribute(
      'aria-current',
      'page',
    );
  });

  it('mostra o painel com a pergunta principal e a situação real do sistema', async () => {
    mockFetch({ '/api/v1/me': { body: DEV_ME }, '/api/health/ready': { body: READY } });
    renderApp('/');
    expect(
      await screen.findByRole('heading', {
        level: 1,
        name: 'O que precisa da minha atenção agora?',
      }),
    ).toBeInTheDocument();
    expect(await screen.findByText('0001')).toBeInTheDocument();
    expect(screen.getAllByText('Operacional')).toHaveLength(2);
  });

  it('indica banco indisponível com ícone e texto', async () => {
    mockFetch({
      '/api/v1/me': { body: DEV_ME },
      '/api/health/ready': {
        status: 503,
        body: { ...READY, status: 'unavailable', database: 'unavailable', schema_revision: null },
      },
    });
    renderApp('/');
    expect(await screen.findAllByText('Indisponível')).toHaveLength(2);
  });

  it('exibe aviso de autenticação DEV e link para pular ao conteúdo', async () => {
    mockFetch({ '/api/v1/me': { body: DEV_ME }, '/api/health/ready': { body: READY } });
    renderApp('/');
    expect(await screen.findByRole('note')).toHaveTextContent('autenticação de desenvolvimento');
    expect(screen.getByRole('link', { name: 'Pular para o conteúdo' })).toHaveAttribute(
      'href',
      '#conteudo',
    );
  });

  it('não exibe aviso DEV para usuários autenticados via Entra ID', async () => {
    mockFetch({
      '/api/v1/me': { body: { ...DEV_ME, auth_method: 'ENTRA_ID' } },
      '/api/health/ready': { body: READY },
    });
    renderApp('/');
    await screen.findByRole('navigation', { name: 'Navegação principal' });
    expect(screen.queryByRole('note')).not.toBeInTheDocument();
  });

  it('mostra botão Sair e aviso de perfil ausente no login via Entra (Easy Auth)', async () => {
    mockFetch({
      '/api/v1/me': { body: { ...DEV_ME, auth_method: 'EASY_AUTH', roles: [], permissions: [] } },
      '/api/health/ready': { body: READY },
    });
    renderApp('/');
    expect(await screen.findByRole('link', { name: 'Sair' })).toHaveAttribute(
      'href',
      '/.auth/logout?post_logout_redirect_uri=/',
    );
    expect(screen.getByText('Sem perfil atribuído')).toBeInTheDocument();
    expect(screen.queryByRole('note')).not.toBeInTheDocument();
  });

  it('orienta o usuário quando não autenticado', async () => {
    mockFetch({
      '/api/v1/me': {
        status: 401,
        body: { code: 'GFB-0401', message: 'Autenticação necessária.', request_id: 'r-12345678' },
      },
    });
    renderApp('/');
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Autenticação necessária');
    expect(alert).toHaveTextContent('DEV_AUTH_ENABLED=true');
    expect(alert).toHaveTextContent('r-12345678');
  });

  it.each([
    ['/documentos', 'Documentos', '2'],
    ['/excecoes', 'Exceções', '4 e 5'],
    ['/pedidos', 'Pedidos de compra', '3'],
    ['/recebimentos', 'Recebimentos', '3'],
    ['/fornecedores', 'Fornecedores', '3'],
  ])('página %s mostra estado vazio honesto', async (path, title, sprint) => {
    mockFetch({ '/api/v1/me': { body: DEV_ME } });
    renderApp(path);
    expect(await screen.findByRole('heading', { level: 1, name: title })).toBeInTheDocument();
    expect(screen.getByText(`Módulo previsto para a Sprint ${sprint}.`)).toBeInTheDocument();
  });

  it('navega entre páginas pelo menu', async () => {
    mockFetch({ '/api/v1/me': { body: DEV_ME }, '/api/health/ready': { body: READY } });
    renderApp('/');
    const nav = await screen.findByRole('navigation', { name: 'Navegação principal' });
    await userEvent.click(within(nav).getByRole('link', { name: 'Fornecedores' }));
    expect(await screen.findByRole('heading', { level: 1, name: 'Fornecedores' })).toBeVisible();
  });

  it('exibe página não encontrada para rotas desconhecidas', async () => {
    mockFetch({ '/api/v1/me': { body: DEV_ME } });
    renderApp('/nao-existe');
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Página não encontrada' }),
    ).toBeInTheDocument();
  });
});
