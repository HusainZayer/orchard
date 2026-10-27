"""Mechanical updates that are safe to run unattended.

1. App Store: for every app in the directory, refresh version, date, price and
   category. When a new version's release notes mention iPhone Duo, record it as
   confirmed and add an entry to the app's Duo update history. App statuses are
   never changed automatically; that stays an editorial call.
2. Apple software: add new betas, release candidates and releases from Apple's
   developer releases feed.

Prints a one-line summary per change and writes the summary to $GITHUB_OUTPUT
(if set) for the commit message. Exits 0 whether or not anything changed.
"""
import json, os, re, sys, time, urllib.request, email.utils, datetime
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from state import load, save

UA = {'User-Agent': 'Orchard-updater/1.0 (+https://orchard-mu-snowy.vercel.app)'}
TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime('%Y-%m-%d')

def get(url, tries=3):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            print('retry', url[:80], e, file=sys.stderr); time.sleep(3 * (i + 1))
    raise RuntimeError('failed: ' + url)

html, st = load()
log = []

# ---- 1. App Store ----
ids = {}
for a in st['apps']:
    m = re.search(r'id(\d+)', a.get('appStore') or '')
    if m: ids.setdefault(m.group(1), []).append(a)
keys = list(ids)
res = {}
for i in range(0, len(keys), 150):
    data = json.loads(get('https://itunes.apple.com/lookup?country=us&id=' + ','.join(keys[i:i + 150])))
    for x in data.get('results', []):
        res[str(x['trackId'])] = x
    time.sleep(1)
DUO = re.compile(r'iPhone\s*Duo', re.I)
for sid, apps in ids.items():
    x = res.get(sid)
    if not x: continue
    v, d = x.get('version'), (x.get('currentVersionReleaseDate') or '')[:10]
    for a in apps:
        sd = a.get('store') or {}
        if v == sd.get('v') and d == sd.get('d'): continue
        a['store'] = {'v': v, 'd': d, 'p': x.get('formattedPrice') or sd.get('p'), 'g': x.get('primaryGenreName') or sd.get('g')}
        a['edited'] = TODAY
        note = ''
        cf = a.get('confirmed') or {}
        if DUO.search(x.get('releaseNotes') or '') and cf.get('v') != v:
            a['confirmed'] = {'v': v, 'd': d}
            if not a.get('duoVersion'):
                a['duoVersion'], a['duoDate'] = v, d
            a.setdefault('history', []).append({'date': d, 'version': v, 'text': 'App Store release notes for version ' + v + ' mention iPhone Duo', 'link': a['appStore']})
            note = ' (release notes mention iPhone Duo)'
        log.append('App: ' + a['name'] + ' ' + str(sd.get('v')) + ' -> ' + v + note)

# ---- 2. Apple software releases ----
try:
    raw = open(os.environ['FEED_FILE'], 'rb').read() if os.environ.get('FEED_FILE') else get('https://developer.apple.com/news/releases/rss/releases.rss')
    feed = ET.fromstring(raw)
except Exception as e:
    print('WARNING: Apple release feed unavailable:', e, file=sys.stderr)
    feed = ET.fromstring('<rss/>')
TITLE = re.compile(r'^(iOS|iPadOS|macOS|watchOS|tvOS|visionOS|Xcode) ([\d.]+)((?: beta(?: \d+)?)|(?: RC(?: \d+)?))? \(([0-9A-Za-z]+)\)$')
def norm(v): return re.sub(r'(\.0)+(?=$| )', '', re.sub(r'^[A-Za-z ]+ (?=\d)', '', v).replace(' RC', '').strip().lower())
have = {(r['platform'], r['channel'], norm(r['version'])) for r in st['releases']}
# macOS has a name (e.g. "Golden Gate 27.2"). Use the newest named release to learn the current name and major version.
macRel = max((r for r in st['releases'] if r['platform'] == 'macOS' and r['channel'] == 'release' and re.match(r'^[A-Za-z][A-Za-z ]* \d', r['version'])), key=lambda r: r['date'], default=None)
macMajor = re.search(r'(\d+)', macRel['version']).group(1) if macRel else ''
macPrefix = re.match(r'^([A-Za-z][A-Za-z ]* )\d', macRel['version']).group(1) if macRel else ''
for it in feed.iter('item'):
    m = TITLE.match((it.findtext('title') or '').strip())
    if not m: continue
    plat, ver, tag, build = m.group(1), m.group(2), (m.group(3) or '').strip(), m.group(4)
    ch = 'developer' if tag.startswith('beta') else 'rc' if tag.startswith('RC') else 'release'
    vs = ver + (' ' + tag if tag.startswith('beta') or (tag.startswith('RC ') ) else '')
    if plat == 'macOS' and macPrefix and ver.split('.')[0] == macMajor: vs = macPrefix + vs
    if (plat, ch, norm(vs)) in have: continue
    dt = email.utils.parsedate_to_datetime(it.findtext('pubDate')).strftime('%Y-%m-%d')
    rid = 'r-auto-' + re.sub(r'[^a-z0-9]+', '-', (plat + '-' + vs + '-' + ch).lower()).strip('-')
    st['releases'].append({'id': rid, 'platform': plat, 'version': vs, 'channel': ch, 'date': dt, 'link': it.findtext('link') or 'https://developer.apple.com/news/releases/', 'build': build})
    have.add((plat, ch, norm(vs)))
    log.append('Software: ' + plat + ' ' + vs + ' (' + ch + ')')

if log:
    st['updated'] = TODAY
    save(html, st)
summary = (str(len(log)) + ' automatic updates') if log else 'no changes'
print(summary); print('\n'.join(log))
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write('changed=' + ('true' if log else 'false') + '\n')
        f.write('summary=' + summary + '\n')
        f.write('details<<EOF\n' + '\n'.join(log[:60]) + ('\n…and ' + str(len(log) - 60) + ' more' if len(log) > 60 else '') + '\nEOF\n')
