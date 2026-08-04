import { Link } from 'react-router-dom'

import { ConfirmationBadge } from './ConfirmationBadge.tsx'
import { AdultsIcon, AreaIcon, BedIcon, ChildrenIcon } from './icons.tsx'
import { formatUsd } from '../../shared/format.ts'
import type { RoomType } from '../../shared/api/types.ts'

export function RoomTypeCard({ roomType }: { roomType: RoomType }) {
  const [cover] = roomType.images
  const detailPath = `/rooms/${roomType.slug}`

  return (
    <article className="room-card">
      <Link className="room-card-media" to={detailPath}>
        {cover !== undefined ? (
          <img src={cover.image_url} alt={cover.alt_text} loading="lazy" />
        ) : (
          <span className="room-card-media-fallback" aria-hidden="true">
            {roomType.name.charAt(0)}
          </span>
        )}
        <span className="room-card-price">
          ${formatUsd(roomType.price_per_night)} <small>/ ночь</small>
        </span>
      </Link>
      <div className="room-card-body">
        <div className="room-card-heading">
          <h3>
            <Link to={detailPath}>{roomType.name}</Link>
          </h3>
          <ConfirmationBadge mode={roomType.confirmation_mode} />
        </div>
        <dl className="room-facts" aria-label="Вместимость и параметры номера">
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
        <p className="room-card-description">{roomType.description}</p>
        <Link className="room-card-link" to={detailPath}>
          Подробнее о номере →
        </Link>
      </div>
    </article>
  )
}
