import type { Plugin } from 'vite';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

/* Content-Security-Policy for the production build only (the dev server needs inline scripts for hot reload).
   - script-src 'self': no inline or third-party scripts can run on the page.
   - Code written by visitors runs inside same-origin Web Workers. A worker loaded from a file does not inherit
     this page policy, which is why the page itself does not need 'unsafe-eval'.
   - connect-src allows https because visitors may point the C++/Java runner at their own Judge0 server. */
const CSP = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self'",
  "font-src 'self'",
  "img-src 'self' data:",
  "connect-src 'self' https:",
  "worker-src 'self'",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'none'",
].join('; ');

function csp(): Plugin {
  return {
    name: 'letify-csp',
    apply: 'build',
    transformIndexHtml(html) {
      return html.replace('<!--CSP-->', `<meta http-equiv="Content-Security-Policy" content="${CSP}">`);
    },
  };
}

export default defineConfig({
  // Relative base: the same build works on GitHub Pages (/Letify/), Cloudflare Pages or a custom domain.
  base: './',
  plugins: [react(), csp()],
  build: { target: 'es2022', sourcemap: false, assetsInlineLimit: 0 },
  worker: { format: 'es' },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node',
  },
});
