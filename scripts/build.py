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
<meta name="theme-color" content="#F5F0E6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14110D" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{chr(10).join(fonts)}
<style>{RESET}</style>
</head>
<body>
'''
(ROOT / 'index.html').write_text(head + body + '\n</body>\n</html>\n')

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
cfg = {'cleanUrls': True, 'headers': heads + [{'source': '/', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=0, must-revalidate'}]}]}
(ROOT / 'vercel.json').write_text(json.dumps(cfg, indent=1))
print('built index.html,', len(heads), 'images')
