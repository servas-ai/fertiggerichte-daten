#!/usr/bin/env python3
"""Daten-Squad T2307 — companies revenue tail via North Data public company pages + MPreis/Billa photo tail.

Task A (companies): North Data (www.northdata.de) public company pages for DE rows that lack employees/revenue and
carry a register id. robots.txt (/ui/<v>/robots.txt) only disallows a list of named crawlers, no '*' group.
Requests go through food_connectors.polite (hard robots gate) with >=10 s between requests, max 40, stop on the first
HTTP 429/403/captcha. The public page embeds the 'Finanzielle Entwicklung' bar-chart data in
<div class="tab-content has-bar-charts" data-data=...>; indicators that are paywalled are rendered as
<button data-censored="true"> tabs and shipped WITHOUT data points (e.g. 'Mitarbeiter' everywhere,
'Umsatz' for small companies) -> never taken. Only uncensored, estimate=false data points from a published
Jahresabschluss/Konzernabschluss are accepted, latest fiscal year, and only when the page title carries the row's
register court + number (and the LEI where the row has one). Scope: consolidated=true -> group (Konzern).

Task B (photos): rows of MPreis/Billa without image_url; MPreis webshop product JSON-LD (mpreis-shop connector) and
BILLA product-discovery API (billa connector) by exact EAN, HEAD 200, vision-gated by hand (front packshot of the
exact product). Decisions are recorded in the evidence JSON; this script applies them.

usage: companies_northdata_T2307.py [--fetch TARGETS.tsv] [--html-dir /tmp/nd_T2307] --apply
"""
import csv, html, json, os, re, sys, time, urllib.error, urllib.request

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = "2026-10-16T2307"
UA = "food-connectors/0.1 (+https://github.com/servas-ai/fertiggerichte-daten)"
CENSOR_MARKERS = ("captcha", "cf-challenge", "are you a robot", "zu viele anfragen")

def fetch(targets, out_dir, max_req=40, gap=10):
    sys.path.insert(0, "/workspace/food-connectors")
    from food_connectors.polite import polite_urlopen
    log = []
    for n, (tag, url) in enumerate(targets):
        if n >= max_req: break
        if n: time.sleep(gap)
        rec = {"tag": tag, "url": url, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        try:
            with polite_urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de"}), timeout=30) as r:
                body = r.read().decode("utf-8", "replace"); rec["status"] = r.status
        except urllib.error.HTTPError as e:
            body = ""; rec["status"] = e.code
        open(os.path.join(out_dir, tag + ".html"), "w").write(body); log.append(rec)
        if rec["status"] in (403, 429) or any(k in body.lower() for k in CENSOR_MARKERS):
            rec["stopped"] = True; break
    return log

def parse(path):
    t = open(path).read()
    title = html.unescape((re.findall(r"<title>(.*?)</title>", t, re.S) or [""])[0]).strip()
    menu = re.search(r'<div class="column bar-charts">(.*?)<div class="tab-content', t, re.S)
    censored = [html.unescape(nm).strip() for c, nm in re.findall(
        r'<button class="item[^"]*"(?: data-censored="(\w+)")?[^>]*>([^<]+)</button>', menu.group(1)) if c == "true"] if menu else []
    m = re.search(r'class="tab-content has-bar-charts" data-data="([^"]*)"', t)
    charts, note = {}, None
    if m:
        d = json.loads(html.unescape(m.group(1))); note = re.sub(r"<[^>]+>", "", d.get("note") or "") or None
        for it in d.get("item", []):
            charts[it.get("item")] = it.get("data", {}).get("data", [])
    leis = sorted(set(re.findall(r">([0-9A-Z]{18}\d\d)</a>", t)))
    return {"title": title, "censored_tabs": censored, "charts": charts, "note": note, "leis": leis,
            "is_search_page": title.startswith("Suche nach")}

def fmt_rev(p, scope_txt):
    v = p["formattedValue"].replace("\u202f", " ")
    return f"{v} ({p['fy_label']}, {scope_txt}; {p['source']['publicationTitle']}, veröffentlicht {p['source']['publicationDate']}, lt. North Data)"

def apply(ev):
    comp = {a["slug"]: a for a in ev["accepted_revenue"]}
    cj = json.load(open(f"{R}/data/companies.json")); n = 0
    for x in cj:
        a = comp.get(x["slug"])
        if a and not x.get("revenue"):
            x["revenue"] = a["value"]; x.setdefault("sources", []).append(a["source_url"]); n += 1
    with open(f"{R}/data/companies.json", "w") as fh:
        fh.write(json.dumps(cj, ensure_ascii=False, indent=1) + "\n")
    rows = list(csv.DictReader(open(f"{R}/data/companies.csv", newline="")))
    for x in rows:
        a = comp.get(x["slug"])
        if a and not x["revenue"]: x["revenue"] = a["value"]
    with open(f"{R}/data/companies.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    img = {a["product_id"]: a["image_url"] for a in ev["photos_accepted"]}
    pj = json.load(open(f"{R}/data/products.json")); m = 0
    for x in pj:
        if x["product_id"] in img and not x.get("image_url"): x["image_url"] = img[x["product_id"]]; m += 1
    with open(f"{R}/data/products.json", "w") as fh:
        fh.write(json.dumps(pj, ensure_ascii=False, indent=1))
    rows = list(csv.DictReader(open(f"{R}/data/products.csv", newline="")))
    for x in rows:
        if x["product_id"] in img and not x["image_url"]: x["image_url"] = img[x["product_id"]]
    with open(f"{R}/data/products.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"companies revenue +{n}, product photos +{m}")

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--fetch" in a:
        tsv = a[a.index("--fetch") + 1]; out = a[a.index("--html-dir") + 1] if "--html-dir" in a else "/tmp/nd_T2307"
        os.makedirs(out, exist_ok=True)
        print(json.dumps(fetch([l.rstrip("\n").split("\t") for l in open(tsv) if l.strip()], out), indent=1))
    if "--apply" in a:
        apply(json.load(open(f"{R}/raw/companies_northdata_{RUN}.json")))
