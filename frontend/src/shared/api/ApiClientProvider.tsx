import { type PropsWithChildren } from 'react'

import { apiClient } from './client.ts'
import { ApiClientContext } from './context.ts'

export function ApiClientProvider({ children }: PropsWithChildren) {
  return <ApiClientContext.Provider value={apiClient}>{children}</ApiClientContext.Provider>
}
