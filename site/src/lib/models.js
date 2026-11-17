import { D, LN, lines, groupsOf } from './devices.js';
// Every model we hold data for, flattened: used by line pages, the buying guide and compare.
export const allModels = lines.flatMap(k => groupsOf(k).flatMap(g => (g.models || []).map(m => ({ ...m, line: k, group: g.id, date: g.date }))));
export const byName = new Map(); allModels.forEach(m => { const key = m.line + '|' + m.name; if (!byName.has(key)) byName.set(key, m); });
export const find = (line, name) => byName.get(line + '|' + name);
export const price = p => { const m = String(p || '').replace(/,/g, '').match(/\$(\d+(?:\.\d+)?)/); return m ? +m[1] : null; };
export const dash = v => (v && v !== '—' && v !== 'None' ? v : '');
