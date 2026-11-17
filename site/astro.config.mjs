import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://orchard-mu-snowy.vercel.app',
  build: { format: 'directory' },
  trailingSlash: 'never',
  devToolbar: { enabled: false },
});
