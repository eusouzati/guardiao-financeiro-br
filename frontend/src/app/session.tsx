import type { ReactNode } from 'react';

import type { Me } from '../api/types';
import { ErrorPanel, LoadingState } from '../components/layout';
import { useApiQuery } from '../hooks/useApiQuery';
import { t } from '../i18n/pt-BR';
import { SessionContext } from './sessionContext';

export function SessionProvider({ children }: { children: ReactNode }) {
  const query = useApiQuery<Me>('/api/v1/me');

  if (query.status === 'loading') {
    return (
      <main className="mx-auto max-w-xl p-8">
        <LoadingState label={t.session.loading} />
      </main>
    );
  }

  if (query.status === 'error') {
    const { error } = query;
    const title =
      error.status === 401
        ? t.session.notAuthenticatedTitle
        : error.code === 'GFB-1001'
          ? t.session.orgNotInitializedTitle
          : t.session.genericErrorTitle;
    return (
      <main className="mx-auto max-w-xl p-8">
        <ErrorPanel
          title={title}
          error={error}
          onRetry={query.reload}
          {...(error.status === 401 ? { help: t.session.notAuthenticatedHelp } : {})}
        />
      </main>
    );
  }

  return <SessionContext value={query.data}>{children}</SessionContext>;
}
