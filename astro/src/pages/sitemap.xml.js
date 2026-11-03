import { SITE, apps, items, updated } from '../lib/site.js';
const u = (p, d) => `<url><loc>${SITE}${p}</loc>${d ? `<lastmod>${String(d).slice(0, 10)}</lastmod>` : ''}</url>`;
export const GET = () => new Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  + u('/', updated) + u('/duo-apps', updated) + u('/news', updated)
  + apps.map(a => u(`/duo-apps/${a.id}`, a.edited || a.added)).join('') + items.map(n => u(`/news/${n.id}`, n.date)).join('') + '</urlset>', { headers: { 'Content-Type': 'application/xml' } });
