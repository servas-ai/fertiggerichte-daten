"""T1835: registered address for DE rows that have a VIES-valid UID but no address (DE VIES returns no address).
Source = the company's own legal notice (imprint_url already in the row). Prints candidate lines for review."""
import sys, json, re, time, urllib.parse
sys.path.insert(0, "/workspace/food-connectors")
import importlib; I = importlib.import_module("food_connectors.company.impressum")
rows = json.load(open("/workspace/fertiggerichte-daten/data/companies.json"))
out = {}
for r in rows:
    if (r.get("address") or "").strip() or not r.get("imprint_url"): continue
    u = r["imprint_url"]; p = urllib.parse.urlparse(u); base = f"{p.scheme}://{p.netloc}"
    if not I._robots_ok(base, u): out[r["slug"]] = {"error": "robots"}; continue
    h = I._fetch(u); time.sleep(1)
    if not h: out[r["slug"]] = {"url": u, "error": "fetch failed"}; print(r["slug"], "FETCH FAIL"); continue
    t = I._text(h); lines = [l.strip() for l in t.split("\n") if l.strip()]
    cands = []
    for i, l in enumerate(lines):
        if re.search(r"(?:^|\b)(?:D-)?\d{5}\s+[A-ZÄÖÜ]", l):
            cands.append(" | ".join(lines[max(0, i-3):i+1]))
    out[r["slug"]] = {"url": u, "legal_name": r.get("legal_name"), "cands": cands[:6]}
    print("==", r["slug"], r.get("legal_name"), u); [print("   ", c[:220]) for c in cands[:6]]
json.dump(out, open("/workspace/fertiggerichte-daten/scripts/web_T1835/addr_out.json", "w"), ensure_ascii=False, indent=1)
