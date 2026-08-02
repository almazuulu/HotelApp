import { useQuery } from '@tanstack/react-query'

import { useApiClient } from '../../shared/api/useApiClient.ts'

export const siteContentQueryKey = ['site', 'content'] as const

export function useSiteContent() {
  const api = useApiClient()

  return useQuery({
    queryKey: siteContentQueryKey,
    queryFn: () => api.site.getContent(),
    staleTime: 5 * 60 * 1000,
  })
}
