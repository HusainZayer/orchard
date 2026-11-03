import data from '../data/state.json';
export const SITE = 'https://orchard-mu-snowy.vercel.app';
export const STATUS = { optimized: 'Optimized for iPhone Duo', coming: 'Coming soon to iPhone Duo', announced: 'Announced for iPhone Duo', reported: 'Developer-reported iPhone Duo support' };
export const POST = { folded: 'Folded', open: 'Open', laptop: 'Laptop', tent: 'Tent', stand: 'Stand', tabletop: 'Tabletop' };
export const apps = [...data.apps].sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
export const items = [...data.news, ...data.posts].sort((a, b) => (b.date || '').localeCompare(a.date || ''));
export const updated = data.updated;
export const trim = (s, n = 155) => { s = String(s || '').split(/\s+/).join(' '); return s.length <= n ? s : s.slice(0, n - 1).replace(/\s+\S*$/, '') + '…'; };
export const icon = (a, n = 128) => (a.icon && /^https:\/\/is\d*-ssl\.mzstatic\.com\//.test(a.icon) ? `${a.icon}/${n}x${n}bb.webp` : null);
