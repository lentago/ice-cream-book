import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import pagefind from 'astro-pagefind';
import { rehypeRedact } from './src/lib/redact.mjs';

export default defineConfig({
  site: 'https://icecreamtofightwith.com',
  integrations: [sitemap(), pagefind()],
  markdown: {
    rehypePlugins: [rehypeRedact],
  },
});
