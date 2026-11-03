"""Build the public site (index.html + vercel.json) from src/orchard.html."""
import json, os, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / 'src' / 'orchard.html').read_text()
body = re.sub(r'<title>.*?</title>\s*', '', src, count=1, flags=re.S)
body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', '', body, count=1)
fonts = re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', body[:2000])
for f in fonts: body = body.replace(f, '', 1)
RESET = ':root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}'
DESC = 'News, rumors, devices, events and iPhone Duo apps, each with its source, plus a rumor tracker that keeps score. An independent site about Apple, not affiliated with Apple.'
head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="orchard-hosted" content="1">
<title>Orchard · Everything Apple, neatly in rows</title>
<meta name="description" content="{DESC}">
<meta property="og:title" content="Orchard">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://orchard-mu-snowy.vercel.app/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://orchard-mu-snowy.vercel.app/">
<link rel="alternate" type="application/rss+xml" title="Orchard" href="/feed.xml">
<meta name="theme-color" content="#F2F0EB" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E0E10" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{chr(10).join(fonts)}
<style>{RESET}</style>
</head>
<body>
'''
# Speed: the app directory is most of the data and only the Duo apps pages need it.
# Move it to the end of the page so the rest renders first; the page loads it once it arrives.
_PAT = re.compile(r'(<script type="application/json" id="state">)(.*?)(</script>)', re.S)
_m = _PAT.search(body)
tail = ''
if _m:
    _st = json.loads(_m.group(2))
    _apps = _st.pop('apps', None)
    if _apps is not None:
        _enc = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
        body = body[:_m.start(2)] + _enc(_st) + body[_m.end(2):]
        tail = '\n<script type="application/json" id="apps-data">' + _enc(_apps) + '</script>'
(ROOT / 'index.html').write_text(head + body + tail + '\n</body>\n</html>\n')

def ctype(p):
    b = open(p, 'rb').read(12)
    if b[:8] == b'\x89PNG\r\n\x1a\n': return 'image/png'
    if b[:3] == b'\xff\xd8\xff': return 'image/jpeg'
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP': return 'image/webp'
    if b[:3] == b'GIF': return 'image/gif'
    return 'application/octet-stream'
heads = []
blob = ROOT / '_blob'
for f in sorted(os.listdir(blob)):
    heads.append({'source': '/_blob/' + f, 'headers': [{'key': 'Content-Type', 'value': ctype(blob / f)}, {'key': 'Cache-Control', 'value': 'public, max-age=31536000, immutable'}]})
missing = sorted(set(re.findall(r'/_blob/([0-9a-f]{32})', src)) | set(re.findall(r'"iconId":"([0-9a-f]{32})"', src)) - set(os.listdir(blob)))
if missing: print('WARNING: images referenced but missing from _blob/:', missing)
short = [{'key': 'Cache-Control', 'value': 'public, max-age=0, must-revalidate'}]
cfg = {'cleanUrls': True, 'headers': heads + [
 {'source': '/', 'headers': short},
 {'source': '/(duo-apps|news)(/.*)?', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=300, s-maxage=3600, stale-while-revalidate=86400'}]},
 {'source': '/(sitemap.xml|feed.xml|robots.txt)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=300, s-maxage=3600'}]},
 {'source': '/og.png', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=86400'}]}]}
(ROOT / 'vercel.json').write_text(json.dumps(cfg, indent=1))
import sys; sys.path.insert(0, str(ROOT / 'scripts'))
import static_pages, state as _state
_h, _st = _state.load()
_n = static_pages.build(ROOT, _st)
print('static pages:', _n)
print('built index.html,', len(heads), 'images')
