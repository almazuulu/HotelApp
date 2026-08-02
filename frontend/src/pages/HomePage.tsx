import { Container, Navbar } from 'react-bootstrap'

export function HomePage() {
  return (
    <>
      <Navbar bg="dark" data-bs-theme="dark">
        <Container>
          <Navbar.Brand href="/">HotelApp</Navbar.Brand>
        </Container>
      </Navbar>
      <main>
        <Container className="py-5">
          <h1>HotelApp</h1>
          <p>Каркас приложения готов. Страницы бронирования появятся в следующих задачах.</p>
        </Container>
      </main>
    </>
  )
}
