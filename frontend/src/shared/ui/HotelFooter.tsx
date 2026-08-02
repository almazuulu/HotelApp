interface HotelFooterProps {
  hotelName?: string
  footerText?: string
  address?: string
  phone?: string
  email?: string
}

export function HotelFooter({
  address,
  email,
  footerText = 'одна гостиница, спокойное бронирование.',
  hotelName = 'HotelApp',
  phone,
}: HotelFooterProps) {
  const hasContacts = address !== undefined || phone !== undefined || email !== undefined

  return (
    <footer className="hotel-footer">
      <div className="hotel-footer-top">
        <div className="hotel-footer-brand">
          <p className="hotel-footer-name">{hotelName}</p>
          <p className="hotel-footer-tagline">{footerText}</p>
        </div>
        {hasContacts ? (
          <address className="hotel-footer-contacts" aria-label="Контакты гостиницы">
            {address !== undefined ? <span>{address}</span> : null}
            {phone !== undefined ? <a href={`tel:${phone.replaceAll(' ', '')}`}>{phone}</a> : null}
            {email !== undefined ? <a href={`mailto:${email}`}>{email}</a> : null}
          </address>
        ) : null}
      </div>
      <div className="hotel-footer-base">
        <p>© {new Date().getFullYear()} {hotelName}</p>
        <p>
          Designed by <a href="https://htmlcodex.com">HTML Codex</a>
        </p>
      </div>
    </footer>
  )
}
