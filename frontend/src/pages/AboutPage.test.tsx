import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import { AboutPage } from './AboutPage.tsx'
import { ApiError, type ApiClient } from '../shared/api/client.ts'
import { ApiClientContext } from '../shared/api/context.ts'
import type { SiteContent } from '../shared/api/types.ts'
import { stubApiClient } from '../test/stubApiClient.ts'

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
  features: [{ icon: '☕', title: 'Завтрак', description: 'Начинайте день без спешки.' }],
}

function renderAbout(client: ApiClient) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ApiClientContext.Provider value={client}>
        <MemoryRouter>
          <AboutPage />
        </MemoryRouter>
      </ApiClientContext.Provider>
    </QueryClientProvider>,
  )
}

describe('AboutPage', () => {
  it('renders the CMS story once as the page heading and applies SEO', async () => {
    renderAbout(stubApiClient({ site: { getContent: vi.fn(async () => siteContent) } }))

    expect(await screen.findByRole('heading', { name: 'Добро пожаловать в Отель Ала-Тоо' })).toBeInTheDocument()
    expect(screen.getAllByText('Добро пожаловать в Отель Ала-Тоо')).toHaveLength(1)
    expect(screen.getByText('Здесь начинается спокойное путешествие.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Завтрак' })).toBeInTheDocument()
    await waitFor(() => expect(document.title).toBe('Добро пожаловать в Отель Ала-Тоо — Отель Ала-Тоо'))
  })

  it('offers a retry when the CMS document is unavailable', async () => {
    const getContent = vi
      .fn<ApiClient['site']['getContent']>()
      .mockRejectedValueOnce(new ApiError({ code: 'NOT_FOUND', message: 'Объект не найден.', errors: null }))
      .mockResolvedValueOnce(siteContent)
    const user = (await import('@testing-library/user-event')).default.setup()

    renderAbout(stubApiClient({ site: { getContent } }))

    await screen.findByRole('heading', { name: 'Контент ещё не опубликован' })
    await user.click(screen.getByRole('button', { name: 'Повторить попытку' }))

    expect(await screen.findByRole('heading', { name: 'Добро пожаловать в Отель Ала-Тоо' })).toBeInTheDocument()
  })
})
