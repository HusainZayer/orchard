"""Write the site data (from the master file) to astro/src/data/state.json."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import state
_, st = state.load()
out = ROOT / 'astro' / 'src' / 'data'; out.mkdir(parents=True, exist_ok=True)
(out / 'state.json').write_text(json.dumps({**{k: st[k] for k in ('updated', 'apps', 'news', 'posts', 'dates')}, 'events': [{k: e.get(k) for k in ('id', 'name', 'date', 'format', 'status')} for e in st.get('events', [])], 'releases': [{k: r.get(k) for k in ('id', 'platform', 'version', 'channel', 'date')} for r in st['releases']], 'devices': {k: st['devices'][k] for k in ('groups', 'lines', 'lineup', 'lineupAsOf', 'sources')}, 'lines': {k: [{'id': g['id'], 'title': g['title'], 'date': g['date']} for g in v] for k, v in st['devices']['lines'].items()}}, ensure_ascii=False))
print('exported', len(st['apps']), 'apps')
