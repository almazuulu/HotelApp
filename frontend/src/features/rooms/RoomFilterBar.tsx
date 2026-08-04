import type { Amenity } from '../../shared/api/types.ts'

export interface RoomFilterValue {
  adults?: number
  children?: number
  amenity: string[]
}

interface RoomFilterBarProps {
  value: RoomFilterValue
  amenityOptions: Amenity[]
  onChange: (next: RoomFilterValue) => void
}

const ADULT_OPTIONS = [1, 2, 3, 4, 5, 6]
const CHILDREN_OPTIONS = [0, 1, 2, 3, 4]

function parseSelect(raw: string): number | undefined {
  return raw === '' ? undefined : Number(raw)
}

/** Capacity selects plus amenity toggle chips; the page owns state and keeps it in the URL. */
export function RoomFilterBar({ amenityOptions, onChange, value }: RoomFilterBarProps) {
  const isFilterActive = value.adults !== undefined || value.children !== undefined || value.amenity.length > 0

  function toggleAmenity(slug: string) {
    const next = value.amenity.includes(slug)
      ? value.amenity.filter((item) => item !== slug)
      : [...value.amenity, slug]
    onChange({ ...value, amenity: next })
  }

  return (
    <div className="room-filters" role="group" aria-label="Фильтры каталога номеров">
      <div className="room-filters-row">
        <label className="room-filter-field">
          <span aria-hidden="true">Взрослые</span>
          <select
            aria-label="Взрослые"
            value={value.adults?.toString() ?? ''}
            onChange={(event) => onChange({ ...value, adults: parseSelect(event.target.value) })}
          >
            <option value="">Неважно</option>
            {ADULT_OPTIONS.map((count) => (
              <option key={count} value={count}>
                от {count}
              </option>
            ))}
          </select>
        </label>
        <label className="room-filter-field">
          <span aria-hidden="true">Дети</span>
          <select
            aria-label="Дети"
            value={value.children?.toString() ?? ''}
            onChange={(event) => onChange({ ...value, children: parseSelect(event.target.value) })}
          >
            <option value="">Неважно</option>
            {CHILDREN_OPTIONS.map((count) => (
              <option key={count} value={count}>
                от {count}
              </option>
            ))}
          </select>
        </label>
        {isFilterActive ? (
          <button
            type="button"
            className="room-filters-reset"
            onClick={() => onChange({ adults: undefined, children: undefined, amenity: [] })}
          >
            Сбросить фильтры
          </button>
        ) : null}
      </div>
      {amenityOptions.length > 0 ? (
        <ul className="room-filters-amenities">
          {amenityOptions.map((amenity) => {
            const isChecked = value.amenity.includes(amenity.slug)

            return (
              <li key={amenity.slug}>
                <label className={`amenity-toggle${isChecked ? ' amenity-toggle-active' : ''}`}>
                  <input type="checkbox" checked={isChecked} onChange={() => toggleAmenity(amenity.slug)} />
                  {amenity.name}
                </label>
              </li>
            )
          })}
        </ul>
      ) : null}
    </div>
  )
}
