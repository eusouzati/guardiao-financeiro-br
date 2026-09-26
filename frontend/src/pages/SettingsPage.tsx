import type { ConfigurationResponse, Policy } from '../api/types';
import { useSession } from '../app/sessionContext';
import { StatusBadge } from '../components/StatusBadge';
import { Card, ErrorPanel, LoadingState, PageHeader } from '../components/layout';
import { useApiQuery } from '../hooks/useApiQuery';
import { t } from '../i18n/pt-BR';
import { formatPolicyValue } from '../lib/policyFormat';

function PoliciesTable({ items }: { items: Policy[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <caption className="sr-only">{t.settings.policies}</caption>
        <thead>
          <tr className="text-left text-slate-600">
            <th scope="col" className="py-2 pr-4 font-medium">
              {t.settings.columns.policy}
            </th>
            <th scope="col" className="py-2 pr-4 font-medium">
              {t.settings.columns.value}
            </th>
            <th scope="col" className="py-2 pr-4 font-medium">
              {t.settings.columns.default}
            </th>
            <th scope="col" className="py-2 font-medium">
              {t.settings.columns.source}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((policy) => (
            <tr key={policy.key} className="align-top">
              <th scope="row" className="py-3 pr-4 text-left font-normal">
                <span className="font-medium text-slate-900">{policy.label}</span>
                <span className="block text-slate-600">{policy.description}</span>
              </th>
              <td className="py-3 pr-4 font-medium whitespace-nowrap text-slate-900">
                {formatPolicyValue(policy, policy.value)}
              </td>
              <td className="py-3 pr-4 whitespace-nowrap text-slate-600">
                {formatPolicyValue(policy, policy.default_value)}
              </td>
              <td className="py-3 whitespace-nowrap">
                <StatusBadge tone={policy.source === 'DEFAULT' ? 'info' : 'ok'}>
                  {t.settings.source[policy.source]}
                </StatusBadge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SettingsPage() {
  const session = useSession();
  const query = useApiQuery<ConfigurationResponse>('/api/v1/configurations');

  return (
    <>
      <PageHeader title={t.settings.title} description={t.settings.description} />
      <div className="space-y-6">
        <Card title={t.settings.organization} titleId="org-title">
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-slate-600">{t.settings.legalName}</dt>
              <dd className="mt-1 font-medium">{session.organization.legal_name}</dd>
            </div>
            <div>
              <dt className="text-sm text-slate-600">{t.settings.taxId}</dt>
              <dd className="mt-1 font-medium">
                {session.organization.tax_id ?? t.settings.notInformed}
              </dd>
            </div>
          </dl>
        </Card>
        <Card title={t.settings.policies} titleId="policies-title">
          {query.status === 'loading' ? <LoadingState /> : null}
          {query.status === 'error' ? (
            <ErrorPanel title={t.settings.policies} error={query.error} onRetry={query.reload} />
          ) : null}
          {query.status === 'success' ? <PoliciesTable items={query.data.items} /> : null}
        </Card>
      </div>
    </>
  );
}
