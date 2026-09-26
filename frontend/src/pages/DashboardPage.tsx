import type { Readiness } from '../api/types';
import { StatusBadge } from '../components/StatusBadge';
import { Card, ErrorPanel, LoadingState, PageHeader } from '../components/layout';
import { useApiQuery } from '../hooks/useApiQuery';
import { t } from '../i18n/pt-BR';

const KPIS = [
  t.dashboard.kpis.received,
  t.dashboard.kpis.noDivergence,
  t.dashboard.kpis.needsReview,
  t.dashboard.kpis.critical,
  t.dashboard.kpis.possibleDuplicates,
  t.dashboard.kpis.totalProcessed,
  t.dashboard.kpis.exceptionAmount,
];

function SystemStatus() {
  const query = useApiQuery<Readiness>('/api/health/ready');

  if (query.status === 'loading') {
    return <LoadingState />;
  }
  if (query.status === 'error' && query.error.status !== 503) {
    return (
      <ErrorPanel title={t.dashboard.systemStatus} error={query.error} onRetry={query.reload} />
    );
  }
  const data = query.status === 'success' ? query.data : null;
  const apiOk = data?.status === 'ok';
  const dbOk = data?.database === 'ok';

  return (
    <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div>
        <dt className="text-sm text-slate-600">{t.dashboard.api}</dt>
        <dd className="mt-1">
          <StatusBadge tone={apiOk ? 'ok' : 'critical'}>
            {apiOk ? t.status.ok : t.status.unavailable}
          </StatusBadge>
        </dd>
      </div>
      <div>
        <dt className="text-sm text-slate-600">{t.dashboard.database}</dt>
        <dd className="mt-1">
          <StatusBadge tone={dbOk ? 'ok' : 'critical'}>
            {dbOk ? t.status.ok : t.status.unavailable}
          </StatusBadge>
        </dd>
      </div>
      <div>
        <dt className="text-sm text-slate-600">{t.dashboard.schema}</dt>
        <dd className="mt-1 font-mono text-sm">{data?.schema_revision ?? t.common.notAvailable}</dd>
      </div>
      <div>
        <dt className="text-sm text-slate-600">{t.dashboard.version}</dt>
        <dd className="mt-1 font-mono text-sm">{data?.version ?? t.common.notAvailable}</dd>
      </div>
      <div>
        <dt className="text-sm text-slate-600">{t.dashboard.environment}</dt>
        <dd className="mt-1 text-sm">{data?.environment ?? t.common.notAvailable}</dd>
      </div>
    </dl>
  );
}

export function DashboardPage() {
  return (
    <>
      <PageHeader title={t.dashboard.title} description={t.dashboard.subtitle} />
      <section aria-label="Indicadores" className="mb-6">
        <ul className="grid grid-cols-2 gap-4 xl:grid-cols-4">
          {KPIS.map((label) => (
            <li key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-sm text-slate-600">{label}</p>
              <p className="mt-2 text-2xl font-semibold text-slate-400">
                <span aria-hidden="true">{t.common.notAvailable}</span>
                <span className="sr-only">{t.dashboard.kpiNoData}</span>
              </p>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-sm text-slate-600">{t.dashboard.kpiNoData}</p>
      </section>
      <Card title={t.dashboard.systemStatus} titleId="system-status">
        <SystemStatus />
      </Card>
    </>
  );
}
