import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,           // 允许外部访问（可选）
    allowedHosts: [
      'https://battery-said-purr.ngrok-free.dev',  // 你的 ngrok 域名
      '.ngrok-free.dev',   // 或者允许所有 ngrok 二级域名
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})