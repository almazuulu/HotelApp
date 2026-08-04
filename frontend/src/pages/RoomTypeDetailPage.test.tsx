import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi } from 'vitest'

import { RoomTypeDetailPage } from './RoomTypeDetailPage.tsx'
import { ApiError, type ApiClient } from '../shared/api/client.ts'
import { ApiClientContext } from '../shared/api/context.ts'
import type { RoomType, SiteContent } from '../shared/api/types.ts'

const siteContent: SiteContent = {
  name: 'Отель Ала-Тоо',
  tagline: 'Тихое место в центре Бишкека',
  about_title: 'Добро пожаловать в Отель Ала-Тоо',
  about_text: 'Здесь начинается спокойное путешествие.',
  address: 'ул. Токтогула, 101, Бишкек',
  phone: '+996 312 123 456',
  email: 'stay@example.com',
  check_in_time: '14:00:00',
  check_out_time: '12:00:00',
  footer_text: 'Спокойное бронирование.',
  seo_title: 'Отель Ала-Тоо — Бишкек',
  seo_description: 'Гостиница в центре Бишкека.',
  seo_keywords: 'отель, Бишкек',
  hero_slides: [],
  features: [],
}

const deluxe: RoomType = {
  name: 'Делюкс с видом на горы',
  slug: 'delux-mountain',
  description: 'Просторный номер с панорамным видом на Ала-Тоо и балконом.',
  price_per_night: '120.00',
  max_adults: 2,
  max_children: 1,
  area_sqm: '28.00',
  bed_count: 1,
  confirmation_mode: 'automatic',
  amenities: [
    { name: 'Wi-Fi', slug: 'wifi' },
    { name: 'Завтрак', slug: 'breakfast' },
  ],
  images: [{ image_url: 'https://example.com/room-1.jpg', alt_text: 'Кровать у окна с видом на горы' }],
}

function createApiClient(getRoomType: ApiClient['catalog']['getRoomType']): ApiClient {
  return {
    basePath: '/api/v1',
    auth: {
      register: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
      me: vi.fn(),
      updateProfile: vi.fn(),
    },
    site: { getContent: vi.fn(async () => siteContent) },
    catalog: { listRoomTypes: vi.fn(), getRoomType },
  }
}

function renderDetail(client: ApiClient, slug = 'delux-mountain') {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ApiClientContext.Provider value={client}>
        <MemoryRouter initialEntries={[`/rooms/${slug}`]}>
          <Routes>
            <Route path="/rooms/:slug" element={<RoomTypeDetailPage />} />
          </Routes>
        </MemoryRouter>
      </ApiClientContext.Provider>
    </QueryClientProvider>,
  )
}

describe('RoomTypeDetailPage', () => {
  it('renders category details and gallery alt text through the API adapter', async () => {
    renderDetail(createApiClient(vi.fn(async () => deluxe)))

    expect(await screen.findByRole('heading', { name: 'Делюкс с видом на горы' })).toBeInTheDocument()
    expect(screen.getByText('Wi-Fi')).toBeInTheDocument()
    expect(screen.getByText('Завтрак')).toBeInTheDocument()
    expect(screen.getByAltText('Кровать у окна с видом на горы')).toBeInTheDocument()
    expect(screen.getByText('$120')).toBeInTheDocument()
    expect(screen.getByText('Мгновенное подтверждение')).toBeInTheDocument()
    await waitFor(() => expect(document.title).toBe('Делюкс с видом на горы — Отель Ала-Тоо'))
  })

  it('shows a not-found state with a link back to the catalog for an unknown slug', async () => {
    const getRoomType = vi
      .fn<ApiClient['catalog']['getRoomType']>()
      .mockRejectedValue(new ApiError({ code: 'NOT_FOUND', message: 'Объект не найден.', errors: null }))

    renderDetail(createApiClient(getRoomType), 'unknown-slug')

    expect(await screen.findByRole('heading', { name: 'Такого номера нет в каталоге' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'К каталогу номеров' })).toBeInTheDocument()
  })

  it('offers a retry on a generic failure', async () => {
    const getRoomType = vi
      .fn<ApiClient['catalog']['getRoomType']>()
      .mockRejectedValueOnce(new ApiError({ code: 'VALIDATION_ERROR', message: 'Ошибка.', errors: null }))
      .mockResolvedValue(deluxe)
    const user = (await import('@testing-library/user-event')).default.setup()

    renderDetail(createApiClient(getRoomType))

    await screen.findByRole('heading', { name: 'Не удалось открыть страницу' })
    await user.click(screen.getByRole('button', { name: 'Повторить попытку' }))

    expect(await screen.findByRole('heading', { name: 'Делюкс с видом на горы' })).toBeInTheDocument()
  })
})
