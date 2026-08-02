import { Container } from 'react-bootstrap'
import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <main>
      <Container className="py-5">
        <h1>Страница не найдена</h1>
        <Link to="/">Вернуться на главную</Link>
      </Container>
    </main>
  )
}
