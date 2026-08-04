import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import { ContactsPage } from './ContactsPage.tsx'
import { ApiError, type ApiClient } from '../shared/api/client.ts'
import { ApiClientContext } from '../shared/api/context.ts'
import type { SiteContent } from '../shared/api/types.ts'

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

function createApiClient(getContent: ApiClient['site']['getContent']): ApiClient {
  return {
    basePath: '/api/v1',
    auth: {
      register: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
      me: vi.fn(),
      updateProfile: vi.fn(),
    },
    site: { getContent },
    catalog: { listRoomTypes: vi.fn(), getRoomType: vi.fn() },
  }
}

function renderContacts(client: ApiClient) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ApiClientContext.Provider value={client}>
        <MemoryRouter>
          <ContactsPage />
        </MemoryRouter>
      </ApiClientContext.Provider>
    </QueryClientProvider>,
  )
}

describe('ContactsPage', () => {
  it('renders address, phone, email and reception hours from the CMS document', async () => {
    renderContacts(createApiClient(vi.fn(async () => siteContent)))

    const main = screen.getByRole('main')

    expect(await within(main).findByText('ул. Токтогула, 101, Бишкек')).toBeInTheDocument()
    expect(within(main).getByRole('link', { name: '+996 312 123 456' })).toHaveAttribute(
      'href',
      'tel:+996312123456',
    )
    expect(within(main).getByRole('link', { name: 'stay@example.com' })).toHaveAttribute(
      'href',
      'mailto:stay@example.com',
    )
    expect(within(main).getByText('Заезд с 14:00')).toBeInTheDocument()
    expect(within(main).getByText('Выезд до 12:00')).toBeInTheDocument()
    await waitFor(() => expect(document.title).toBe('Контакты — Отель Ала-Тоо'))
  })

  it('offers a retry when the CMS document is unavailable', async () => {
    const getContent = vi
      .fn<ApiClient['site']['getContent']>()
      .mockRejectedValueOnce(new ApiError({ code: 'NOT_FOUND', message: 'Объект не найден.', errors: null }))
      .mockResolvedValueOnce(siteContent)
    const user = (await import('@testing-library/user-event')).default.setup()

    renderContacts(createApiClient(getContent))

    await screen.findByRole('heading', { name: 'Контент ещё не опубликован' })
    await user.click(screen.getByRole('button', { name: 'Повторить попытку' }))

    const main = screen.getByRole('main')
    expect(await within(main).findByText('ул. Токтогула, 101, Бишкек')).toBeInTheDocument()
  })
})
