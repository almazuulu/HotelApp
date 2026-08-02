import { useContext } from 'react'

import { type ApiClient } from './client.ts'
import { ApiClientContext } from './context.ts'

export function useApiClient(): ApiClient {
  const client = useContext(ApiClientContext)

  if (client === null) {
    throw new Error('useApiClient must be used inside ApiClientProvider')
  }

  return client
}
