import type { RouteObject } from 'react-router';

import { DashboardPage } from '../pages/DashboardPage';
import {
  DocumentsPage,
  ExceptionsPage,
  PurchaseOrdersPage,
  ReceiptsPage,
  SuppliersPage,
} from '../pages/ModulePages';
import { NotFoundPage } from '../pages/NotFoundPage';
import { SettingsPage } from '../pages/SettingsPage';
import { AppLayout } from './AppLayout';
import { SessionProvider } from './session';

export const routes: RouteObject[] = [
  {
    element: (
      <SessionProvider>
        <AppLayout />
      </SessionProvider>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'excecoes', element: <ExceptionsPage /> },
      { path: 'documentos', element: <DocumentsPage /> },
      { path: 'pedidos', element: <PurchaseOrdersPage /> },
      { path: 'recebimentos', element: <ReceiptsPage /> },
      { path: 'fornecedores', element: <SuppliersPage /> },
      { path: 'configuracoes', element: <SettingsPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
];
