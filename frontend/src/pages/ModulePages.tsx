import { PageHeader, UpcomingModule } from '../components/layout';
import { t } from '../i18n/pt-BR';

type ModuleKey = 'documents' | 'exceptions' | 'purchaseOrders' | 'receipts' | 'suppliers';

/**
 * Páginas de módulos ainda não implementados. Mostram o propósito do módulo e um estado
 * vazio honesto — não há API simulada nem dados fictícios na interface.
 */
function ModulePage({ module }: { module: ModuleKey }) {
  const content = t.modules[module];
  return (
    <>
      <PageHeader title={content.title} description={content.description} />
      <UpcomingModule message={content.empty} sprint={content.sprint} />
    </>
  );
}

export const DocumentsPage = () => <ModulePage module="documents" />;
export const ExceptionsPage = () => <ModulePage module="exceptions" />;
export const PurchaseOrdersPage = () => <ModulePage module="purchaseOrders" />;
export const ReceiptsPage = () => <ModulePage module="receipts" />;
export const SuppliersPage = () => <ModulePage module="suppliers" />;
