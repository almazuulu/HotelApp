import type { ConfirmationMode } from '../../shared/api/types.ts'

const LABEL: Record<ConfirmationMode, string> = {
  automatic: 'Мгновенное подтверждение',
  manual: 'Подтверждение менеджером',
}

export function ConfirmationBadge({ mode }: { mode: ConfirmationMode }) {
  return (
    <span className={`confirmation-badge${mode === 'automatic' ? ' confirmation-badge-instant' : ''}`}>
      {LABEL[mode]}
    </span>
  )
}
