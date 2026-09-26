import { Link } from 'react-router';

import { PageHeader } from '../components/layout';
import { t } from '../i18n/pt-BR';

export function NotFoundPage() {
  return (
    <>
      <PageHeader title={t.notFound.title} description={t.notFound.description} />
      <Link to="/" className="font-medium text-brand-700 underline underline-offset-2">
        {t.notFound.back}
      </Link>
    </>
  );
}
