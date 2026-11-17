// Same ranking as the app's "Our picks": ranked by how well an app uses the fold, from our own data.
import { apps, POST } from './site.js';
export const CATS = ['Productivity', 'Video', 'Music', 'Games', 'Health & Fitness', 'Travel', 'Weather', 'Photo & Video', 'Social', 'Sports', 'Food & Shopping', 'Education', 'Creativity', 'Finance', 'Reading & News', 'Lifestyle'];
export const slug = c => c.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const KNOWN = { folded: 'Folded', open: 'Open', laptop: 'Laptop', tent: 'Tent', split: 'Split View' };
const postures = a => (a.postures || []).filter(k => KNOWN[k]);
export function score(a) {
  if (typeof a.score === 'number' && isFinite(a.score)) return Math.max(0, Math.min(10, a.score));
  const ps = postures(a); if (!ps.length) return null;
  const st = a.status === 'optimized' ? 3 : a.status === 'coming' ? 1 : 0;
  return st + ps.filter(k => k !== 'folded').length + (a.foldFeature ? 2 : 0) + (a.confirmed && a.confirmed.v ? 1 : 0);
}
export function why(a) {
  const out = [], ps = postures(a).filter(k => k !== 'folded');
  if (a.featured) out.push('Apple pick');
  if (a.foldFeature) out.push('Built around the fold');
  if (ps.length >= 2) out.push(`${ps.length} unfolded postures: ${ps.map(k => KNOWN[k]).join(', ')}`);
  else if (ps.length === 1) out.push(`Works ${KNOWN[ps[0]].toLowerCase()} on the inner display`);
  if (a.confirmed && a.confirmed.v) out.push(`Confirmed in release notes (v${String(a.confirmed.v).replace(/^v/i, '')})`);
  return out;
}
const pool = apps.filter(a => a.status === 'optimized' && score(a) !== null);
const ps = a => score(a) * 10 + (a.featured ? 3 : 0);
const cmp = (a, b) => (ps(b) - ps(a)) || a.name.localeCompare(b.name);
pool.sort(cmp);
const per = {}; export const top10 = [];
for (const a of pool) { if (top10.length >= 10) break; per[a.category] = per[a.category] || 0; if (per[a.category] >= 2) continue; per[a.category]++; top10.push(a); }
const seen = new Set(), set = [];
const add = a => { if (!seen.has(a.id) && set.length < 100) { seen.add(a.id); set.push(a); } };
top10.forEach(add); CATS.forEach(c => pool.filter(a => a.category === c).slice(0, 4).forEach(add)); pool.forEach(add);
export const all = top10.concat(set.filter(a => !top10.includes(a)).sort(cmp));
export const cats = CATS.map(c => ({ name: c, slug: slug(c), n: all.filter(a => a.category === c).length })).filter(c => c.n);
