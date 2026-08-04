import Container from 'react-bootstrap/Container'
import { Link, useParams } from 'react-router-dom'

import { ConfirmationBadge } from '../features/rooms/ConfirmationBadge.tsx'
import { AdultsIcon, AreaIcon, BedIcon, ChildrenIcon } from '../features/rooms/icons.tsx'
import { RoomTypeGallery } from '../features/rooms/RoomTypeGallery.tsx'
import { useRoomType } from '../features/rooms/roomsQuery.ts'
import { useSiteContent } from '../features/content/siteQuery.ts'
import { ApiError } from '../shared/api/client.ts'
import { formatUsd, truncate } from '../shared/format.ts'
import { PageBanner } from '../shared/ui/PageBanner.tsx'
import { SiteLayout } from '../shared/ui/SiteLayout.tsx'
import { StatusSection } from '../shared/ui/StatusSection.tsx'
import { useDocumentMeta } from '../shared/useDocumentMeta.ts'

export function RoomTypeDetailPage() {
  const { slug = '' } = useParams<{ slug: string }>()
  const roomTypeQuery = useRoomType(slug)
  const siteContent = useSiteContent()
  const roomType = roomTypeQuery.data
  const hotelName = siteContent.data?.name
  const isNotFound = roomTypeQuery.error instanceof ApiError && roomTypeQuery.error.code === 'NOT_FOUND'

  useDocumentMeta(
    roomType !== undefined && hotelName !== undefined ? `${roomType.name} — ${hotelName}` : undefined,
    roomType !== undefined ? truncate(roomType.description, 155) : undefined,
  )

  return (
    <SiteLayout mainClassName="site-main">
      {roomTypeQuery.isPending ? (
        <StatusSection
          variant="loading"
          eyebrow="Загружаем"
          title="Загружаем номер"
          description="Загружаем данные о категории номера."
        />
      ) : roomTypeQuery.isError ? (
        <StatusSection
          variant="error"
          eyebrow={isNotFound ? 'Категория не найдена' : 'Не удалось загрузить данные'}
          title={isNotFound ? 'Такого номера нет в каталоге' : 'Не удалось открыть страницу'}
          description={
            isNotFound
              ? 'Возможно, категория была переименована или снята с публикации.'
              : 'Проверьте подключение и повторите попытку.'
          }
          action={
            isNotFound ? (
              <Link className="cms-primary-action" to="/rooms">
                К каталогу номеров
              </Link>
            ) : (
              <button className="cms-primary-action" type="button" onClick={() => void roomTypeQuery.refetch()}>
                Повторить попытку
              </button>
            )
          }
        />
      ) : roomType !== undefined ? (
        <>
          <PageBanner eyebrow="Категория номера" title={roomType.name}>
            <Link className="page-banner-back" to="/rooms">
              ← Все номера
            </Link>
          </PageBanner>
          <section className="room-detail" aria-labelledby="room-detail-heading">
            <Container>
              <h2 className="visually-hidden" id="room-detail-heading">
                Информация о номере
              </h2>
              <div className="room-detail-grid">
                <RoomTypeGallery images={roomType.images} roomName={roomType.name} />
                <aside className="room-detail-panel" aria-label="Стоимость и параметры номера">
                  <p className="room-detail-price">
                    ${formatUsd(roomType.price_per_night)} <span>/ ночь</span>
                  </p>
                  <ConfirmationBadge mode={roomType.confirmation_mode} />
                  <dl className="room-facts room-facts-panel">
                    <div>
                      <dt>
                        <AdultsIcon /> Взрослые
                      </dt>
                      <dd>{roomType.max_adults}</dd>
                    </div>
                    <div>
                      <dt>
                        <ChildrenIcon /> Дети
                      </dt>
                      <dd>{roomType.max_children}</dd>
                    </div>
                    <div>
                      <dt>
                        <BedIcon /> Кровати
                      </dt>
                      <dd>{roomType.bed_count}</dd>
                    </div>
                    <div>
                      <dt>
                        <AreaIcon /> Площадь
                      </dt>
                      <dd>{roomType.area_sqm} м²</dd>
                    </div>
                  </dl>
                  {roomType.amenities.length > 0 ? (
                    <div className="room-detail-amenities">
                      <p className="room-detail-amenities-label">Удобства</p>
                      <ul>
                        {roomType.amenities.map((amenity) => (
                          <li key={amenity.slug} className="amenity-tag">
                            {amenity.name}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </aside>
              </div>
              <div className="room-detail-description">
                <p>{roomType.description}</p>
              </div>
            </Container>
          </section>
        </>
      ) : null}
    </SiteLayout>
  )
}
