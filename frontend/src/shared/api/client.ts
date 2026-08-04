import type {
  AccountUser,
  ApiErrorCode,
  ApiErrorPayload,
  LoginPayload,
  ProfileUpdatePayload,
  RegistrationPayload,
  RoomType,
  RoomTypeFilters,
  SiteContent,
} from './types.ts'

const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export class ApiError extends Error {
  readonly code: ApiErrorCode
  readonly errors: unknown

  constructor(payload: ApiErrorPayload) {
    super(payload.message)
    this.name = 'ApiError'
    this.code = payload.code
    this.errors = payload.errors
  }
}

function isApiErrorPayload(value: unknown): value is ApiErrorPayload {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const candidate = value as Record<string, unknown>
  return typeof candidate.code === 'string' && typeof candidate.message === 'string'
}

function csrfToken(): string | undefined {
  return document.cookie
    .split('; ')
    .find((entry) => entry.startsWith('csrftoken='))
    ?.split('=')[1]
}

async function decodeError(response: Response): Promise<ApiError> {
  const body: unknown = await response.json().catch(() => null)
  if (isApiErrorPayload(body)) {
    return new ApiError(body)
  }

  return new ApiError({
    code: 'VALIDATION_ERROR',
    message: 'Сервер вернул неожиданный ответ.',
    errors: null,
  })
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = init.method?.toUpperCase() ?? 'GET'
  if (UNSAFE_METHODS.has(method)) {
    await fetch('/api/v1/csrf/', { credentials: 'include' })
  }

  const headers = new Headers(init.headers)
  if (init.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }

  const token = csrfToken()
  if (UNSAFE_METHODS.has(method) && token !== undefined) {
    headers.set('X-CSRFToken', decodeURIComponent(token))
  }

  const response = await fetch(`/api/v1${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })
  if (!response.ok) {
    throw await decodeError(response)
  }
  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

function roomTypeQuery(filters: RoomTypeFilters): string {
  const params = new URLSearchParams()
  if (filters.adults !== undefined) {
    params.set('adults', String(filters.adults))
  }
  if (filters.children !== undefined) {
    params.set('children', String(filters.children))
  }
  for (const slug of filters.amenity ?? []) {
    params.append('amenity', slug)
  }

  const query = params.toString()
  return query === '' ? '' : `?${query}`
}

export interface ApiClient {
  readonly basePath: '/api/v1'
  readonly auth: {
    register(payload: RegistrationPayload): Promise<AccountUser>
    login(payload: LoginPayload): Promise<AccountUser>
    logout(): Promise<void>
    me(): Promise<AccountUser>
    updateProfile(payload: ProfileUpdatePayload): Promise<AccountUser>
  }
  readonly site: {
    getContent(): Promise<SiteContent>
  }
  readonly catalog: {
    listRoomTypes(filters?: RoomTypeFilters): Promise<RoomType[]>
    getRoomType(slug: string): Promise<RoomType>
  }
}

export const apiClient: ApiClient = {
  basePath: '/api/v1',
  auth: {
    register: (payload) => request<AccountUser>('/auth/register/', { method: 'POST', body: JSON.stringify(payload) }),
    login: (payload) => request<AccountUser>('/auth/login/', { method: 'POST', body: JSON.stringify(payload) }),
    logout: () => request<void>('/auth/logout/', { method: 'POST' }),
    me: () => request<AccountUser>('/auth/me/'),
    updateProfile: (payload) =>
      request<AccountUser>('/auth/me/', { method: 'PATCH', body: JSON.stringify(payload) }),
  },
  site: {
    getContent: () => request<SiteContent>('/site/'),
  },
  catalog: {
    listRoomTypes: (filters = {}) => request<RoomType[]>(`/room-types/${roomTypeQuery(filters)}`),
    getRoomType: (slug) => request<RoomType>(`/room-types/${encodeURIComponent(slug)}/`),
  },
}
