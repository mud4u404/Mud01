import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: { host: '0.0.0.0', port: 5173 },
  preview: { host: '0.0.0.0', port: 4173 },
  build: {
    assetsInlineLimit: 0,
    chunkSizeWarningLimit: 8192
  }
});
