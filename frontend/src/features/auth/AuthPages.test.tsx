import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi } from 'vitest'

import type { ApiClient } from '../../shared/api/client.ts'
import { ApiClientContext } from '../../shared/api/context.ts'
import type { AccountUser, SiteContent } from '../../shared/api/types.ts'
import { AccountPage } from '../../pages/AccountPage.tsx'
import { LoginPage } from '../../pages/LoginPage.tsx'
import { RegisterPage } from '../../pages/RegisterPage.tsx'

const user: AccountUser = {
  id: 1,
  username: 'mariya',
  email: 'mariya@example.com',
  first_name: 'Мария',
  last_name: 'Иванова',
  phone: '+996700123456',
}

const siteContent: SiteContent = {
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

function createApiClient(overrides: Partial<ApiClient['auth']> = {}): ApiClient {
  return {
    basePath: '/api/v1',
    auth: {
      register: vi.fn(async () => user),
      login: vi.fn(async () => user),
      logout: vi.fn(async () => undefined),
      me: vi.fn(async () => user),
      updateProfile: vi.fn(async () => user),
      ...overrides,
    },
    site: {
      getContent: vi.fn(async () => siteContent),
    },
    catalog: {
      listRoomTypes: vi.fn(),
      getRoomType: vi.fn(),
    },
  }
}

function renderPage(initialPath: string, client: ApiClient) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ApiClientContext.Provider value={client}>
        <MemoryRouter initialEntries={[initialPath]}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/account" element={<AccountPage />} />
          </Routes>
        </MemoryRouter>
      </ApiClientContext.Provider>
    </QueryClientProvider>,
  )
}

describe('authentication pages', () => {
  it('submits login data through the API adapter and opens the account', async () => {
    const login = vi.fn(async () => user)
    const client = createApiClient({ login })
    const browser = userEvent.setup()

    renderPage('/login', client)
    await browser.type(screen.getByLabelText('Имя пользователя'), 'mariya')
    await browser.type(screen.getByLabelText('Пароль'), 'correct-horse-battery-staple')
    await browser.click(screen.getByRole('button', { name: 'Войти в аккаунт' }))

    expect(login).toHaveBeenCalledWith({
      username: 'mariya',
      password: 'correct-horse-battery-staple',
    })
    expect(await screen.findByRole('heading', { name: 'Здравствуйте, Мария' })).toBeInTheDocument()
  })

  it('submits all required registration data through the API adapter', async () => {
    const register = vi.fn(async () => user)
    const client = createApiClient({ register })
    const browser = userEvent.setup()

    renderPage('/register', client)
    await browser.type(screen.getByLabelText('Имя'), 'Мария')
    await browser.type(screen.getByLabelText('Фамилия'), 'Иванова')
    await browser.type(screen.getByLabelText('Имя пользователя'), 'mariya')
    await browser.type(screen.getByLabelText('Email'), 'mariya@example.com')
    await browser.type(screen.getByLabelText('Телефон'), '+996700123456')
    await browser.type(screen.getByLabelText('Пароль'), 'correct-horse-battery-staple')
    await browser.click(screen.getByRole('button', { name: 'Создать аккаунт' }))

    expect(register).toHaveBeenCalledWith({
      username: 'mariya',
      email: 'mariya@example.com',
      first_name: 'Мария',
      last_name: 'Иванова',
      phone: '+996700123456',
      password: 'correct-horse-battery-staple',
    })
    expect(await screen.findByRole('heading', { name: 'Здравствуйте, Мария' })).toBeInTheDocument()
  })

  it('ends the session from the profile page through the API adapter', async () => {
    const logout = vi.fn(async () => undefined)
    const client = createApiClient({ logout })
    const browser = userEvent.setup()

    renderPage('/account', client)
    await browser.click(await screen.findByRole('button', { name: 'Выйти' }))

    expect(logout).toHaveBeenCalledOnce()
    expect(await screen.findByRole('heading', { name: 'С возвращением' })).toBeInTheDocument()
  })
})
