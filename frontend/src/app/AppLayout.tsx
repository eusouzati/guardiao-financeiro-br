import { useState, type ReactNode } from 'react';
import { NavLink, Outlet } from 'react-router';

import {
  IconAlert,
  IconBox,
  IconBuilding,
  IconCart,
  IconClose,
  IconDashboard,
  IconDocument,
  IconMenu,
  IconSettings,
  ShieldLogo,
} from '../components/icons';
import { t } from '../i18n/pt-BR';
import { useSession } from './sessionContext';

/** Logout do Easy Auth (Container Apps): encerra a sessão e volta para a raiz. */
const LOGOUT_URL = '/.auth/logout?post_logout_redirect_uri=/';

interface NavItem {
  to: string;
  label: string;
  icon: ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: t.nav.dashboard, icon: <IconDashboard /> },
  { to: '/excecoes', label: t.nav.exceptions, icon: <IconAlert /> },
  { to: '/documentos', label: t.nav.documents, icon: <IconDocument /> },
  { to: '/pedidos', label: t.nav.purchaseOrders, icon: <IconCart /> },
  { to: '/recebimentos', label: t.nav.receipts, icon: <IconBox /> },
  { to: '/fornecedores', label: t.nav.suppliers, icon: <IconBuilding /> },
  { to: '/configuracoes', label: t.nav.settings, icon: <IconSettings /> },
];

function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav aria-label={t.mainNavigation}>
      <ul className="space-y-1">
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.to === '/'}
              {...(onNavigate ? { onClick: onNavigate } : {})}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${
                  isActive
                    ? 'bg-brand-700 text-white'
                    : 'text-brand-100 hover:bg-brand-800 hover:text-white'
                }`
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function Brand() {
  return (
    <div className="flex items-center gap-2 px-3 py-4 text-white">
      <ShieldLogo className="size-8 text-brand-100" />
      <div>
        <p className="text-sm leading-tight font-semibold">{t.appName}</p>
        <p className="text-xs leading-tight text-brand-100">{t.appTagline}</p>
      </div>
    </div>
  );
}

export function AppLayout() {
  const session = useSession();
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => {
    setMenuOpen(false);
  };

  return (
    <div className="min-h-screen">
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-brand-800"
      >
        {t.skipToContent}
      </a>

      {session.auth_method === 'DEV' ? (
        <div
          role="note"
          className="bg-warning-50 px-4 py-2 text-center text-sm font-medium text-warning-700"
        >
          {t.devAuthBanner}
        </div>
      ) : null}

      <div className="flex">
        <aside className="hidden w-64 shrink-0 bg-brand-900 px-3 lg:block lg:min-h-screen">
          <Brand />
          <Navigation />
        </aside>

        {menuOpen ? (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              aria-label={t.closeMenu}
              className="absolute inset-0 bg-slate-900/50"
              onClick={closeMenu}
            />
            <aside className="relative h-full w-72 bg-brand-900 px-3">
              <div className="flex items-center justify-between">
                <Brand />
                <button
                  type="button"
                  onClick={closeMenu}
                  aria-label={t.closeMenu}
                  className="rounded-md p-2 text-brand-100 hover:text-white"
                >
                  <IconClose />
                </button>
              </div>
              <Navigation onNavigate={closeMenu} />
            </aside>
          </div>
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-3 lg:px-8">
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="rounded-md p-2 text-slate-700 hover:bg-slate-100 lg:hidden"
                aria-label={t.openMenu}
                aria-expanded={menuOpen}
                onClick={() => {
                  setMenuOpen(true);
                }}
              >
                <IconMenu />
              </button>
              <p className="text-sm font-medium text-slate-700">
                {session.organization.legal_name}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-slate-900">{session.display_name}</p>
                <p className="text-xs text-slate-600">
                  {session.roles.length > 0 ? session.roles.join(', ') : t.noRoleAssigned}
                </p>
              </div>
              {session.auth_method === 'EASY_AUTH' ? (
                <a
                  href={LOGOUT_URL}
                  className="rounded-md px-3 py-1.5 text-sm font-medium text-brand-700 ring-1 ring-slate-300 hover:bg-slate-50"
                >
                  {t.signOut}
                </a>
              ) : null}
            </div>
          </header>

          <main id="conteudo" tabIndex={-1} className="flex-1 px-4 py-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
