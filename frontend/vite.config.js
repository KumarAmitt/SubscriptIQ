import { fileURLToPath, URL } from 'node:url'
import { existsSync } from 'node:fs'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  envDir: existsSync('../.env') ? '../' : '.',
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': fileURLToPath(new URL('./node_modules/vue/dist/vue.esm-browser.js', import.meta.url)),
      'pinia': fileURLToPath(new URL('./node_modules/pinia/dist/pinia.esm-browser.js', import.meta.url)),
      'vue-router': fileURLToPath(new URL('./node_modules/vue-router/dist/vue-router.esm-browser.js', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
  },
})
