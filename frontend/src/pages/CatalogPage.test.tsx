import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import { CatalogPage } from './CatalogPage.tsx'
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

const standard: RoomType = {
  name: 'Стандарт',
  slug: 'standard',
  description: 'Уютный номер для короткой поездки.',
  price_per_night: '70.00',
  max_adults: 2,
  max_children: 0,
  area_sqm: '18.00',
  bed_count: 1,
  confirmation_mode: 'manual',
  amenities: [{ name: 'Wi-Fi', slug: 'wifi' }],
  images: [],
}

function createApiClient(overrides: Partial<ApiClient['catalog']> = {}): ApiClient {
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
    catalog: {
      listRoomTypes: vi.fn(async () => [deluxe, standard]),
      getRoomType: vi.fn(),
      ...overrides,
    },
  }
}

function renderCatalog(client: ApiClient) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ApiClientContext.Provider value={client}>
        <MemoryRouter initialEntries={['/rooms']}>
          <CatalogPage />
        </MemoryRouter>
      </ApiClientContext.Provider>
    </QueryClientProvider>,
  )
}

describe('CatalogPage', () => {
  it('renders room types from the API', async () => {
    renderCatalog(createApiClient())

    expect(await screen.findByRole('heading', { name: 'Делюкс с видом на горы' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Стандарт' })).toBeInTheDocument()
    expect(screen.getByText('$120')).toBeInTheDocument()
    expect(screen.getByText('Найдено категорий: 2')).toHaveAttribute('aria-live', 'polite')
    await waitFor(() => expect(document.title).toBe('Номера — Отель Ала-Тоо'))
  })

  it('does not show the result summary while the catalog is loading', async () => {
    renderCatalog(createApiClient({ listRoomTypes: vi.fn(() => new Promise<RoomType[]>(() => undefined)) }))

    expect(await screen.findByRole('heading', { name: 'Загружаем номера' })).toBeInTheDocument()
    expect(screen.queryByText(/Найдено категорий:/)).not.toBeInTheDocument()
  })

  it('sends the selected capacity filter to the API', async () => {
    const listRoomTypes = vi.fn<ApiClient['catalog']['listRoomTypes']>(async (filters) =>
      filters?.adults === 2 ? [deluxe] : [deluxe, standard],
    )
    const user = (await import('@testing-library/user-event')).default.setup()

    renderCatalog(createApiClient({ listRoomTypes }))
    await screen.findByRole('heading', { name: 'Делюкс с видом на горы' })
    expect(screen.getByText('Найдено категорий: 2')).toHaveAttribute('aria-live', 'polite')

    await user.selectOptions(screen.getByLabelText('Взрослые'), '2')

    await waitFor(() =>
      expect(listRoomTypes).toHaveBeenCalledWith(expect.objectContaining({ adults: 2 })),
    )
    expect(await screen.findByText('Найдено категорий: 1')).toHaveAttribute('aria-live', 'polite')
  })

  it('offers a retry when the catalog fails to load', async () => {
    const listRoomTypes = vi
      .fn<ApiClient['catalog']['listRoomTypes']>()
      .mockRejectedValueOnce(new ApiError({ code: 'VALIDATION_ERROR', message: 'Ошибка.', errors: null }))
      .mockResolvedValue([deluxe])
    const user = (await import('@testing-library/user-event')).default.setup()

    renderCatalog(createApiClient({ listRoomTypes }))

    await screen.findByRole('heading', { name: 'Не удалось открыть каталог' })
    expect(screen.queryByText(/Найдено категорий:/)).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Повторить попытку' }))

    expect(await screen.findByRole('heading', { name: 'Делюкс с видом на горы' })).toBeInTheDocument()
  })

  it('shows an empty state when the catalog has no room types', async () => {
    renderCatalog(createApiClient({ listRoomTypes: vi.fn(async () => []) }))

    expect(await screen.findByRole('heading', { name: 'Каталог пока пуст' })).toBeInTheDocument()
    expect(screen.queryByText(/Найдено категорий:/)).not.toBeInTheDocument()
  })
})
