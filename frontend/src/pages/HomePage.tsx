import Carousel from 'react-bootstrap/Carousel'
import Container from 'react-bootstrap/Container'
import { useEffect } from 'react'
import { Link } from 'react-router-dom'

import { StayDayRail } from '../features/content/StayDayRail.tsx'
import { useSiteContent } from '../features/content/siteQuery.ts'
import { ApiError } from '../shared/api/client.ts'
import type { HeroSlide, SiteContent } from '../shared/api/types.ts'
import { HotelFooter } from '../shared/ui/HotelFooter.tsx'

function HeroActions({ slide }: { slide: HeroSlide }) {
  const primaryAction =
    slide.primary_cta_label?.trim() && slide.primary_cta_url?.trim() ? (
      <a className="cms-primary-action" href={slide.primary_cta_url}>
        {slide.primary_cta_label}
      </a>
    ) : null
  const secondaryAction =
    slide.secondary_cta_label?.trim() && slide.secondary_cta_url?.trim() ? (
      <a className="cms-secondary-action" href={slide.secondary_cta_url}>
        {slide.secondary_cta_label}
      </a>
    ) : null

  return primaryAction !== null || secondaryAction !== null ? (
    <div className="cms-hero-actions">
      {primaryAction}
      {secondaryAction}
    </div>
  ) : null
}

function HeroSlideContent({
  isPrimaryHeading = true,
  slide,
}: {
  isPrimaryHeading?: boolean
  slide: HeroSlide
}) {
  const Heading = isPrimaryHeading ? 'h1' : 'h2'

  return (
    <article className="cms-hero-slide">
      {slide.image_url?.trim() ? (
        <img
          className="cms-hero-image"
          src={slide.image_url}
          alt=""
          loading={isPrimaryHeading ? 'eager' : 'lazy'}
        />
      ) : null}
      <div className="cms-hero-overlay">
        <Container className="cms-hero-copy">
          <p className="cms-section-label">{slide.eyebrow}</p>
          <Heading>{slide.title}</Heading>
          {slide.body !== undefined ? <p className="cms-hero-body">{slide.body}</p> : null}
          <HeroActions slide={slide} />
        </Container>
      </div>
    </article>
  )
}

function Hero({ content }: { content: SiteContent }) {
  const [firstSlide] = content.hero_slides

  return content.hero_slides.length > 1 ? (
    <Carousel
      className="cms-hero-carousel"
      interval={7000}
      pause="hover"
      prevLabel="Предыдущий слайд"
      nextLabel="Следующий слайд"
    >
      {content.hero_slides.map((slide, index) => (
        <Carousel.Item key={`${slide.title}-${slide.image_url ?? ''}`}>
          <HeroSlideContent isPrimaryHeading={index === 0} slide={slide} />
        </Carousel.Item>
      ))}
    </Carousel>
  ) : firstSlide !== undefined ? (
    <HeroSlideContent slide={firstSlide} />
  ) : (
    <section className="cms-hero-slide cms-hero-fallback">
      <Container className="cms-hero-copy">
        <p className="cms-section-label">Гостеприимство без суеты</p>
        <h1>{content.name}</h1>
        <p className="cms-hero-body">{content.tagline}</p>
      </Container>
    </section>
  )
}

function SiteContentView({ content }: { content: SiteContent }) {
  const aboutParagraphs = content.about_text.split(/\n{2,}/).filter((paragraph) => paragraph.trim() !== '')

  return (
    <>
      <Hero content={content} />
      <section className="cms-about" id="about" aria-labelledby="about-title">
        <Container>
          <div className="cms-about-head">
            <p className="cms-section-label cms-section-label-dark">О гостинице</p>
            <h2 id="about-title">{content.about_title}</h2>
          </div>
          <div className="cms-about-prose">
            {aboutParagraphs.map((paragraph) => (
              <p key={paragraph.slice(0, 48)}>{paragraph}</p>
            ))}
          </div>
          <StayDayRail checkInTime={content.check_in_time} checkOutTime={content.check_out_time} />
        </Container>
      </section>
      {content.features.length > 0 ? (
        <section className="cms-features" id="features" aria-labelledby="features-title">
          <Container>
            <div className="cms-section-heading">
              <p className="cms-section-label cms-section-label-dark">В гостинице</p>
              <h2 id="features-title">Всё важное — рядом</h2>
            </div>
            <div className="cms-feature-grid">
              {content.features.map((feature) => (
                <article className="cms-feature-card" key={`${feature.title}-${feature.icon}`}>
                  <span className="cms-feature-icon" aria-hidden="true">{feature.icon}</span>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </article>
              ))}
            </div>
          </Container>
        </section>
      ) : null}
    </>
  )
}

export function HomePage() {
  const contentQuery = useSiteContent()
  const content = contentQuery.data
  const isUnpublished = contentQuery.error instanceof ApiError && contentQuery.error.code === 'NOT_FOUND'

  useEffect(() => {
    if (content !== undefined) {
      document.title = content.seo_title
      document
        .querySelector('meta[name="description"]')
        ?.setAttribute('content', content.seo_description)
    }
  }, [content])

  return (
    <div className="hotel-app-shell">
      <a className="skip-link" href="#home-main">
        Перейти к содержанию
      </a>
      <header className="hotel-header">
        <Link className="hotel-wordmark" to="/" aria-label={`${content?.name ?? 'HotelApp'} — главная`}>
          {content?.name ?? 'HotelApp'}
        </Link>
        <nav className="hotel-nav" aria-label="Основная навигация">
          {content !== undefined ? (
            <>
              <a className="hotel-nav-anchor" href="#about">О гостинице</a>
              {content.features.length > 0 ? (
                <a className="hotel-nav-anchor" href="#features">Удобства</a>
              ) : null}
            </>
          ) : null}
          <Link to="/login">Войти</Link>
          <Link className="hotel-nav-cta" to="/register">Регистрация</Link>
        </nav>
      </header>
      <main className="home-main" id="home-main">
        {contentQuery.isPending ? (
          <section className="cms-status cms-status-loading" aria-busy="true">
            <Container>
              <h1 className="visually-hidden">Загружаем страницу гостиницы</h1>
              <p className="cms-section-label">Загружаем</p>
              <span className="cms-skeleton cms-skeleton-title" />
              <span className="cms-skeleton cms-skeleton-line" />
              <span className="cms-skeleton cms-skeleton-line cms-skeleton-line-short" />
              <p className="visually-hidden" aria-live="polite">Загружаем информацию о гостинице.</p>
            </Container>
          </section>
        ) : contentQuery.isError ? (
          <section className="cms-status" aria-live="polite">
            <Container>
              <p className="cms-section-label">
                {isUnpublished ? 'Информация пока недоступна' : 'Не удалось загрузить данные'}
              </p>
              <h1>{isUnpublished ? 'Контент ещё не опубликован' : 'Не удалось открыть страницу'}</h1>
              <p>
                {isUnpublished
                  ? 'Менеджер может добавить профиль гостиницы в административной панели.'
                  : 'Проверьте подключение и повторите попытку.'}
              </p>
              <button className="cms-primary-action" type="button" onClick={() => void contentQuery.refetch()}>
                Повторить попытку
              </button>
            </Container>
          </section>
        ) : content !== undefined ? <SiteContentView content={content} /> : null}
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
