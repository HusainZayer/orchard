import { STATUS, icon } from './site.js';
export const fmt = d => d ? new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }) : '';
export const KIND = { news: 'News', rumor: 'Rumor', update: 'Update', review: 'Review', issue: 'Issue' };
export const PILL = { optimized: ['opt', '✓', 'Optimized'], coming: ['soon', '…', 'Coming'], announced: ['soon', '…', 'Announced'], reported: ['rep', '?', 'Reported'] };
export const srcsOf = n => (n.srcs && n.srcs.length ? n.srcs : (n.link ? [[n.source || 'Source', n.link]] : []));
export const srcLine = n => srcsOf(n).map(s => s[0]).join(', ') || n.source || '';
export const letter = a => (a.name.match(/[A-Za-z0-9]/) || ['•'])[0].toUpperCase();
export { STATUS, icon };
