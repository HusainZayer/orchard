import { items } from './site.js';
export const PER = 30;
export const TYPES = [
  { slug: '', label: 'All', kinds: null },
  { slug: 'news', label: 'News', kinds: ['news', 'update', 'note'] },
  { slug: 'rumors', label: 'Rumors', kinds: ['rumor'] },
  { slug: 'reviews', label: 'Reviews', kinds: ['review'] },
  { slug: 'issues', label: 'Issues', kinds: ['issue'] },
];
export const listFor = t => (t.kinds ? items.filter(n => t.kinds.includes(n.kind)) : items);
export const pagesFor = t => Math.max(1, Math.ceil(listFor(t).length / PER));
export const hrefFor = (t, p) => (t.slug ? `/news/type/${t.slug}${p > 1 ? `/${p}` : ''}` : (p > 1 ? `/news/page/${p}` : '/news'));
export const paths = () => TYPES.flatMap(t => Array.from({ length: pagesFor(t) }, (_, i) => [t, i + 1]));
