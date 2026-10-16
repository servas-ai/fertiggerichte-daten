"""T1938 probe: crawl company-owned 'about/history/facts/careers/press' pages on the row's verified website and extract
candidate sentences for employees / revenue / founding. robots.txt respected, no cookies/JS/login, <=1 req/s per host,
4 hosts in parallel (threads, one process). Output: scripts/facts_T1938/crawl_out.json (snippets only, no full HTML kept)."""
import csv, html, json, re, sys, time, threading, urllib.parse, urllib.request, urllib.robotparser, urllib.error, ssl
from concurrent.futures import ThreadPoolExecutor
UA = "food-connectors/0.1 (+https://github.com/servas-ai/fertiggerichte-daten)"
CTX = ssl.create_default_context()
HINT = re.compile(r"(ueber-?uns|uber-?uns|über-?uns|about|unternehmen|company|geschichte|historie|history|chronik|tradition|zahlen|fakten|facts|"
                  r"karriere|career|jobs|presse|press|news|wir|team|portrait|portr%C3%A4t|profil|who-we-are|chi-siamo|azienda|storia|"
                  r"geschaeftsbericht|annual|nachhaltigkeit|sustainability|philosophie|familie|family|milestones|meilensteine)", re.I)
PATHS = ["/ueber-uns", "/uber-uns", "/unternehmen", "/about", "/about-us", "/de/ueber-uns", "/de/unternehmen", "/geschichte",
         "/unternehmen/geschichte", "/karriere", "/presse", "/en/about-us", "/chi-siamo", "/it/chi-siamo", "/azienda", "/storia"]
EMP = re.compile(r"(\d[\d.,\s]{0,8}\d|\d)\s*(?:\+\s*)?(?:Mitarbeiter|Mitarbeitende|Beschäftigte|MitarbeiterInnen|Mitarbeiter:innen|Mitarbeiter\*innen|Angestellte|Kolleg|employees|staff|dipendenti|collaboratori|people|Menschen)", re.I)
REV = re.compile(r"(Umsatz|Umsätze|Jahresumsatz|Umsatzerlöse|turnover|revenue|sales of|fatturato|Mio\.?\s*(?:€|Euro|EUR)|Millionen\s*(?:€|Euro)|Mrd\.?\s*(?:€|Euro)|million euros|€\s?\d[\d.,]*\s?(?:Mio|Mrd|million|billion))", re.I)
FOUND = re.compile(r"(gegründet|gründete|Gründung|Gründungsjahr|founded|established|since\s+1[89]\d\d|seit\s+1[89]\d\d|seit\s+20[012]\d|fondat[aoe]|dal\s+1[89]\d\d|est\.\s*1[89]\d\d|Firmengeschichte|anno\s+1[89]\d\d)", re.I)
YEAR = re.compile(r"\b(1[789]\d\d|20[012]\d)\b")
_last = {}; _lock = threading.Lock(); _rob = {}
def get(url, timeout=20):
    host = urllib.parse.urlparse(url).netloc
    with _lock:
        t = _last.get(host, 0); wait = 1.1 - (time.time() - t); _last[host] = max(time.time(), t + 1.1)
    if wait > 0: time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-AT,de;q=0.9,en;q=0.6"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            ct = r.headers.get("Content-Type", "")
            if "html" not in ct and "text" not in ct: return None, r.geturl(), f"ctype {ct}"
            return r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace"), r.geturl(), r.status
    except urllib.error.HTTPError as e: return None, url, e.code
    except Exception as e: return None, url, str(e)[:80]
def robots_ok(url):
    p = urllib.parse.urlparse(url); base = f"{p.scheme}://{p.netloc}"
    if base not in _rob:
        rp = urllib.robotparser.RobotFileParser(); txt, _, st = get(base + "/robots.txt", timeout=12)
        if txt is None and st in (401, 403): rp.disallow_all = True
        else: rp.parse((txt or "").splitlines())
        _rob[base] = rp
    return _rob[base].can_fetch(UA, url)
def text(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</td>|</tr>|</section>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h)); t = re.sub(r"[ \t\xa0\u202f]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t)
def snippets(t, rx, need_year=False):
    out = []
    for m in rx.finditer(t):
        a = max(0, m.start() - 220); b = min(len(t), m.end() + 220); s = re.sub(r"\s+", " ", t[a:b]).strip()
        if need_year and not YEAR.search(s): continue
        if s not in out: out.append(s)
    return out[:12]
def crawl(site):
    base = site.rstrip("/"); p = urllib.parse.urlparse(base); root = f"{p.scheme}://{p.netloc}"; dom = p.netloc.replace("www.", "")
    res = {"site": site, "pages": [], "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    start = base + "/" if p.path in ("", "/") else base
    if not robots_ok(start): res["error"] = "robots disallow home"; return res
    h, final, st = get(start)
    if not h: res["error"] = f"home {st}"; return res
    cands = []
    for href, lab in re.findall(r'(?is)<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', h):
        u = urllib.parse.urljoin(final, html.unescape(href).strip())
        q = urllib.parse.urlparse(u)
        if q.scheme not in ("http", "https") or not q.netloc.replace("www.", "").endswith(dom.split(":")[0]): continue
        if re.search(r"\.(pdf|jpg|png|zip|svg|webp)$", q.path, re.I): continue
        if HINT.search(q.path + " " + text(lab)) and not re.search(r"impressum|datenschutz|privacy|agb|cookie|login|warenkorb|cart|/produkte?/|/product", q.path, re.I):
            u = u.split("#")[0]
            if u not in cands: cands.append(u)
    for x in PATHS:
        if root + x not in cands: cands.append(root + x)
    pages = [(final, h)]; seen = {final}
    for u in cands[:14]:
        if len(pages) >= 9: break
        if u in seen: continue
        seen.add(u)
        if not robots_ok(u): continue
        hh, fu, st = get(u)
        if hh and fu not in [x[0] for x in pages]: pages.append((fu, hh))
    for u, hh in pages:
        t = text(hh)
        res["pages"].append({"url": u, "emp": snippets(t, EMP), "rev": snippets(t, REV), "found": snippets(t, FOUND, True)})
    return res
if __name__ == "__main__":
    rows = list(csv.DictReader(open("data/companies.csv")))
    sites = sorted({r["website"].strip() for r in rows if r["website"].strip() and (not r["employees"].strip() or not r["revenue"].strip() or not r["founded"].strip())})
    out = {}
    with ThreadPoolExecutor(4) as ex:
        for s, r in zip(sites, ex.map(crawl, sites)):
            out[s] = r; print(s, r.get("error") or len(r["pages"]), flush=True)
    json.dump(out, open("scripts/facts_T1938/crawl_out.json", "w"), ensure_ascii=False, indent=1)
