import fs from 'node:fs';
import { createRequire } from 'node:module';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
const require = createRequire(import.meta.url);
const f = (pkg, file) => fs.readFileSync(require.resolve(pkg + '/package.json').replace('package.json', 'files/' + file));
const serif = f('@fontsource/newsreader', 'newsreader-latin-600-normal.woff');
const sans = f('@fontsource/ibm-plex-sans', 'ibm-plex-sans-latin-500-normal.woff');
const mono = f('@fontsource/ibm-plex-mono', 'ibm-plex-mono-latin-500-normal.woff');
const h = (type, style, children, extra = {}) => ({ type, props: { style, children, ...extra } });
const dot = (cx, cy, r, leaf) => ({ type: 'circle', props: { cx, cy, r, fill: leaf ? '#C8E36A' : '#1A1A17', ...(leaf ? { stroke: '#1A1A17', 'stroke-width': 2 } : {}) } });
const logo = { type: 'svg', props: { width: 64, height: 60, viewBox: '0 0 30 28', children: [dot(5, 5, 3), dot(13, 5, 3), dot(21, 5, 3.5, true), dot(9, 14, 3), dot(17, 14, 3), dot(25, 14, 3), dot(5, 23, 3), dot(13, 23, 3), dot(21, 23, 3)] } };
export async function card({ kicker, title, foot }) {
  const size = title.length > 90 ? 52 : title.length > 60 ? 64 : title.length > 35 ? 76 : 92;
  const tree = h('div', { width: 1200, height: 630, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: 64, background: '#F7F4EE', color: '#1A1A17', fontFamily: 'Newsreader', borderTop: '16px solid #1E5A44' }, [
    h('div', { display: 'flex', alignItems: 'center', justifyContent: 'space-between' }, [
      h('div', { display: 'flex', alignItems: 'center', gap: 20 }, [logo, h('div', { display: 'flex', fontSize: 44, fontWeight: 600 }, ['Orchard'])]),
      h('div', { display: 'flex', fontFamily: 'IBM Plex Mono', fontSize: 24, color: '#5C5A52', textTransform: 'uppercase', letterSpacing: 2 }, [kicker]),
    ]),
    h('div', { display: 'flex', fontSize: size, lineHeight: 1.1, fontWeight: 600, letterSpacing: -1 }, [title]),
    h('div', { display: 'flex', justifyContent: 'space-between', fontFamily: 'IBM Plex Sans', fontSize: 24, color: '#5C5A52', borderTop: '2px solid #1A1A17', paddingTop: 20 }, [h('div', { display: 'flex' }, [foot || '']), h('div', { display: 'flex' }, ['An independent site about Apple, not affiliated with Apple'])]),
  ]);
  const svg = await satori(tree, { width: 1200, height: 630, fonts: [{ name: 'Newsreader', data: serif, weight: 600, style: 'normal' }, { name: 'IBM Plex Sans', data: sans, weight: 500, style: 'normal' }, { name: 'IBM Plex Mono', data: mono, weight: 500, style: 'normal' }] });
  return new Response(new Resvg(svg).render().asPng(), { headers: { 'Content-Type': 'image/png' } });
}
