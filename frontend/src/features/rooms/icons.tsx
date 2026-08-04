import type { SVGProps } from 'react'

/** Minimal line-icon set for the room fact sheet: one stroke weight, no icon-font dependency. */
function RoomFactIcon({ children, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      {children}
    </svg>
  )
}

export function AdultsIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <RoomFactIcon {...props}>
      <circle cx="10" cy="5.6" r="2.6" />
      <path d="M4 17c0-3.4 2.7-6 6-6s6 2.6 6 6" />
    </RoomFactIcon>
  )
}

export function ChildrenIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <RoomFactIcon {...props}>
      <circle cx="10" cy="6.4" r="2" />
      <path d="M5.6 17c0-2.7 2-4.7 4.4-4.7s4.4 2 4.4 4.7" />
    </RoomFactIcon>
  )
}

export function BedIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <RoomFactIcon {...props}>
      <path d="M2.5 15.5V7a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 8.5 7v3" />
      <path d="M2.5 15.5v-2A1.5 1.5 0 0 1 4 12h12a1.5 1.5 0 0 1 1.5 1.5v2" />
      <path d="M11.5 10V7A1.5 1.5 0 0 1 13 5.5h3A1.5 1.5 0 0 1 17.5 7v3" />
      <path d="M2.5 12v-1a1.5 1.5 0 0 1 1.5-1.5h12A1.5 1.5 0 0 1 17.5 11v1" />
    </RoomFactIcon>
  )
}

export function AreaIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <RoomFactIcon {...props}>
      <path d="M7 2.5H2.5V7" />
      <path d="M13 2.5h4.5V7" />
      <path d="M7 17.5H2.5V13" />
      <path d="M13 17.5h4.5V13" />
    </RoomFactIcon>
  )
}
