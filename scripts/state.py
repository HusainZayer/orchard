"""Read and write the site's data, which lives as JSON inside src/orchard.html."""
import json, re, pathlib
SRC = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'orchard.html'
PAT = re.compile(r'(<script type="application/json" id="state">)(.*?)(</script>)', re.S)

def load():
    html = SRC.read_text()
    return html, json.loads(PAT.search(html).group(2))

def save(html, st):
    js = json.dumps(st, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    m = PAT.search(html)
    SRC.write_text(html[:m.start(2)] + js + html[m.end(2):])
