import { useEffect } from 'react'

/** Applies a page's SEO title/description once CMS-derived copy is available; leaves the tag untouched otherwise. */
export function useDocumentMeta(title?: string, description?: string) {
  useEffect(() => {
    if (title !== undefined) {
      document.title = title
    }
    if (description !== undefined) {
      document.querySelector('meta[name="description"]')?.setAttribute('content', description)
    }
  }, [title, description])
}
