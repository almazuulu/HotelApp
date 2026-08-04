import Container from 'react-bootstrap/Container'

import { useSiteContent } from '../features/content/siteQuery.ts'
import { ApiError } from '../shared/api/client.ts'
import { truncate } from '../shared/format.ts'
import { PageBanner } from '../shared/ui/PageBanner.tsx'
import { SiteLayout } from '../shared/ui/SiteLayout.tsx'
import { StatusSection } from '../shared/ui/StatusSection.tsx'
import { useDocumentMeta } from '../shared/useDocumentMeta.ts'

/** Mirrors the domain default in `bookings/policy.py`: 14:00 check-in, 12:00 check-out. */
function formatHour(value: string | undefined, fallback: string): string {
  const [hours = '00', minutes = '00'] = (value ?? fallback).split(':')
  return `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`
}

export function ContactsPage() {
  const contentQuery = useSiteContent()
  const content = contentQuery.data
  const isUnpublished = contentQuery.error instanceof ApiError && contentQuery.error.code === 'NOT_FOUND'

  useDocumentMeta(
    content !== undefined ? `Контакты — ${content.name}` : undefined,
    content !== undefined
      ? truncate(`${content.address}. Телефон: ${content.phone}. Email: ${content.email}.`, 155)
      : undefined,
  )

  return (
    <SiteLayout mainClassName="site-main">
      {contentQuery.isPending ? (
        <StatusSection
          variant="loading"
          eyebrow="Загружаем"
          title="Загружаем контакты"
          description="Загружаем контактные данные гостиницы."
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
          <PageBanner
            eyebrow="Контакты"
            title="Свяжитесь с нами"
            lead={`Мы на связи каждый день. Заезд с ${formatHour(content.check_in_time, '14:00')}, выезд до ${formatHour(content.check_out_time, '12:00')}.`}
          />
          <section className="contacts-section" aria-labelledby="contacts-heading">
            <Container>
              <h2 className="visually-hidden" id="contacts-heading">
                Контактные данные
              </h2>
              <div className="contacts-grid">
                <div className="contacts-card">
                  <p className="cms-section-label cms-section-label-dark">Адрес</p>
                  <address>{content.address}</address>
                </div>
                <div className="contacts-card">
                  <p className="cms-section-label cms-section-label-dark">Телефон</p>
                  <a href={`tel:${content.phone.replaceAll(' ', '')}`}>{content.phone}</a>
                </div>
                <div className="contacts-card">
                  <p className="cms-section-label cms-section-label-dark">Email</p>
                  <a href={`mailto:${content.email}`}>{content.email}</a>
                </div>
                <div className="contacts-card">
                  <p className="cms-section-label cms-section-label-dark">Стойка регистрации</p>
                  <p>Заезд с {formatHour(content.check_in_time, '14:00')}</p>
                  <p>Выезд до {formatHour(content.check_out_time, '12:00')}</p>
                </div>
              </div>
            </Container>
          </section>
        </>
      ) : null}
    </SiteLayout>
  )
}
