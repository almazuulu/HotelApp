import { createBrowserRouter } from 'react-router-dom'

import { AboutPage } from '../pages/AboutPage.tsx'
import { AccountPage } from '../pages/AccountPage.tsx'
import { CatalogPage } from '../pages/CatalogPage.tsx'
import { ContactsPage } from '../pages/ContactsPage.tsx'
import { HomePage } from '../pages/HomePage.tsx'
import { LoginPage } from '../pages/LoginPage.tsx'
import { NotFoundPage } from '../pages/NotFoundPage.tsx'
import { RegisterPage } from '../pages/RegisterPage.tsx'
import { RoomTypeDetailPage } from '../pages/RoomTypeDetailPage.tsx'

export const appRouter = createBrowserRouter([
  { path: '/', element: <HomePage /> },
  { path: '/rooms', element: <CatalogPage /> },
  { path: '/rooms/:slug', element: <RoomTypeDetailPage /> },
  { path: '/about', element: <AboutPage /> },
  { path: '/contacts', element: <ContactsPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/account', element: <AccountPage /> },
  { path: '*', element: <NotFoundPage /> },
])
