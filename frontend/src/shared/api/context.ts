import { createContext } from 'react'

import { type ApiClient } from './client.ts'

export const ApiClientContext = createContext<ApiClient | null>(null)
