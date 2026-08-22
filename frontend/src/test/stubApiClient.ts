import { vi } from 'vitest'

import type { ApiClient } from '../shared/api/client.ts'
import type { AccountUser, SiteContent } from '../shared/api/types.ts'

/**
 * The stub API adapter from HotelAppPLAN.md section 3: feature tests inject it
 * through `ApiClientContext` instead of mocking global fetch. Only `client.ts`
 * itself talks to the network; these defaults keep page tests free of fixtures
 * they do not assert on.
 */
export const stubUser: AccountUser = {
  id: 1,
  username: 'mariya',
  email: 'mariya@example.com',
  first_name: 'Мария',
  last_name: 'Иванова',
  phone: '+996700123456',
}

export const stubSiteContent: SiteContent = {
  name: 'Отель Ала-Тоо',
  tagline: 'Тихое место в центре Бишкека',
  about_title: 'О гостинице',
  about_text: 'Текст',
  address: 'Бишкек',
  phone: '+996 312 123 456',
  email: 'stay@example.com',
  footer_text: 'Спокойное бронирование.',
  seo_title: 'Отель Ала-Тоо',
  seo_description: 'Описание',
  hero_slides: [],
  features: [],
}

export function stubApiClient(
  overrides: {
    auth?: Partial<ApiClient['auth']>
    site?: Partial<ApiClient['site']>
    catalog?: Partial<ApiClient['catalog']>
  } = {},
): ApiClient {
  return {
    basePath: '/api/v1',
    auth: {
      register: vi.fn(async () => stubUser),
      login: vi.fn(async () => stubUser),
      logout: vi.fn(async () => undefined),
      me: vi.fn(async () => stubUser),
      updateProfile: vi.fn(async () => stubUser),
      ...overrides.auth,
    },
    site: {
      getContent: vi.fn(async () => stubSiteContent),
      ...overrides.site,
    },
    catalog: {
      listRoomTypes: vi.fn(),
      getRoomType: vi.fn(),
      ...overrides.catalog,
    },
  }
}
