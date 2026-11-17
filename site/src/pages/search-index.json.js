import { items, apps, trim } from '../lib/site.js';
import { lines, LN, groupsOf } from '../lib/devices.js';
import data from '../data/state.json';
// t: title, u: url, k: type, s: short text. Pagefind replaces this in the data phase.
const out = [
  ...items.map(n => ({ t: n.title, u: `/news/${n.id}`, k: n.kind === 'rumor' ? 'Rumor' : 'News', s: trim(n.body, 120), d: n.date })),
  ...apps.map(a => ({ t: a.name, u: `/duo-apps/${a.id}`, k: 'Duo app', s: [a.developer, a.category].filter(Boolean).join(' · ') })),
  ...lines.flatMap(k => groupsOf(k).map(g => ({ t: g.title, u: `/launches/${g.id}`, k: LN[k], s: g.date, d: g.date }))),
  ...(data.events || []).map(e => ({ t: e.name, u: `/events/${e.id}`, k: 'Event', s: e.date, d: e.date })),
];
export const GET = () => new Response(JSON.stringify(out), { headers: { 'Content-Type': 'application/json' } });
