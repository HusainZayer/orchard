import { items, STATUS, trim } from '../../lib/site.js';
import { all } from '../../lib/picks.js';
import { card } from '../../lib/og.js';
export function getStaticPaths() {
  return [
    ...items.map(n => ({ params: { path: `news/${n.id}` }, props: { kicker: n.kind === 'rumor' ? 'Rumor' : 'News', title: trim(n.title, 110), foot: [n.date, n.source].filter(Boolean).join(' · ') } })),
    ...all.map((a, i) => ({ params: { path: `app/${a.id}` }, props: { kicker: `iPhone Duo · Our pick #${i + 1}`, title: a.name, foot: [a.category, STATUS[a.status]].filter(Boolean).join(' · ') } })),
  ];
}
export const GET = ({ props }) => card(props);
