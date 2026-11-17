import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', 'VITE_')
  if (mode === 'production') {
    let apiUrl
    try {
      apiUrl = new URL(env.VITE_API_URL)
    } catch {
      throw new Error('Production builds require VITE_API_URL to be set to the HTTPS API URL.')
    }

    if (
      apiUrl.protocol !== 'https:' ||
      ['localhost', '127.0.0.1', '0.0.0.0'].includes(apiUrl.hostname) ||
      !apiUrl.pathname.replace(/\/+$/, '').endsWith('/api') ||
      apiUrl.username ||
      apiUrl.password ||
      apiUrl.search ||
      apiUrl.hash
    ) {
      throw new Error('VITE_API_URL must be a public HTTPS API base URL ending in /api.')
    }
  }

  return {
    plugins: [react(), tailwindcss()],
    server: {
      port: 5173,
    },
    test: {
      environment: 'jsdom',
      setupFiles: './src/test/setup.js',
      css: false,
      coverage: {
        provider: 'v8',
        reporter: ['text', 'lcov'],
        exclude: ['src/test/**', 'src/main.jsx'],
      },
    },
  }
})
