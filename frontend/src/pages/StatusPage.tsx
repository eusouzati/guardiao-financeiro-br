import type { Readiness } from '../api/types';
import { ShieldLogo } from '../components/icons';
import { StatusBadge } from '../components/StatusBadge';
import { useApiQuery } from '../hooks/useApiQuery';
import { t } from '../i18n/pt-BR';

/**
 * Página pública de status (Sprint 0): identifica a aplicação e o ambiente e mostra se a
 * API responde. Não exige sessão e não exibe dados de negócio nem detalhes internos.
 */
export function StatusPage() {
  const readiness = useApiQuery<Readiness>('/api/health/ready');

  let apiStatus;
  if (readiness.status === 'loading') {
    apiStatus = <StatusBadge tone="info">{t.statusPage.checking}</StatusBadge>;
  } else if (readiness.status === 'success' && readiness.data.status === 'ok') {
    apiStatus = <StatusBadge tone="ok">{t.status.ok}</StatusBadge>;
  } else {
    apiStatus = <StatusBadge tone="critical">{t.status.unavailable}</StatusBadge>;
  }

  return (
    <main id="conteudo" className="mx-auto flex min-h-screen max-w-xl flex-col justify-center p-8">
      <div className="rounded-lg bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="flex items-center gap-3">
          <ShieldLogo className="size-10 text-brand-700" />
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{t.appName}</h1>
            <p className="text-sm text-slate-600">{t.appTagline}</p>
          </div>
        </div>
        <p className="mt-6">
          <span className="rounded-md bg-brand-50 px-2 py-1 text-sm font-semibold text-brand-800 ring-1 ring-brand-700/20">
            {t.statusPage.environment}
          </span>
        </p>
        <dl className="mt-6 space-y-3">
          <div className="flex items-center justify-between gap-4">
            <dt className="text-sm font-medium text-slate-700">{t.statusPage.apiStatus}</dt>
            <dd aria-live="polite">{apiStatus}</dd>
          </div>
          {readiness.status === 'success' ? (
            <div className="flex items-center justify-between gap-4">
              <dt className="text-sm font-medium text-slate-700">{t.statusPage.version}</dt>
              <dd className="text-sm text-slate-900">{readiness.data.version}</dd>
            </div>
          ) : null}
        </dl>
        {readiness.status === 'loading' ? null : (
          <button
            type="button"
            onClick={readiness.reload}
            className="mt-6 rounded-md px-3 py-1.5 text-sm font-medium text-brand-700 ring-1 ring-slate-300 hover:bg-slate-50"
          >
            {t.statusPage.refresh}
          </button>
        )}
      </div>
    </main>
  );
}
