import { useQuery } from '@tanstack/react-query'

import { useApiClient } from '../../shared/api/useApiClient.ts'

export const accountQueryKey = ['accounts', 'me'] as const

export function useCurrentUser() {
  const api = useApiClient()

  return useQuery({
    queryKey: accountQueryKey,
    queryFn: () => api.auth.me(),
  })
}
