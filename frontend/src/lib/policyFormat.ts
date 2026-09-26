import type { Policy } from '../api/types';
import { t } from '../i18n/pt-BR';
import { formatCurrencyBRL, formatDecimal, formatPercent } from './format';

/** Formata o valor de uma política conforme tipo e unidade (somente exibição). */
export function formatPolicyValue(policy: Policy, value: Policy['value']): string {
  if (typeof value === 'boolean') {
    return value ? t.common.yes : t.common.no;
  }
  if (policy.type === 'SEVERITY') {
    const labels: Record<string, string> = {
      INFO: t.status.info,
      WARNING: t.status.warning,
      CRITICAL: t.status.critical,
    };
    return labels[String(value)] ?? String(value);
  }
  const text = String(value);
  switch (policy.unit) {
    case 'BRL':
      return formatCurrencyBRL(text);
    case 'PERCENT':
      return formatPercent(text);
    case null:
      return formatDecimal(text);
    default: {
      const unit = t.settings.units[policy.unit];
      return unit ? `${formatDecimal(text)} ${unit}` : formatDecimal(text);
    }
  }
}
