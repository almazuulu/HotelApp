import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { RoomTypeGallery } from './RoomTypeGallery.tsx'
import type { RoomTypeImage } from '../../shared/api/types.ts'

const images: RoomTypeImage[] = [
  { image_url: 'https://example.com/room-1.jpg', alt_text: 'Номер с большой кроватью' },
  { image_url: 'https://example.com/room-2.jpg', alt_text: 'Рабочая зона номера' },
  { image_url: 'https://example.com/room-3.jpg', alt_text: 'Ванная комната номера' },
]

function renderGallery(galleryImages = images) {
  return render(<RoomTypeGallery images={galleryImages} roomName="Делюкс" />)
}

function thumbnail(index: number) {
  return screen.getByRole('button', { name: `Показать фото ${index} из ${images.length}` })
}

function expectActiveThumbnail(index: number) {
  const activeThumbnail = thumbnail(index)

  expect(activeThumbnail).toHaveClass('active')
  expect(activeThumbnail).toHaveAttribute('aria-current', 'true')
}

describe('RoomTypeGallery', () => {
  it('cycles through thumbnails with ArrowLeft and ArrowRight, moving focus to the active thumbnail', async () => {
    const user = userEvent.setup()
    renderGallery()

    thumbnail(1).focus()
    await user.keyboard('{ArrowLeft}')

    expectActiveThumbnail(3)
    expect(thumbnail(3)).toHaveFocus()

    await user.keyboard('{ArrowRight}')

    expectActiveThumbnail(1)
    expect(thumbnail(1)).toHaveFocus()
  })

  it('selects the first and last thumbnail with Home and End', async () => {
    const user = userEvent.setup()
    renderGallery()

    thumbnail(2).focus()
    await user.keyboard('{Home}')

    expectActiveThumbnail(1)
    expect(thumbnail(1)).toHaveFocus()

    thumbnail(2).focus()
    await user.keyboard('{End}')

    expectActiveThumbnail(3)
    expect(thumbnail(3)).toHaveFocus()
  })

  it('keeps click selection and Carousel controls synchronized with the active thumbnail', async () => {
    const user = userEvent.setup()
    renderGallery()

    await user.click(thumbnail(2))
    expectActiveThumbnail(2)

    await user.click(screen.getByRole('button', { name: 'Следующее фото' }))
    expectActiveThumbnail(3)
  })

  it('does not render thumbnail keyboard navigation for a single image', () => {
    renderGallery(images.slice(0, 1))

    expect(screen.queryByRole('list', { name: 'Выбор фотографии' })).not.toBeInTheDocument()
  })
})
