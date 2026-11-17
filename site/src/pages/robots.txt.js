import { SITE } from '../lib/site.js';
// Search engines and answer-engine crawlers are welcome; crawlers that only collect training data are not.
export const GET = () => new Response(`User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nUser-agent: Google-Extended\nDisallow: /\n\nSitemap: ${SITE}/sitemap.xml\n`, { headers: { 'Content-Type': 'text/plain' } });
