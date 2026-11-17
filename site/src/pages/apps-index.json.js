import { apps, icon } from '../lib/site.js';
const rows = apps.map(a => { const ic = icon(a, 128); return { i: a.id, n: a.name, d: a.developer || '', c: a.category || '', s: a.status, p: a.postures || [], $: a.price || (a.store && a.store.p) || '', e: a.edited || '', m: ic || '' }; });
export const GET = () => new Response(JSON.stringify(rows), { headers: { 'Content-Type': 'application/json' } });
