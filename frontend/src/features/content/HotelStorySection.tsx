import Container from 'react-bootstrap/Container'

import { StayDayRail } from './StayDayRail.tsx'
import type { SiteContent } from '../../shared/api/types.ts'

interface HotelStorySectionProps {
  content: SiteContent
  /** False on the dedicated About page, whose PageBanner already carries `about_title` as the page `<h1>`. */
  showHeading?: boolean
}

/** The "О гостинице" prose plus the feature grid; shared between the home teaser and the full About page. */
export function HotelStorySection({ content, showHeading = true }: HotelStorySectionProps) {
  const aboutParagraphs = content.about_text.split(/\n{2,}/).filter((paragraph) => paragraph.trim() !== '')

  return (
    <>
      <section className="cms-about" id="about" aria-labelledby={showHeading ? 'about-title' : undefined}>
        <Container>
          {showHeading ? (
            <div className="cms-about-head">
              <p className="cms-section-label cms-section-label-dark">О гостинице</p>
              <h2 id="about-title">{content.about_title}</h2>
            </div>
          ) : null}
          <div className="cms-about-prose">
            {aboutParagraphs.map((paragraph) => (
              <p key={paragraph.slice(0, 48)}>{paragraph}</p>
            ))}
          </div>
          <StayDayRail checkInTime={content.check_in_time} checkOutTime={content.check_out_time} />
        </Container>
      </section>
      {content.features.length > 0 ? (
        <section className="cms-features" id="features" aria-labelledby="features-title">
          <Container>
            <div className="cms-section-heading">
              <p className="cms-section-label cms-section-label-dark">В гостинице</p>
              <h2 id="features-title">Всё важное — рядом</h2>
            </div>
            <div className="cms-feature-grid">
              {content.features.map((feature) => (
                <article className="cms-feature-card" key={`${feature.title}-${feature.icon}`}>
                  <span className="cms-feature-icon" aria-hidden="true">
                    {feature.icon}
                  </span>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </article>
              ))}
            </div>
          </Container>
        </section>
      ) : null}
    </>
  )
}
