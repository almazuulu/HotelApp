import { type PropsWithChildren } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { useSiteContent } from '../../features/content/siteQuery.ts'
import { HotelFooter } from './HotelFooter.tsx'

const NAV_LINK_CLASS_NAME = ({ isActive }: { isActive: boolean }) => `hotel-nav-anchor${isActive ? ' active' : ''}`

interface SiteLayoutProps extends PropsWithChildren {
  mainClassName?: string
}

/** Shared public-site chrome: skip link, header/nav, and footer. Owns nothing about a page's own content state. */
export function SiteLayout({ children, mainClassName }: SiteLayoutProps) {
  const contentQuery = useSiteContent()
  const content = contentQuery.data

  return (
    <div className="hotel-app-shell">
      <a className="skip-link" href="#main-content">
        Перейти к содержанию
      </a>
      <header className="hotel-header">
        <Link className="hotel-wordmark" to="/" aria-label={`${content?.name ?? 'HotelApp'} — главная`}>
          {content?.name ?? 'HotelApp'}
        </Link>
        <nav className="hotel-nav" aria-label="Основная навигация">
          <NavLink to="/" end className={NAV_LINK_CLASS_NAME}>
            Главная
          </NavLink>
          <NavLink to="/rooms" className={NAV_LINK_CLASS_NAME}>
            Номера
          </NavLink>
          <NavLink to="/about" className={NAV_LINK_CLASS_NAME}>
            О гостинице
          </NavLink>
          <NavLink to="/contacts" className={NAV_LINK_CLASS_NAME}>
            Контакты
          </NavLink>
          <Link to="/login">Войти</Link>
          <Link className="hotel-nav-cta" to="/register">
            Регистрация
          </Link>
        </nav>
      </header>
      <main id="main-content" className={mainClassName}>
        {children}
      </main>
      <HotelFooter
        hotelName={content?.name}
        footerText={content?.footer_text}
        address={content?.address}
        phone={content?.phone}
        email={content?.email}
      />
    </div>
  )
}
