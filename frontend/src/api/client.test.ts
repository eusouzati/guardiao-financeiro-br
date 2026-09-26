import { describe, expect, it, vi } from 'vitest';

import { ApiError, apiGet, NETWORK_ERROR_CODE } from './client';

function stubFetch(response: Response | Error) {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => (response instanceof Error ? Promise.reject(response) : Promise.resolve(response))),
  );
}

describe('apiGet', () => {
  it('retorna o corpo JSON em caso de sucesso', async () => {
    stubFetch(new Response(JSON.stringify({ status: 'ok' }), { status: 200 }));
    await expect(apiGet('/api/health/live')).resolves.toEqual({ status: 'ok' });
  });

  it('normaliza erros padronizados da API', async () => {
    stubFetch(
      new Response(
        JSON.stringify({
          code: 'GFB-0403',
          message: 'Você não tem permissão para executar esta operação.',
          request_id: 'abc12345',
          details: [],
        }),
        { status: 403 },
      ),
    );
    const error = await apiGet('/api/v1/audit/events').catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 403, code: 'GFB-0403', requestId: 'abc12345' });
  });

  it('trata respostas de erro sem JSON (ex.: proxy)', async () => {
    stubFetch(
      new Response('<html>Bad Gateway</html>', {
        status: 502,
        headers: { 'x-request-id': 'proxy-1234' },
      }),
    );
    const error = await apiGet('/api/v1/me').catch((e: unknown) => e);
    expect(error).toMatchObject({ status: 502, code: 'HTTP-502', requestId: 'proxy-1234' });
    expect((error as ApiError).message).not.toContain('html');
  });

  it('converte falha de rede em mensagem compreensível', async () => {
    stubFetch(new TypeError('Failed to fetch'));
    const error = await apiGet('/api/v1/me').catch((e: unknown) => e);
    expect(error).toMatchObject({ status: 0, code: NETWORK_ERROR_CODE });
  });
});
