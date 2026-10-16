"""T1835 verification pass: re-fetch each candidate legal notice once, record which of OUR verified identifiers appear,
whether the legal name / registered street+postcode appear, and VIES-check printed VAT ids for rows without UID."""
import sys, json, re, time, importlib, urllib.parse
sys.path.insert(0, "/workspace/food-connectors")
I = importlib.import_module("food_connectors.company.impressum")
R = importlib.import_module("food_connectors.company.registries")
A = {"maresi-austria-gmbh": "https://maresi.at/de/impressum", "alnatura-gmbh": "https://alnatura.de/impressum",
 "alnatura-produktions-und-handels-gmbh": "https://alnatura.de/impressum", "weinbergmaier-gmbh": "https://weinbergmaier.at/impressum",
 "mpreis-warenvertriebs-gmbh": "https://mpreis.at/sp/impressum", "noem-ag": "https://www.noem.at/impressum",
 "bertagni-1882-spa": "https://bertagni1882.it/", "dr-oetker-gmbh": "https://www.oetker.at/impressum",
 "ehrmann-gmbh": "https://www.ehrmann.de/impressum", "adriatic-group-gmbh": "https://adriaticgroup.at/de/impressum",
 "biovegan-gmbh": "https://biovegan.de/pages/impressum", "dr-schaer-spa": "https://schaer.com/imprint",
 "glatz-gmbh": "https://glatz.at/impressum-gruppe", "tress-lebensmittel-gmbh-co-kg": "https://tressbrueder.de/impressum",
 "andros-deutschland-gmbh": "https://andros.de/impressum/", "euryza-gmbh": "https://www.reis-fit.de/impressum/",
 "greenforce-future-food-ag": "https://greenforce.com/policies/legal-notice", "ruegenwalder-muehle-carl-mueller-gmbh-co-kg": "https://www.ruegenwalder.de/de/impressum",
 "efko-frischfrucht-und-delikatessen-gmbh": "https://www.efko.at/impressum/", "followfood-gmbh": "https://followfood.de/impressum",
 "rewe-international-ag": "https://rewe-group.at/de/impressum/", "spar-oesterreichische-warenhandels-aktiengesellschaft": "https://spar.at/impressum.html"}
rows = {r["slug"]: r for r in json.load(open("/workspace/fertiggerichte-daten/data/companies.json"))}
def squash(s): return re.sub(r"[\s.\-/]", "", s or "").lower()
out = {}
for slug, url in A.items():
    r = rows[slug]; p = urllib.parse.urlparse(url); base = f"{p.scheme}://{p.netloc}"
    rec = {"imprint_url": url, "website": base, "robots_ok": I._robots_ok(base, url)}
    h = I._fetch(url) if rec["robots_ok"] else None
    if not h: rec["error"] = "fetch failed"; out[slug] = rec; print(slug, "FAIL"); continue
    t = I._text(h); tq = squash(t)
    ids = {}
    for k in ("uid", "lei", "fn", "hrb", "register_id"):
        v = (r.get(k) or "").replace("FN ", "")
        if v and len(squash(v)) >= 4 and squash(v) in tq: ids[k] = r.get(k)
    rec["id_hits"] = ids
    rec["name_on_page"] = I._name_on_page(r.get("legal_name") or r["name"], t)
    addr = r.get("address") or ""; m = re.search(r"\b(\d{4,5})\b", addr); street = addr.split(",")[0]
    rec["postcode_on_page"] = bool(m and m.group(1) in t); rec["street_on_page"] = bool(street and squash(street)[:10] in tq)
    vats = []
    for v in I.VAT_RX.findall(t):
        v = re.sub(r"[\s.]", "", v)
        if v not in vats: vats.append(v)
    rec["vats_on_page"] = vats
    if not r.get("uid"):
        rec["vies"] = []
        for v in vats[:3]:
            try:
                d = R.vies_check(v); vn = d.get("name") if d.get("name") not in ("---", "", None) else None
                rec["vies"].append({"uid": v, "valid": bool(d.get("valid")), "vies_name": vn,
                    "vies_address": d.get("address") if d.get("address") not in ("---", "") else None, "checked_at": d.get("requestDate"),
                    "name_match": round(R.match_score(r.get("legal_name") or r["name"], vn), 2) if vn else None})
            except Exception as e: rec["vies"].append({"uid": v, "error": str(e)[:100]})
    out[slug] = rec
    print(slug, ids, rec["name_on_page"], rec["postcode_on_page"], rec["street_on_page"], [(x["uid"], x.get("valid"), x.get("vies_name"), x.get("name_match")) for x in rec.get("vies", [])], flush=True)
json.dump(out, open("/workspace/fertiggerichte-daten/scripts/web_T1835/verify_out.json", "w"), ensure_ascii=False, indent=1)
