/**
 * Boundary placeholder for the typed API client introduced in issue #30.
 *
 * Features receive this adapter through context; they do not import network
 * primitives. The current scaffold deliberately makes no application request.
 */
export interface ApiClient {
  readonly basePath: '/api/v1'
}

export const apiClient: ApiClient = {
  basePath: '/api/v1',
}
