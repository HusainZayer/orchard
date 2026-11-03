import { SITE } from '../lib/site.js';
export const GET = () => new Response(`User-agent: *\nAllow: /\nSitemap: ${SITE}/sitemap.xml\n`, { headers: { 'Content-Type': 'text/plain' } });
