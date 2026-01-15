import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // ★これが超重要
    port: 5173,
    watch: {
      usePolling: true // WindowsのDockerで変更を検知させるおまじない
    }
  }
})