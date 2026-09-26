import { useCallback, useEffect, useState } from 'react';

import { ApiError, apiGet } from '../api/client';

type Settled<T> = { status: 'success'; data: T } | { status: 'error'; error: ApiError };

export type QueryState<T> = { status: 'loading' } | Settled<T>;

/**
 * Busca simples com cancelamento. Suficiente para a Sprint 1 (sem biblioteca de cache).
 * O estado de carregamento é derivado da chave da requisição (sem setState síncrono no efeito).
 */
export function useApiQuery<T>(path: string): QueryState<T> & { reload: () => void } {
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{ key: string; state: Settled<T> } | null>(null);
  const key = `${path}#${String(attempt)}`;

  useEffect(() => {
    const controller = new AbortController();
    apiGet<T>(path, controller.signal)
      .then((data) => {
        setResult({ key, state: { status: 'success', data } });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        setResult({
          key,
          state: {
            status: 'error',
            error:
              error instanceof ApiError
                ? error
                : new ApiError(0, 'UNKNOWN', 'Erro inesperado ao carregar os dados.', null),
          },
        });
      });
    return () => {
      controller.abort();
    };
  }, [path, key]);

  const reload = useCallback(() => {
    setAttempt((value) => value + 1);
  }, []);

  const state: QueryState<T> = result?.key === key ? result.state : { status: 'loading' };
  return { ...state, reload };
}
