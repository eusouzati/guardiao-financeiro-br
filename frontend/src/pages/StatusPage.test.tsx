import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import type { Readiness } from '../api/types';
import { mockFetch, renderApp } from '../test/utils';

const READY: Readiness = {
  status: 'ok',
  version: '0.1.0.dev1',
  environment: 'mvp',
  database: 'ok',
  schema_revision: '0001',
};

describe('página de status', () => {
  it('é pública e mostra nome, ambiente MVP e API operacional', async () => {
    const fetchMock = mockFetch({ '/api/health/ready': { body: READY } });
    renderApp('/status');
    expect(
      screen.getByRole('heading', { level: 1, name: 'Guardião Financeiro BR' }),
    ).toBeInTheDocument();
    expect(screen.getByText('MVP')).toBeInTheDocument();
    expect(screen.getByText('Status da API')).toBeInTheDocument();
    expect(await screen.findByText('Operacional')).toBeInTheDocument();
    expect(screen.getByText('0.1.0.dev1')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/health/ready');
  });

  it('mostra API indisponível quando a verificação falha', async () => {
    mockFetch({
      '/api/health/ready': {
        status: 503,
        body: { ...READY, status: 'unavailable', database: 'unavailable', schema_revision: null },
      },
    });
    renderApp('/status');
    expect(await screen.findByText('Indisponível')).toBeInTheDocument();
    expect(screen.queryByText('0.1.0.dev1')).not.toBeInTheDocument();
  });

  it('é oferecida quando o usuário não está autenticado', async () => {
    mockFetch({
      '/api/v1/me': {
        status: 401,
        body: { code: 'GFB-0401', message: 'Autenticação necessária.', request_id: null },
      },
    });
    renderApp('/');
    expect(await screen.findByRole('link', { name: 'Ver status da aplicação' })).toHaveAttribute(
      'href',
      '/status',
    );
  });
});
