import type { PropsWithChildren, ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { HotelFooter } from '../../shared/ui/HotelFooter.tsx'

interface AuthFrameProps extends PropsWithChildren {
  eyebrow: string
  title: string
  actions?: ReactNode
}

export function AuthFrame({ actions, children, eyebrow, title }: AuthFrameProps) {
  return (
    <div className="hotel-app-shell">
      <header className="hotel-header">
        <Link className="hotel-wordmark" to="/" aria-label="HotelApp — главная">
          Hotel<span>App</span>
        </Link>
        <nav className="hotel-nav" aria-label="Основная навигация">
          <NavLink to="/login">Войти</NavLink>
          <NavLink to="/register">Регистрация</NavLink>
          {actions}
        </nav>
      </header>
      <main className="auth-main">
        <section className="auth-intro" aria-labelledby="auth-page-title">
          <p className="hotel-eyebrow">{eyebrow}</p>
          <h1 id="auth-page-title">{title}</h1>
          <p>
            Управляйте бронированиями в одном месте. Вход защищён сессионной cookie и
            подтверждением CSRF.
          </p>
        </section>
        <section className="auth-card" aria-label={title}>
          {children}
        </section>
      </main>
      <HotelFooter />
    </div>
  )
}
