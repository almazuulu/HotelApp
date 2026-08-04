import Container from 'react-bootstrap/Container'
import type { ReactNode } from 'react'

interface StatusSectionProps {
  variant: 'loading' | 'error'
  eyebrow: string
  title: string
  description?: string
  action?: ReactNode
}

/**
 * The shared loading/error band for public pages: a skeleton while pending, a titled message with an
 * optional recovery action on failure. Reuses the home page's original `cms-status` visual language.
 */
export function StatusSection({ action, description, eyebrow, title, variant }: StatusSectionProps) {
  const isLoading = variant === 'loading'

  return (
    <section
      className={`cms-status${isLoading ? ' cms-status-loading' : ''}`}
      aria-busy={isLoading ? 'true' : undefined}
      aria-live={isLoading ? undefined : 'polite'}
    >
      <Container>
        <p className="cms-section-label">{eyebrow}</p>
        {isLoading ? (
          <>
            <h1 className="visually-hidden">{title}</h1>
            <span className="cms-skeleton cms-skeleton-title" />
            <span className="cms-skeleton cms-skeleton-line" />
            <span className="cms-skeleton cms-skeleton-line cms-skeleton-line-short" />
            {description !== undefined ? (
              <p className="visually-hidden" aria-live="polite">
                {description}
              </p>
            ) : null}
          </>
        ) : (
          <>
            <h1>{title}</h1>
            {description !== undefined ? <p>{description}</p> : null}
            {action}
          </>
        )}
      </Container>
    </section>
  )
}
