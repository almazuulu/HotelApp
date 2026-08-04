import Carousel from 'react-bootstrap/Carousel'
import Container from 'react-bootstrap/Container'

import { HotelStorySection } from '../features/content/HotelStorySection.tsx'
import { useSiteContent } from '../features/content/siteQuery.ts'
import { ApiError } from '../shared/api/client.ts'
import type { HeroSlide, SiteContent } from '../shared/api/types.ts'
import { SiteLayout } from '../shared/ui/SiteLayout.tsx'
import { StatusSection } from '../shared/ui/StatusSection.tsx'
import { useDocumentMeta } from '../shared/useDocumentMeta.ts'

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

export function HomePage() {
  const contentQuery = useSiteContent()
  const content = contentQuery.data
  const isUnpublished = contentQuery.error instanceof ApiError && contentQuery.error.code === 'NOT_FOUND'

  useDocumentMeta(content?.seo_title, content?.seo_description)

  return (
    <SiteLayout mainClassName="site-main">
      {contentQuery.isPending ? (
        <StatusSection
          variant="loading"
          eyebrow="Загружаем"
          title="Загружаем страницу гостиницы"
          description="Загружаем информацию о гостинице."
        />
      ) : contentQuery.isError ? (
        <StatusSection
          variant="error"
          eyebrow={isUnpublished ? 'Информация пока недоступна' : 'Не удалось загрузить данные'}
          title={isUnpublished ? 'Контент ещё не опубликован' : 'Не удалось открыть страницу'}
          description={
            isUnpublished
              ? 'Менеджер может добавить профиль гостиницы в административной панели.'
              : 'Проверьте подключение и повторите попытку.'
          }
          action={
            <button className="cms-primary-action" type="button" onClick={() => void contentQuery.refetch()}>
              Повторить попытку
            </button>
          }
        />
      ) : content !== undefined ? (
        <>
          <Hero content={content} />
          <HotelStorySection content={content} />
        </>
      ) : null}
    </SiteLayout>
  )
}
