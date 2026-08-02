import { useEffect, useState } from 'react'

const HOTEL_TIME_ZONE = 'Asia/Bishkek'
const MINUTES_PER_DAY = 24 * 60
const HOUR_TICKS = [0, 6, 12, 18, 24]
const DEFAULT_CHECK_IN_MINUTES = 14 * 60
const DEFAULT_CHECK_OUT_MINUTES = 12 * 60

interface StayDayRailProps {
  checkInTime?: string
  checkOutTime?: string
}

function toMinutes(value: string | undefined, fallback: number): number {
  const [rawHours, rawMinutes] = (value ?? '').split(':')
  const hours = Number(rawHours)
  const minutes = Number(rawMinutes)

  if (!Number.isInteger(hours) || !Number.isInteger(minutes)) {
    return fallback
  }

  return Math.min(Math.max(hours * 60 + minutes, 0), MINUTES_PER_DAY)
}

function formatClock(minutes: number): string {
  const hours = Math.floor(minutes / 60) % 24
  const rest = minutes % 60

  return `${String(hours).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
}

/** Reads the wall-clock minute of the day at the hotel, independent of the visitor's own timezone. */
function readHotelMinutes(): number {
  const parts = new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    hour12: false,
    minute: '2-digit',
    timeZone: HOTEL_TIME_ZONE,
  }).formatToParts(new Date())
  const hours = Number(parts.find((part) => part.type === 'hour')?.value ?? '0') % 24
  const minutes = Number(parts.find((part) => part.type === 'minute')?.value ?? '0')

  return hours * 60 + minutes
}

function percent(minutes: number): string {
  return `${((minutes / MINUTES_PER_DAY) * 100).toFixed(4)}%`
}

/**
 * Draws one hotel day: the hours a room belongs to a guest, the turnaround gap between
 * check-out and check-in, and the hotel's own current time. Presentation only — every
 * value comes from published CMS content, and no booking deadline is derived here.
 */
export function StayDayRail({ checkInTime, checkOutTime }: StayDayRailProps) {
  const checkIn = toMinutes(checkInTime, DEFAULT_CHECK_IN_MINUTES)
  const checkOut = toMinutes(checkOutTime, DEFAULT_CHECK_OUT_MINUTES)
  const [hotelMinutes, setHotelMinutes] = useState(readHotelMinutes)

  useEffect(() => {
    const timer = window.setInterval(() => setHotelMinutes(readHotelMinutes()), 30_000)

    return () => window.clearInterval(timer)
  }, [])

  const turnaroundStart = Math.min(checkIn, checkOut)
  const turnaroundEnd = Math.max(checkIn, checkOut)

  return (
    <section className="stay-rail" aria-labelledby="stay-rail-title">
      <p className="cms-section-label cms-section-label-dark">Сутки в отеле</p>
      <h3 className="stay-rail-title" id="stay-rail-title">
        Между выездом и заездом номер готовят к следующему гостю
      </h3>

      <div className="stay-rail-track" aria-hidden="true">
        <span
          className="stay-rail-band stay-rail-band-stay"
          style={{ insetInlineStart: 0, inlineSize: percent(turnaroundStart) }}
        />
        <span
          className="stay-rail-band stay-rail-band-turnaround"
          style={{
            inlineSize: percent(turnaroundEnd - turnaroundStart),
            insetInlineStart: percent(turnaroundStart),
          }}
        />
        <span
          className="stay-rail-band stay-rail-band-stay"
          style={{
            inlineSize: percent(MINUTES_PER_DAY - turnaroundEnd),
            insetInlineStart: percent(turnaroundEnd),
          }}
        />
        <span className="stay-rail-edge stay-rail-edge-out" style={{ insetInlineStart: percent(checkOut) }}>
          <b>Выезд</b> {formatClock(checkOut)}
        </span>
        <span className="stay-rail-edge stay-rail-edge-in" style={{ insetInlineStart: percent(checkIn) }}>
          <b>Заезд</b> {formatClock(checkIn)}
        </span>
        <span className="stay-rail-now" style={{ insetInlineStart: percent(hotelMinutes) }} />
        <span className="stay-rail-hours">
          {HOUR_TICKS.map((hour) => (
            <span className="stay-rail-hour" key={hour} style={{ insetInlineStart: percent(hour * 60) }}>
              {String(hour).padStart(2, '0')}
            </span>
          ))}
        </span>
      </div>

      <dl className="stay-rail-legend">
        <div>
          <dt>Заезд</dt>
          <dd>с {formatClock(checkIn)}</dd>
        </div>
        <div>
          <dt>Выезд</dt>
          <dd>до {formatClock(checkOut)}</dd>
        </div>
        <div className="stay-rail-legend-now">
          <dt>Сейчас в Бишкеке</dt>
          <dd>{formatClock(hotelMinutes)}</dd>
        </div>
      </dl>
    </section>
  )
}
