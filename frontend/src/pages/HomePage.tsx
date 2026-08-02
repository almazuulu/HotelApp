import Container from 'react-bootstrap/Container'
import { Link } from 'react-router-dom'

import { HotelFooter } from '../shared/ui/HotelFooter.tsx'

export function HomePage() {
  return (
    <div className="hotel-app-shell">
      <header className="hotel-header">
        <Link className="hotel-wordmark" to="/">
          Hotel<span>App</span>
        </Link>
        <nav className="hotel-nav" aria-label="Основная навигация">
          <Link to="/login">Войти</Link>
          <Link to="/register">Регистрация</Link>
        </nav>
      </header>
      <main className="home-main">
        <Container>
          <p className="hotel-eyebrow">Одна гостиница · один спокойный сервис</p>
          <h1>HotelApp</h1>
          <p>Каркас приложения готов. Страницы бронирования появятся в следующих задачах.</p>
        </Container>
      </main>
      <HotelFooter />
    </div>
  )
}
