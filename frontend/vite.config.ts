import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Inside Compose the backend is reached by service name. Override the variable to
// run the dev server outside Docker against http://localhost:8000.
const backendOrigin = process.env.VITE_BACKEND_ORIGIN ?? 'http://backend:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    // Bind mounts do not deliver inotify events reliably on macOS and Windows.
    watch: { usePolling: true },
    // The SPA, API and Django admin share the browser origin. This preserves
    // first-party session cookies and lets admin assets load through Vite too.
    // changeOrigin stays false so Django sees the browser's Host and Origin.
    proxy: {
      '/api': { target: backendOrigin, changeOrigin: false },
      '/media': { target: backendOrigin, changeOrigin: false },
      '/admin': { target: backendOrigin, changeOrigin: false },
      '/static': { target: backendOrigin, changeOrigin: false },
    },
  },
})
