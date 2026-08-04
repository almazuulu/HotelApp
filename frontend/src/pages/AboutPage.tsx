import { HotelStorySection } from '../features/content/HotelStorySection.tsx'
import { useSiteContent } from '../features/content/siteQuery.ts'
import { ApiError } from '../shared/api/client.ts'
import { truncate } from '../shared/format.ts'
import { PageBanner } from '../shared/ui/PageBanner.tsx'
import { SiteLayout } from '../shared/ui/SiteLayout.tsx'
import { StatusSection } from '../shared/ui/StatusSection.tsx'
import { useDocumentMeta } from '../shared/useDocumentMeta.ts'

export function AboutPage() {
  const contentQuery = useSiteContent()
  const content = contentQuery.data
  const isUnpublished = contentQuery.error instanceof ApiError && contentQuery.error.code === 'NOT_FOUND'

  useDocumentMeta(
    content !== undefined ? `${content.about_title} — ${content.name}` : undefined,
    content !== undefined ? truncate(content.about_text, 155) : undefined,
  )

  return (
    <SiteLayout mainClassName="site-main">
      {contentQuery.isPending ? (
        <StatusSection
          variant="loading"
          eyebrow="Загружаем"
          title="Загружаем страницу «О гостинице»"
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
          <PageBanner eyebrow="О гостинице" title={content.about_title} lead={content.tagline} />
          <HotelStorySection content={content} showHeading={false} />
        </>
      ) : null}
    </SiteLayout>
  )
}
