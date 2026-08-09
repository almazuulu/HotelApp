import Container from 'react-bootstrap/Container'
import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'

import { RoomFilterBar, type RoomFilterValue } from '../features/rooms/RoomFilterBar.tsx'
import { RoomTypeCard } from '../features/rooms/RoomTypeCard.tsx'
import { collectAmenities, useRoomTypes } from '../features/rooms/roomsQuery.ts'
import { useSiteContent } from '../features/content/siteQuery.ts'
import { truncate } from '../shared/format.ts'
import { PageBanner } from '../shared/ui/PageBanner.tsx'
import { SiteLayout } from '../shared/ui/SiteLayout.tsx'
import { StatusSection } from '../shared/ui/StatusSection.tsx'
import { useDocumentMeta } from '../shared/useDocumentMeta.ts'

function parsePositiveInt(raw: string | null): number | undefined {
  if (raw === null) {
    return undefined
  }
  const value = Number.parseInt(raw, 10)
  return Number.isFinite(value) && value >= 1 ? value : undefined
}

function parseNonNegativeInt(raw: string | null): number | undefined {
  if (raw === null) {
    return undefined
  }
  const value = Number.parseInt(raw, 10)
  return Number.isFinite(value) && value >= 0 ? value : undefined
}

export function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const siteContent = useSiteContent()
  const hotelName = siteContent.data?.name

  const adults = parsePositiveInt(searchParams.get('adults'))
  const children = parseNonNegativeInt(searchParams.get('children'))
  const amenity = searchParams.getAll('amenity')
  const isFilterActive = adults !== undefined || children !== undefined || amenity.length > 0

  useDocumentMeta(
    hotelName !== undefined ? `Номера — ${hotelName}` : undefined,
    hotelName !== undefined
      ? truncate(`Каталог номеров отеля ${hotelName}. ${siteContent.data?.tagline ?? ''}`, 155)
      : undefined,
  )

  const facetsQuery = useRoomTypes({ adults, children })
  const listQuery = useRoomTypes({ adults, children, amenity })
  const amenityOptions = useMemo(() => collectAmenities(facetsQuery.data ?? []), [facetsQuery.data])
  const rooms = listQuery.data ?? []

  function applyFilters(next: RoomFilterValue) {
    const params = new URLSearchParams()
    if (next.adults !== undefined) {
      params.set('adults', String(next.adults))
    }
    if (next.children !== undefined) {
      params.set('children', String(next.children))
    }
    for (const slug of next.amenity) {
      params.append('amenity', slug)
    }
    setSearchParams(params, { replace: true })
  }

  return (
    <SiteLayout mainClassName="site-main">
      <PageBanner
        eyebrow="Каталог"
        title="Номера"
        lead="Каждая категория показывает вместимость, площадь, удобства и актуальную цену за ночь — без скрытых условий."
      />
      <section className="room-catalog" aria-labelledby="room-catalog-heading">
        <Container>
          <h2 className="visually-hidden" id="room-catalog-heading">
            Список номеров
          </h2>
          <RoomFilterBar
            value={{ adults, children, amenity }}
            amenityOptions={amenityOptions}
            onChange={applyFilters}
          />
          {listQuery.isPending ? (
            <StatusSection
              variant="loading"
              eyebrow="Загружаем"
              title="Загружаем номера"
              description="Загружаем каталог номеров."
            />
          ) : listQuery.isError ? (
            <StatusSection
              variant="error"
              eyebrow="Не удалось загрузить данные"
              title="Не удалось открыть каталог"
              description="Проверьте подключение и повторите попытку."
              action={
                <button className="cms-primary-action" type="button" onClick={() => void listQuery.refetch()}>
                  Повторить попытку
                </button>
              }
            />
          ) : rooms.length === 0 ? (
            <div className="room-catalog-empty">
              <p className="cms-section-label cms-section-label-dark">Результаты</p>
              <h3>{isFilterActive ? 'Ничего не найдено' : 'Каталог пока пуст'}</h3>
              <p>
                {isFilterActive
                  ? 'Попробуйте изменить число гостей или снять часть удобств из фильтра.'
                  : 'Менеджер ещё не опубликовал ни одной категории номеров.'}
              </p>
              {isFilterActive ? (
                <button
                  className="cms-primary-action"
                  type="button"
                  onClick={() => applyFilters({ adults: undefined, children: undefined, amenity: [] })}
                >
                  Сбросить фильтры
                </button>
              ) : null}
            </div>
          ) : (
            <>
              <p className="room-catalog-summary" aria-live="polite">
                Найдено категорий: {rooms.length}
              </p>
              <div className="room-grid">
                {rooms.map((roomType) => (
                  <RoomTypeCard key={roomType.slug} roomType={roomType} />
                ))}
              </div>
            </>
          )}
        </Container>
      </section>
    </SiteLayout>
  )
}
