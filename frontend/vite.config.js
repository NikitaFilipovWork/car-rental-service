import { fileURLToPath, URL } from 'node:url';

import { defineConfig, loadEnv } from 'vite';
import vue2 from '@vitejs/plugin-vue2';

export default defineConfig(({ mode }) => {
  const env = { ...loadEnv(mode, process.cwd(), ''), ...process.env };
  // Django backend; requests to /api and /media are proxied there, so no CORS is needed
  const target = env.VITE_PROXY_TARGET || 'http://localhost:8000';

  return {
    plugins: [vue2()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 5173,
      proxy: {
        '/api': { target },
        '/media': { target }
      }
    }
  };
});
