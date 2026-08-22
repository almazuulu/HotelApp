import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, apiClient } from './client.ts'

type FetchLike = (url: string, init: RequestInit) => Promise<Response>

const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } })

const okFetch = (body: unknown) => vi.fn<FetchLike>(async () => jsonResponse(body))

afterEach(() => {
  vi.unstubAllGlobals()
  document.cookie = 'csrftoken=; Max-Age=0'
})

describe('apiClient network adapter', () => {
  it('sends GET requests to the versioned base path with session credentials and no CSRF header', async () => {
    const fetchMock = okFetch({ name: 'Отель Ала-Тоо' })
    vi.stubGlobal('fetch', fetchMock)

    await apiClient.site.getContent()

    expect(fetchMock).toHaveBeenCalledOnce()
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/site/')
    expect(init.credentials).toBe('include')
    expect(new Headers(init.headers).get('x-csrftoken')).toBeNull()
    expect(new Headers(init.headers).get('content-type')).toBeNull()
  })

  it('builds the catalog query from capacity and amenity filters', async () => {
    const fetchMock = okFetch([])
    vi.stubGlobal('fetch', fetchMock)

    await apiClient.catalog.listRoomTypes({ adults: 2, children: 1, amenity: ['breakfast', 'wifi'] })

    expect(fetchMock.mock.calls[0][0]).toBe(
      '/api/v1/room-types/?adults=2&children=1&amenity=breakfast&amenity=wifi',
    )
  })

  it('encodes the room type slug into the detail path', async () => {
    const fetchMock = okFetch({ slug: 'a b' })
    vi.stubGlobal('fetch', fetchMock)

    await apiClient.catalog.getRoomType('a b')

    expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/room-types/a%20b/')
  })

  it('prefetches the CSRF cookie and sends its decoded token on unsafe methods', async () => {
    document.cookie = 'csrftoken=t0k3n%2F42'
    const fetchMock = okFetch({ id: 1 })
    vi.stubGlobal('fetch', fetchMock)

    await apiClient.auth.login({ username: 'mariya', password: 'secret' })

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/csrf/')
    const [url, init] = fetchMock.mock.calls[1]
    expect(url).toBe('/api/v1/auth/login/')
    expect(new Headers(init.headers).get('x-csrftoken')).toBe('t0k3n/42')
    expect(new Headers(init.headers).get('content-type')).toBe('application/json')
    expect(init.credentials).toBe('include')
  })

  it('omits the CSRF header but keeps the prefetch when the cookie is missing', async () => {
    const fetchMock = okFetch({ id: 1 })
    vi.stubGlobal('fetch', fetchMock)

    await apiClient.auth.register({
      username: 'mariya',
      email: 'mariya@example.com',
      first_name: 'Мария',
      last_name: 'Иванова',
      phone: '+996700123456',
      password: 'secret',
    })

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(new Headers(fetchMock.mock.calls[1][1].headers).get('x-csrftoken')).toBeNull()
  })

  it('serializes the PATCH body for profile updates', async () => {
    document.cookie = 'csrftoken=t0k3n'
    const fetchMock = okFetch({ id: 1 })
    vi.stubGlobal('fetch', fetchMock)

    await apiClient.auth.updateProfile({ first_name: 'Анна' })

    const [url, init] = fetchMock.mock.calls[1]
    expect(url).toBe('/api/v1/auth/me/')
    expect(init.method).toBe('PATCH')
    expect(init.body).toBe('{"first_name":"Анна"}')
  })

  it('rejects with a typed ApiError carrying the envelope code and field errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn<FetchLike>(
        async () =>
          jsonResponse(
            {
              code: 'VALIDATION_ERROR',
              message: 'Некорректные данные запроса.',
              errors: { email: ['Введите корректный email.'] },
            },
            400,
          ),
      ),
    )

    const failure = apiClient.auth.register({
      username: 'mariya',
      email: 'mariya@example.com',
      first_name: 'Мария',
      last_name: 'Иванова',
      phone: '+996700123456',
      password: 'secret',
    })

    await expect(failure).rejects.toBeInstanceOf(ApiError)
    await expect(failure).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      message: 'Некорректные данные запроса.',
      errors: { email: ['Введите корректный email.'] },
    })
  })

  it('falls back to a generic ApiError when the error body is not JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn<FetchLike>(
        async () =>
          new Response('<html>Bad Gateway</html>', {
            status: 502,
            headers: { 'content-type': 'text/html' },
          }),
      ),
    )

    await expect(apiClient.site.getContent()).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      message: 'Сервер вернул неожиданный ответ.',
    })
  })

  it('falls back when a JSON error body does not use the envelope', async () => {
    vi.stubGlobal('fetch', vi.fn<FetchLike>(async () => jsonResponse({ detail: 'Not found.' }, 404)))

    await expect(apiClient.catalog.getRoomType('unknown')).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      message: 'Сервер вернул неожиданный ответ.',
    })
  })

  it('returns undefined for 204 responses', async () => {
    const fetchMock = vi.fn<FetchLike>(async () => new Response(null, { status: 204 }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiClient.auth.logout()).resolves.toBeUndefined()
  })
})
