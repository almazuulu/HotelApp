/** Shortens text to `maxLength`, breaking cleanly for a meta-description-sized snippet. */
export function truncate(text: string, maxLength: number): string {
  const trimmed = text.trim()

  return trimmed.length > maxLength ? `${trimmed.slice(0, maxLength - 1).trimEnd()}…` : trimmed
}

/** Drops a redundant ".00" from a Decimal-string USD amount without ever parsing it as a float. */
export function formatUsd(amount: string): string {
  return amount.endsWith('.00') ? amount.slice(0, -3) : amount
}
