import Carousel from 'react-bootstrap/Carousel'
import { useState } from 'react'

import type { RoomTypeImage } from '../../shared/api/types.ts'

interface RoomTypeGalleryProps {
  images: RoomTypeImage[]
  roomName: string
}

export function RoomTypeGallery({ images, roomName }: RoomTypeGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0)

  if (images.length === 0) {
    return (
      <div className="room-gallery room-gallery-empty" role="img" aria-label={`Фотографии номера «${roomName}» пока не добавлены`}>
        {roomName.charAt(0)}
      </div>
    )
  }

  return (
    <div className="room-gallery">
      <Carousel
        activeIndex={activeIndex}
        onSelect={setActiveIndex}
        interval={null}
        indicators={false}
        prevLabel="Предыдущее фото"
        nextLabel="Следующее фото"
      >
        {images.map((image) => (
          <Carousel.Item key={image.image_url}>
            <img className="d-block w-100" src={image.image_url} alt={image.alt_text} />
          </Carousel.Item>
        ))}
      </Carousel>
      {images.length > 1 ? (
        <ul className="room-gallery-thumbs" aria-label="Выбор фотографии">
          {images.map((image, index) => (
            <li key={image.image_url}>
              <button
                type="button"
                className={index === activeIndex ? 'active' : undefined}
                aria-current={index === activeIndex ? 'true' : undefined}
                aria-label={`Показать фото ${index + 1} из ${images.length}`}
                onClick={() => setActiveIndex(index)}
              >
                <img src={image.image_url} alt="" loading="lazy" />
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
