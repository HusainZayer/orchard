"""Static, indexable pages: /duo-apps/<id>, /news/<id>, hubs, sitemap.xml, robots.txt, feed.xml.
Everything comes from the same state JSON as the app; nothing is invented."""
import json, pathlib, html, shutil
from email.utils import format_datetime
import datetime as dt
SITE = 'https://orchard-mu-snowy.vercel.app'
E = lambda s: html.escape(str(s or ''), quote=True)
STATUS = {'optimized': 'Optimized for iPhone Duo', 'coming': 'Coming soon to iPhone Duo', 'announced': 'Announced for iPhone Duo', 'reported': 'Developer-reported iPhone Duo support'}
POST = {'folded': 'Folded', 'open': 'Open', 'laptop': 'Laptop', 'tent': 'Tent', 'stand': 'Stand', 'tabletop': 'Tabletop'}
CSS = ('body{margin:0;font:17px/1.55 system-ui,-apple-system,sans-serif;background:#F2F0EB;color:#111}@media(prefers-color-scheme:dark){body{background:#08080A;color:#EEE}a{color:#C6FF3D}.k{color:#aaa}}'
       'main{max-width:42rem;margin:0 auto;padding:24px 16px 64px}a{color:#111;text-underline-offset:3px}h1{font-size:2rem;line-height:1.1;margin:.4em 0}.k{font:600 12px/1 ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:#555}'
       'nav a{margin-right:1rem}.btn{display:inline-block;margin:1rem 0;padding:.7em 1.1em;border:2px solid currentColor;font-weight:700;text-decoration:none}li{margin:.3em 0}footer{margin-top:3rem;font-size:14px;opacity:.75}')

def page(path, title, desc, body, ld=None, typ='website'):
    url = SITE + path
    j = ('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>') if ld else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · Orchard</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{typ}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Orchard" href="/feed.xml">
