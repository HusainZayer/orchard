"""Watch Apple news sources and start the Claude refresh task as soon as something new appears.

Runs every 30 minutes from .github/workflows/detect.yml. It is cheap: it only reads
RSS feeds, compares them with what it has already seen, and, when there is
something new and relevant, calls the scheduled task's API trigger with a list of
the new items (the task then researches and publishes them).

Secrets (GitHub repo settings > Secrets and variables > Actions):
  ORCHARD_FIRE_URL    the task's Fire URL
  ORCHARD_FIRE_TOKEN  the task's API token
Without them it still runs and logs what it would have sent.
"""
import json, os, re, sys, time, datetime, urllib.request, email.utils
import xml.etree.ElementTree as ET

SEEN_FILE = os.environ.get('SEEN_FILE', '.cache/seen.json')
MIN_GAP_MIN = int(os.environ.get('MIN_GAP_MIN', '30'))   # never fire more often than this
UA = {'User-Agent': 'Orchard-watcher/1.0 (+https://orchard-mu-snowy.vercel.app)'}

# (name, url, filter). filter None = every item counts; otherwise a regex the title must match.
FEEDS = [
    ('Apple Newsroom', 'https://www.apple.com/newsroom/rss-feed.rss', None),
    ('Apple Developer releases', 'https://developer.apple.com/news/releases/rss/releases.rss',
     re.compile(r'^(iOS|iPadOS|macOS|watchOS|tvOS|visionOS) [\d.]+( RC)?( \d)? \(', re.I)),  # public releases and RCs, not betas
    ('MacRumors', 'https://feeds.macrumors.com/MacRumors-All',
     re.compile(r'iPhone Duo|Gurman|Kuo|Apple (Announces|Releases|Launches|Unveils|Confirms|Responds)|Pro and Tell|\bM6\b|HomeView|iPad mini|recall|outage', re.I)),
    ('9to5Mac', 'https://9to5mac.com/feed/',
     re.compile(r'iPhone Duo|Gurman|Apple (announces|releases|launches|unveils|confirms|responds)|Pro and Tell|\bM6\b', re.I)),
]

def fetch(url):
    if os.environ.get('FEEDS_DIR'):   # local testing
        p = os.path.join(os.environ['FEEDS_DIR'], re.sub(r'[^a-z0-9]+', '_', url.lower()) + '.xml')
        return open(p, 'rb').read() if os.path.exists(p) else b'<rss/>'
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except Exception as e:
            print('retry', url, e, file=sys.stderr); time.sleep(2 * (i + 1))
    print('WARNING: could not read', url, file=sys.stderr)
    return b'<rss/>'

def items(raw):
    try: root = ET.fromstring(raw)
    except ET.ParseError: return []
    out = []
    for it in root.iter():
        tag = it.tag.split('}')[-1]
        if tag not in ('item', 'entry'): continue
        get = lambda n: next((c for c in it if c.tag.split('}')[-1] == n), None)
        first = lambda *ns: next((x for x in (get(n) for n in ns) if x is not None), None)
        t = get('title'); l = get('link'); g = first('guid', 'id'); d = first('pubDate', 'updated', 'published')
        link = (l.get('href') if l is not None and l.get('href') else (l.text if l is not None else '')) or ''
        out.append({'title': (t.text or '').strip() if t is not None else '', 'link': link.strip(),
                    'id': ((g.text if g is not None else '') or link or (t.text if t is not None else '')).strip(),
                    'date': (d.text or '').strip() if d is not None else ''})
    return out

os.makedirs(os.path.dirname(SEEN_FILE) or '.', exist_ok=True)
state = json.load(open(SEEN_FILE)) if os.path.exists(SEEN_FILE) else {}
seen = set(state.get('seen', []))
pending = state.get('pending', [])
first_run = not seen
now = time.time()

for name, url, flt in FEEDS:
    for it in items(fetch(url)):
        if not it['id'] or it['id'] in seen: continue
        seen.add(it['id'])
        if first_run: continue                      # first run only learns what already exists
        if flt is not None and not flt.search(it['title']): continue
        pending.append({'source': name, 'title': it['title'], 'link': it['link'], 'date': it['date']})

fired = False
gap_ok = now - state.get('last_fire', 0) >= MIN_GAP_MIN * 60
if pending and gap_ok:
    text = 'New items spotted by the Orchard watcher (cover these first, then do the usual checks):\n' + '\n'.join(
        '- [' + p['source'] + '] ' + p['title'] + ' | ' + p['link'] for p in pending[:25])
    url, tok = os.environ.get('ORCHARD_FIRE_URL'), os.environ.get('ORCHARD_FIRE_TOKEN')
    if url and tok:
        req = urllib.request.Request(url, data=json.dumps({'text': text}).encode(), method='POST', headers={
            'Authorization': 'Bearer ' + tok, 'anthropic-beta': 'experimental-cc-routine-2026-04-01',
            'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'})
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=30).read() or b'{}')
            print('Started refresh:', r.get('claude_code_session_url', r))
            fired = True
        except Exception as e:
            print('WARNING: could not start the refresh task:', e, file=sys.stderr)
    else:
        print('Secrets not set; would have sent:\n' + text)
    if fired:
        pending = []
        state['last_fire'] = now
elif pending:
    print(len(pending), 'new item(s) waiting; last refresh started less than', MIN_GAP_MIN, 'minutes ago')

state['seen'] = sorted(seen)[-3000:]
state['pending'] = pending
json.dump(state, open(SEEN_FILE, 'w'))
print(('First run: learned ' + str(len(seen)) + ' existing items' if first_run else 'Checked feeds') + ' | waiting: ' + str(len(pending)) + ' | refresh started: ' + str(fired))
