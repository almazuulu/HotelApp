import Container from 'react-bootstrap/Container'
import type { ReactNode } from 'react'

interface PageBannerProps {
  eyebrow: string
  title: string
  lead?: string
  children?: ReactNode
}

/** The typographic interior-page header: wayfinding for every route that isn't the image-led home hero. */
export function PageBanner({ children, eyebrow, lead, title }: PageBannerProps) {
  return (
    <section className="page-banner">
      <Container>
        <p className="cms-section-label">{eyebrow}</p>
        <h1>{title}</h1>
        {lead !== undefined ? <p className="page-banner-lead">{lead}</p> : null}
        {children}
      </Container>
    </section>
  )
}
