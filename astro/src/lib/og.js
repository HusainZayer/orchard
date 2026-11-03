import fs from 'node:fs';
import { createRequire } from 'node:module';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
const require = createRequire(import.meta.url);
const dir = require.resolve('@fontsource/archivo/package.json').replace('package.json', 'files/');
const font = fs.readFileSync(dir + 'archivo-latin-900-normal.woff');
const h = (type, style, children) => ({ type, props: { style, children } });
export async function card({ kicker, title, foot }) {
  const size = title.length > 90 ? 52 : title.length > 60 ? 64 : title.length > 35 ? 80 : 100;
  const tree = h('div', { width: 1200, height: 630, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: 64, background: '#08080A', color: '#F2F0EB', fontFamily: 'Archivo' }, [
    h('div', { display: 'flex', fontSize: 26, color: '#C6FF3D', letterSpacing: 3, textTransform: 'uppercase' }, ['ORCHARD · ' + kicker]),
    h('div', { display: 'flex', fontSize: size, lineHeight: 1.02, textTransform: 'uppercase', letterSpacing: -1 }, [title]),
    h('div', { display: 'flex', justifyContent: 'space-between', fontSize: 24, color: '#A8A8B0' }, [h('div', { display: 'flex' }, [foot || '']), h('div', { display: 'flex' }, ['Independent · not affiliated with Apple'])]),
  ]);
  const svg = await satori(tree, { width: 1200, height: 630, fonts: [{ name: 'Archivo', data: font, weight: 900, style: 'normal' }] });
  return new Response(new Resvg(svg).render().asPng(), { headers: { 'Content-Type': 'image/png' } });
}
