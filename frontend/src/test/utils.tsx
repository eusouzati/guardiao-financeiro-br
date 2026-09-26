import { render } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { vi } from 'vitest';

import type { Me } from '../api/types';
import { routes } from '../app/routes';

/** Respostas por caminho para o ``fetch`` dos testes (não é API simulada da aplicação). */
export type FetchRoutes = Record<string, { status?: number; body: unknown }>;

export function mockFetch(routesByPath: FetchRoutes) {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
    const path = url.replace(/^https?:\/\/[^/]+/, '');
    const route = routesByPath[path];
    if (!route) {
      return Promise.resolve(
        new Response(JSON.stringify({ code: 'GFB-0404', message: 'x', request_id: null }), {
          status: 404,
        }),
      );
    }
    return Promise.resolve(
      new Response(JSON.stringify(route.body), {
        status: route.status ?? 200,
        headers: { 'Content-Type': 'application/json', 'x-request-id': 'req-test-0001' },
      }),
    );
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

export const DEV_ME: Me = {
  user_id: 'dev-user',
  display_name: 'Usuário de desenvolvimento',
  auth_method: 'DEV',
  roles: ['ADMIN'],
  permissions: ['DASHBOARD_READ', 'CONFIGURATION_READ'],
  organization: {
    id: '00000000-0000-4000-8000-000000000001',
    legal_name: 'Organização Demonstração (fictícia)',
    tax_id: null,
  },
};

export function renderApp(path = '/') {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  return render(<RouterProvider router={router} />);
}
