"""Write the site data (from the master file) to astro/src/data/state.json."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import state
_, st = state.load()
out = ROOT / 'astro' / 'src' / 'data'; out.mkdir(parents=True, exist_ok=True)
(out / 'state.json').write_text(json.dumps({k: st[k] for k in ('updated', 'apps', 'news', 'posts')}, ensure_ascii=False))
print('exported', len(st['apps']), 'apps')
