import { screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import type { Policy } from '../api/types';
import { DEV_ME, mockFetch, renderApp } from '../test/utils';

function policy(overrides: Partial<Policy>): Policy {
  return {
    key: 'k',
    label: 'Política',
    description: 'Descrição',
    type: 'BOOLEAN',
    unit: null,
    value: true,
    default_value: true,
    allowed_values: [],
    minimum: null,
    maximum: null,
    source: 'DEFAULT',
    version: null,
    changed_by: null,
    changed_at: null,
    ...overrides,
  };
}

const POLICIES: Policy[] = [
  policy({ key: 'purchase_order_required', label: 'Exigir pedido de compra' }),
  policy({
    key: 'amount_tolerance_absolute',
    label: 'Tolerância de valor (R$)',
    type: 'DECIMAL',
    unit: 'BRL',
    value: '0.25',
    default_value: '0.05',
    source: 'ORGANIZATION',
    version: 2,
  }),
  policy({
    key: 'amount_tolerance_percentage',
    label: 'Tolerância de valor (%)',
    type: 'DECIMAL',
    unit: 'PERCENT',
    value: '0.50',
    default_value: '0.50',
  }),
  policy({
    key: 'duplicate_window_days',
    label: 'Janela de possível duplicidade (dias)',
    type: 'INTEGER',
    unit: 'DAYS',
    value: 30,
    default_value: 30,
  }),
  policy({
    key: 'purchase_order_missing_severity',
    label: 'Severidade de pedido ausente',
    type: 'SEVERITY',
    value: 'CRITICAL',
    default_value: 'CRITICAL',
  }),
];

describe('Configurações', () => {
  it('lista políticas efetivas com formatação pt-BR e origem', async () => {
    mockFetch({
      '/api/v1/me': { body: DEV_ME },
      '/api/v1/configurations': { body: { items: POLICIES } },
    });
    renderApp('/configuracoes');

    const table = await screen.findByRole('table', { name: 'Políticas de conferência' });
    const row = (name: string) => within(table).getByRole('row', { name: new RegExp(name) });

    expect(within(row('Exigir pedido de compra')).getAllByText('Sim')).toHaveLength(2);
    expect(within(row('Tolerância de valor \\(R\\$\\)')).getByText('R$ 0,25')).toBeInTheDocument();
    expect(within(row('Tolerância de valor \\(R\\$\\)')).getByText('R$ 0,05')).toBeInTheDocument();
    expect(
      within(row('Tolerância de valor \\(R\\$\\)')).getByText('Definido pela organização'),
    ).toBeInTheDocument();
    expect(within(row('Tolerância de valor \\(%\\)')).getAllByText('0,50%')).toHaveLength(2);
    expect(within(row('Janela de possível')).getAllByText('30 dias')).toHaveLength(2);
    expect(within(row('Severidade')).getAllByText('Crítico')).toHaveLength(2);
    expect(
      screen.getByText('Organização Demonstração (fictícia)', { selector: 'dd' }),
    ).toBeVisible();
  });

  it('mostra erro de permissão retornado pelo backend', async () => {
    mockFetch({
      '/api/v1/me': { body: DEV_ME },
      '/api/v1/configurations': {
        status: 403,
        body: {
          code: 'GFB-0403',
          message: 'Você não tem permissão para executar esta operação.',
          request_id: 'req-99999999',
          details: [],
        },
      },
    });
    renderApp('/configuracoes');
    expect(await screen.findByRole('alert')).toHaveTextContent('Você não tem permissão');
  });
});
