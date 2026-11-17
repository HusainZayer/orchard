import data from '../data/state.json';
import { items, apps } from './site.js';
import { D, LN, lines } from './devices.js';
export const TODAY = new Date().toISOString().slice(0, 10);
export const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
export const fmt = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
const groups = lines.flatMap(k => ((k === 'iphone' ? D.groups : D.lines[k]) || []).map(g => ({ ...g, line: k })));
export const years = [...new Set((data.events || []).map(e => e.date.slice(0, 4)))].sort();
export function calItems(y) {
  const out = [];
  (data.events || []).forEach(e => { if (e.date.slice(0, 4) === y) out.push({ d: e.date, k: 'Event', t: e.name, sub: e.format || 'Event' }); });
  const rel = {};
  data.releases.forEach(r => { if (r.channel === 'release' && r.platform !== 'Xcode' && r.date.slice(0, 4) === y) (rel[r.date] = rel[r.date] || []).push(r.platform + ' ' + String(r.version).replace('Golden Gate ', '')); });
  Object.entries(rel).forEach(([d, v]) => out.push({ d, k: 'Software', t: v.join(', '), sub: 'Software release' }));
  groups.forEach(g => { if (g.date.slice(0, 4) === y) out.push({ d: g.date, k: 'Launch', t: g.title, sub: LN[g.line] + ' launch', href: `/devices/${g.line}#${g.id}` }); });
  return out.sort((a, b) => a.d.localeCompare(b.d) || a.k.localeCompare(b.k));
}
export const addDays = (d, n) => { const t = new Date(d + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + n); return t.toISOString().slice(0, 10); };
export const weekStart = d => { const t = new Date(d + 'T12:00:00Z'), dow = (t.getUTCDay() + 6) % 7; t.setUTCDate(t.getUTCDate() - dow); return t.toISOString().slice(0, 10); };
export function weekData(ws) {
  const we = addDays(ws, 6), inW = d => d && d >= ws && d <= we && d <= TODAY;
  const news = items.filter(x => inW(x.date));
  const launches = groups.filter(g => inW(g.date));
  const events = (data.events || []).filter(e => inW(e.date));
  const rels = data.releases.filter(r => inW(r.date) && (r.channel === 'release' || r.channel === 'rc')).sort((a, b) => b.date.localeCompare(a.date));
  const duo = apps.filter(a => a.confirmed && inW(a.confirmed.d));
  return { ws, we, news, launches, events, rels, duo };
}
export const curWeek = weekStart(TODAY);
export const weekList = Array.from({ length: 12 }, (_, i) => addDays(curWeek, -7 * i));
export const weekLabel = ws => { const we = addDays(ws, 6); return `${+ws.slice(8)}${ws.slice(5, 7) !== we.slice(5, 7) ? ' ' + MONTHS[+ws.slice(5, 7) - 1].slice(0, 3) : ''} – ${+we.slice(8)} ${MONTHS[+we.slice(5, 7) - 1].slice(0, 3)} ${we.slice(0, 4)}`; };
