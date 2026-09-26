import { createContext, useContext } from 'react';

import type { Me } from '../api/types';

export const SessionContext = createContext<Me | null>(null);

/** Usuário atual. Permissões servem só para UX: o backend decide a autorização. */
export function useSession(): Me {
  const session = useContext(SessionContext);
  if (!session) {
    throw new Error('useSession deve ser usado dentro de SessionProvider');
  }
  return session;
}
