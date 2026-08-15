import Carousel from 'react-bootstrap/Carousel'
import { useRef, useState, type KeyboardEvent } from 'react'

import type { RoomTypeImage } from '../../shared/api/types.ts'

interface RoomTypeGalleryProps {
  images: RoomTypeImage[]
  roomName: string
}

export function RoomTypeGallery({ images, roomName }: RoomTypeGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const thumbnailRefs = useRef<Array<HTMLButtonElement | null>>([])

  function handleThumbnailKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    if (images.length < 2) {
      return
    }

    let nextIndex: number | null = null

    switch (event.key) {
      case 'ArrowLeft':
        nextIndex = (index - 1 + images.length) % images.length
        break
      case 'ArrowRight':
        nextIndex = (index + 1) % images.length
        break
      case 'Home':
        nextIndex = 0
        break
      case 'End':
        nextIndex = images.length - 1
        break
      default:
        return
    }

    event.preventDefault()
    setActiveIndex(nextIndex)
    thumbnailRefs.current[nextIndex]?.focus()
  }

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
                onKeyDown={(event) => handleThumbnailKeyDown(event, index)}
                ref={(element) => {
                  thumbnailRefs.current[index] = element
                }}
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
