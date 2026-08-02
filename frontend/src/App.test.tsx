import { render, screen } from '@testing-library/react'

import { App } from './App.tsx'

describe('App', () => {
  it('renders the home route', () => {
    window.history.pushState({}, '', '/')

    render(<App />)

    expect(screen.getByRole('link', { name: 'HotelApp — главная' })).toBeInTheDocument()
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})
