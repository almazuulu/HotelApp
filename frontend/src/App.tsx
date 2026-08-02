import { AppProviders } from './app/AppProviders.tsx'
import { appRouter } from './app/router.tsx'

import { RouterProvider } from 'react-router-dom'

export function App() {
  return (
    <AppProviders>
      <RouterProvider router={appRouter} />
    </AppProviders>
  )
}
