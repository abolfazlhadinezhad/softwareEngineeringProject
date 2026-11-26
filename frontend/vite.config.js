import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const target = process.env.VITE_API_PROXY_TARGET || 'http://backend:8000';
export default defineConfig({
  plugins: [react()],
  server: { host: '0.0.0.0', port: 5173, strictPort: true, watch: { usePolling: true }, proxy: {
    '/api': { target, changeOrigin: false }, '/admin': { target, changeOrigin: false }, '/static': { target, changeOrigin: false },
  } },
  test: { environment: 'jsdom', setupFiles: './src/test/setup.js', exclude: ['e2e/**', 'node_modules/**'] },
});