<style>{CSS}</style>{j}</head><body><main><nav class="k"><a href="/">Orchard</a><a href="/news">News</a><a href="/duo-apps">Duo apps</a></nav>
{body}<footer>An independent site about Apple, not affiliated with Apple. <a href="/">Open the full Orchard app</a></footer></main></body></html>'''

def trim(s, n=155):
    s = ' '.join(str(s or '').split())
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'

def build(root, st):
    out = pathlib.Path(root)
    for d in ('duo-apps', 'news'):
        shutil.rmtree(out / d, ignore_errors=True); (out / d).mkdir()
    urls = [('/', st.get('updated'))]
    apps = sorted(st['apps'], key=lambda a: a['name'].lower())
    for a in apps:
        s = a.get('status'); lab = STATUS.get(s, 'iPhone Duo app')
        store = a.get('store') or {}
        facts = [f'<li><b>Status:</b> {E(lab)}</li>', f'<li><b>Developer:</b> {E(a.get("developer"))}</li>', f'<li><b>Category:</b> {E(a.get("category"))}</li>']
        if a.get('postures'): facts.append('<li><b>Fold positions it uses:</b> ' + ', '.join(POST.get(p, p.title()) for p in a['postures']) + '</li>')
        if store.get('v'): facts.append(f'<li><b>Latest version:</b> {E(store["v"])}' + (f' ({E(store["d"])})' if store.get('d') else '') + '</li>')
        c = a.get('confirmed')
        if c: facts.append(f'<li><b>Release notes mention iPhone Duo:</b> version {E(c.get("v"))}, {E(c.get("d"))}</li>')
        hist = ''.join(f'<li>{E(h.get("date"))}: {E(h.get("text"))}</li>' for h in (a.get('history') or [])[:8])
        links = []
        if a.get('link'): links.append(f'<a href="{E(a["link"])}" rel="noopener">Source</a>')
        if a.get('appStore'): links.append(f'<a href="{E(a["appStore"])}" rel="noopener">App Store</a>')
        body = f'<p class="k">{E(lab)}</p><h1>{E(a["name"])}</h1><p>{E(a.get("body"))}</p><ul>{"".join(facts)}</ul>' \
               + (f'<h2>History</h2><ul>{hist}</ul>' if hist else '') \
               + f'<p>{" · ".join(links)}</p><a class="btn" href="/#{E(a["id"])}">See it in Orchard</a>'
        ld = {'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': a['name'], 'applicationCategory': a.get('category') or 'Application', 'operatingSystem': 'iOS', 'author': {'@type': 'Organization', 'name': a.get('developer') or ''}}
        if a.get('appStore'): ld['url'] = a['appStore']
        (out / 'duo-apps' / f'{a["id"]}.html').write_text(page(f'/duo-apps/{a["id"]}', f'{a["name"]} on iPhone Duo', trim(f'{lab}. {a.get("body")}'), body, ld))
        urls.append((f'/duo-apps/{a["id"]}', a.get('edited') or a.get('added')))
    groups = {}
    for a in apps: groups.setdefault(STATUS.get(a.get('status'), 'Other'), []).append(a)
    hub = ''.join(f'<h2>{E(k)} ({len(v)})</h2><ul>' + ''.join(f'<li><a href="/duo-apps/{a["id"]}">{E(a["name"])}</a> <span class="k">{E(a.get("category"))}</span></li>' for v in [v] for a in v) + '</ul>'
                  for k, v in sorted(groups.items(), key=lambda kv: list(STATUS.values()).index(kv[0]) if kv[0] in STATUS.values() else 9))
    (out / 'duo-apps' / 'index.html').write_text(page('/duo-apps', 'iPhone Duo apps', f'{len(apps)} apps with their iPhone Duo status, each with its source.', f'<h1>iPhone Duo apps</h1><p>{len(apps)} apps, each with a status and a source. Apple-listed apps come first; developer-reported ones are labelled as such.</p>' + hub))
    urls.append(('/duo-apps', st.get('updated')))
    items = sorted([n for n in st.get('news', []) + st.get('posts', [])], key=lambda n: n.get('date') or '', reverse=True)
    for n in items:
        srcs = n.get('srcs') or ([[n.get('source') or 'Source', n['link']]] if n.get('link') else [])
        sl = ''.join(f'<li><a href="{E(u)}" rel="noopener">{E(t)}</a></li>' for t, u in srcs)
        body = f'<p class="k">{E(n.get("date"))}</p><h1>{E(n["title"])}</h1><p>{E(n.get("body"))}</p>' + (f'<h2>Sources</h2><ul>{sl}</ul>' if sl else '') + f'<a class="btn" href="/#{E(n["id"])}">See it in Orchard</a>'
        ld = {'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': n['title'], 'datePublished': n.get('date'), 'publisher': {'@type': 'Organization', 'name': 'Orchard'}}
        (out / 'news' / f'{n["id"]}.html').write_text(page(f'/news/{n["id"]}', n['title'], trim(n.get('body')), body, ld, 'article'))
        urls.append((f'/news/{n["id"]}', n.get('date')))
    (out / 'news' / 'index.html').write_text(page('/news', 'Apple news and rumors', 'Apple news, rumors and updates, each with its sources.', '<h1>News</h1><ul>' + ''.join(f'<li><span class="k">{E(n.get("date"))}</span> <a href="/news/{n["id"]}">{E(n["title"])}</a></li>' for n in items) + '</ul>'))
    urls.append(('/news', st.get('updated')))
    sm = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}{p}</loc>' + (f'<lastmod>{str(d)[:10]}</lastmod>' if d else '') + '</url>' for p, d in urls) + '</urlset>'
    (out / 'sitemap.xml').write_text(sm)
    (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    def rfc(d):
        try: return format_datetime(dt.datetime.strptime(str(d)[:10], '%Y-%m-%d').replace(tzinfo=dt.timezone.utc))
        except Exception: return format_datetime(dt.datetime.now(dt.timezone.utc))
    feed = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Orchard</title><link>' + SITE + '</link><description>Apple news, rumors and iPhone Duo apps, each with its source. An independent site, not affiliated with Apple.</description>' \
        + ''.join(f'<item><title>{E(n["title"])}</title><link>{SITE}/news/{n["id"]}</link><guid>{SITE}/news/{n["id"]}</guid><pubDate>{rfc(n.get("date"))}</pubDate><description>{E(trim(n.get("body"), 300))}</description></item>' for n in items[:40]) + '</channel></rss>'
    (out / 'feed.xml').write_text(feed)
    return len(urls)
