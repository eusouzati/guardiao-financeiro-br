import type { ApiErrorBody } from './types';

/** Erro normalizado da API, com código estável e mensagem pt-BR (docs/error-codes.md). */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string | null;

  constructor(status: number, code: string, message: string, requestId: string | null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.requestId = requestId;
  }
}

export const NETWORK_ERROR_CODE = 'NETWORK';

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as Record<string, unknown>).code === 'string' &&
    typeof (value as Record<string, unknown>).message === 'string'
  );
}

/**
 * GET em uma rota da API na mesma origem. Aceita também respostas de erro não-JSON
 * (ex.: 502 do proxy) e falhas de rede, sempre devolvendo ``ApiError`` em pt-BR.
 */
export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
      ...(signal ? { signal } : {}),
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error;
    }
    throw new ApiError(
      0,
      NETWORK_ERROR_CODE,
      'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.',
      null,
    );
  }

  const requestId = response.headers.get('x-request-id');
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    if (isApiErrorBody(body)) {
      throw new ApiError(response.status, body.code, body.message, body.request_id ?? requestId);
    }
    throw new ApiError(
      response.status,
      `HTTP-${String(response.status)}`,
      'O servidor não conseguiu processar a solicitação. Tente novamente em instantes.',
      requestId,
    );
  }
  return body as T;
}
