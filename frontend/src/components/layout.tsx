import type { ReactNode } from 'react';

import { ApiError } from '../api/client';
import { t } from '../i18n/pt-BR';
import { IconConstruction } from './icons';

export function PageHeader({ title, description }: { title: string; description?: string }) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{title}</h1>
      {description ? <p className="mt-1 max-w-3xl text-slate-600">{description}</p> : null}
    </header>
  );
}

export function Card({
  title,
  children,
  titleId,
}: {
  title?: string;
  children: ReactNode;
  titleId?: string;
}) {
  return (
    <section
      className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
      {...(titleId ? { 'aria-labelledby': titleId } : {})}
    >
      {title ? (
        <h2 id={titleId} className="mb-4 text-base font-semibold text-slate-900">
          {title}
        </h2>
      ) : null}
      {children}
    </section>
  );
}

export function LoadingState({ label = t.common.loading }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="py-8 text-slate-600">
      {label}
    </div>
  );
}

export function ErrorPanel({
  title,
  error,
  onRetry,
  help,
}: {
  title: string;
  error: ApiError;
  onRetry?: () => void;
  help?: string;
}) {
  return (
    <div role="alert" className="rounded-lg border border-critical-700/30 bg-critical-50 p-5">
      <h2 className="font-semibold text-critical-700">{title}</h2>
      <p className="mt-1 text-slate-800">{error.message}</p>
      {help ? <p className="mt-2 text-sm text-slate-700">{help}</p> : null}
      {error.requestId ? (
        <p className="mt-2 text-sm text-slate-600">
          {t.common.requestId}: <code className="font-mono">{error.requestId}</code>
        </p>
      ) : null}
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-md bg-white px-3 py-1.5 text-sm font-medium text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50"
        >
          {t.common.retry}
        </button>
      ) : null}
    </div>
  );
}

/** Estado vazio honesto para módulos ainda não implementados (sem dados simulados). */
export function UpcomingModule({ message, sprint }: { message: string; sprint: string }) {
  return (
    <div className="flex flex-col items-center rounded-lg border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
      <span className="text-slate-500">
        <IconConstruction />
      </span>
      <p className="mt-3 font-medium text-slate-800">{message}</p>
      <p className="mt-1 text-sm text-slate-600">{t.modules.upcoming(sprint)}</p>
    </div>
  );
}
