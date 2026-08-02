import { render, screen } from '@testing-library/react'
import { afterEach, beforeEach, vi } from 'vitest'

import { StayDayRail } from './StayDayRail.tsx'

describe('StayDayRail', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // 03:20 UTC is 09:20 in Asia/Bishkek (UTC+6), whatever timezone the visitor is in.
    vi.setSystemTime(new Date('2026-08-02T03:20:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows the published stay hours and the hotel time', () => {
    render(<StayDayRail checkInTime="14:00:00" checkOutTime="12:00:00" />)

    expect(screen.getByText('с 14:00')).toBeInTheDocument()
    expect(screen.getByText('до 12:00')).toBeInTheDocument()
    expect(screen.getByText('Сейчас в Бишкеке')).toBeInTheDocument()
    expect(screen.getByText('09:20')).toBeInTheDocument()
  })

  it('falls back to the standard hours when the times are missing or malformed', () => {
    render(<StayDayRail checkInTime={undefined} checkOutTime="полдень" />)

    expect(screen.getByText('с 14:00')).toBeInTheDocument()
    expect(screen.getByText('до 12:00')).toBeInTheDocument()
  })
})
