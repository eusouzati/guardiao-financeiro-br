import type { ReactNode } from 'react';

import { IconAlert, IconCheckCircle, IconInfo, IconXCircle } from './icons';

export type StatusTone = 'ok' | 'info' | 'warning' | 'critical';

const STYLES: Record<StatusTone, { className: string; icon: ReactNode }> = {
  ok: { className: 'bg-ok-50 text-ok-700 ring-ok-700/20', icon: <IconCheckCircle /> },
  info: { className: 'bg-info-50 text-info-700 ring-info-700/20', icon: <IconInfo /> },
  warning: {
    className: 'bg-warning-50 text-warning-700 ring-warning-700/20',
    icon: <IconAlert />,
  },
  critical: {
    className: 'bg-critical-50 text-critical-700 ring-critical-700/20',
    icon: <IconXCircle />,
  },
};

/** Status com ícone + texto: nunca apenas cor (WCAG 1.4.1). */
export function StatusBadge({ tone, children }: { tone: StatusTone; children: ReactNode }) {
  const style = STYLES[tone];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-medium ring-1 ring-inset ${style.className}`}
    >
      {style.icon}
      {children}
    </span>
  );
}
