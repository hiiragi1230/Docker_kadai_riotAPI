import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // ★これが超重要
    port: 5173,
    // ★ここから追加
    proxy: {
      '/api': {
        // 'app' は docker-compose.yml に書いたバックエンドのサービス名です
        // もしサービス名を 'backend' などにしている場合は書き換えてください
        target: 'http://backend:8000', 
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '') // '/api' を消して転送
      }
    },
    //
    watch: {
      usePolling: true // WindowsのDockerで変更を検知させるおまじない
    }
  }
})