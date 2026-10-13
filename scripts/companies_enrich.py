"""Resolve every producer / brand owner / retailer to a legal entity via GLEIF (+parents), merge
already-researched facts (producer_profiles.json) and plants (companies.json, Statistik Austria approval list).
Writes data/companies.json + data/companies.csv. Only verified registry hits are stored (match_score>=0.5)."""
import json, re, sys, os, csv, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from food_company import registries as R
SRC = os.environ.get("FERTIG_SRC", "/workspace/fertig")
APP = os.environ.get("FERTIG_APP", "/workspace/fertig-app/public/data.json")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# herst string (normalized prefix) -> legal-name query used in registries
ALIAS = {"billa": "BILLA AG", "unilever austria": "Unilever Austria GmbH", "iglo austria": "iglo Austria GmbH",
 "iglo gmbh": "iglo GmbH", "fit2go": "Fit2go GmbH", "nestle oesterreich": "Nestlé Österreich GmbH",
 "mars austria": "Mars Austria OG", "radatz": "Radatz - Feine Wiener Fleischwaren GmbH",
 "ja natuerlich": "Ja! Natürlich Naturprodukte Gesellschaft m.b.H.", "efko": "efko Frischfrucht und Delikatessen GmbH",
 "amlacher nudeln": "Amlacher Nudeln", "josef recheis": "Recheis Teigwaren GmbH", "hamkervertriebsgesellschaftmbh": "Hamker Vertriebsgesellschaft mbH",
 "lab alimentare cecchin": "Laboratorio Alimentare Cecchin Andrea e Carlo srl", "dr schaer": "Dr. Schär AG"}
RETAIL = [("billa","BILLA AG","AT"),("spar","SPAR Österreichische Warenhandels-Aktiengesellschaft","AT"),("hofer","HOFER KG","AT"),
 ("lidl","Lidl Österreich GmbH","AT"),("penny","PENNY GmbH","AT"),("dm","dm drogerie markt GmbH","AT"),
 ("rewe-international","REWE International AG","AT"),("unimarkt","Unimarkt GmbH","AT"),("mpreis","MPREIS Warenvertriebs GmbH","AT")]
BRAND_OWNERS = [("knorr","Unilever Austria GmbH","AT"),("maggi","Nestlé Österreich GmbH","AT"),("felix","FELIX Austria GmbH","AT"),
 ("iglo","iglo Austria GmbH","AT"),("planted","Planted Foods AG","CH"),("rana","Pastificio Rana S.p.A.","IT"),
 ("frosta","FRoSTA Tiefkühlkost GmbH","DE"),("inzersdorfer","Inzersdorfer Nahrungsmittelwerke","AT"),("maresi","Maresi Austria GmbH","AT")]

def norm(s):
    s = s.split(",")[0].split("\n")[0]
    s = re.sub(r"\(.*?\)", "", s).strip()
    return s
def key(s):
    k = s.lower().replace("ö","oe").replace("ü","ue").replace("ä","ae").replace("!","").replace(".","")
    return re.sub(r"\s+"," ",k).strip()
def slug(s): return re.sub(r"[^a-z0-9]+","-",key(s)).strip("-")[:60]

def main():
    rows = json.load(open(APP))["rows"]
    groups = collections.defaultdict(list)
    for r in rows:
        h = (r.get("herst") or "").strip()
        if not h: continue
        n = norm(h); k = key(n)
        q = next((v for a, v in ALIAS.items() if k.startswith(a)), n)
        groups[q].append(r)
    profiles = {p["name"]: p for p in json.load(open(f"{SRC}/analysis/producer_profiles.json"))}
    comps = {c["name"]: c for c in json.load(open(f"{SRC}/analysis/companies.json"))}
    ents = {}
    for q, rs in groups.items(): ents[q] = {"role": "producer", "country_hint": None, "rows": rs}
    for s, q, cc in RETAIL: ents.setdefault(q, {"role": "retailer", "rows": []}).update(role=ents.get(q,{}).get("role","retailer") if q in groups else "retailer", country_hint=cc, chain=s)
    for s, q, cc in BRAND_OWNERS: e = ents.setdefault(q, {"role": "brand_owner", "rows": []}); e["country_hint"] = cc; e.setdefault("brands", []).append(s)
    for n in comps:
        if comps[n]["type"] == "producer": ents.setdefault(n, {"role": "producer", "rows": []})
    out = []
    for q, e in ents.items():
        print("·", q, file=sys.stderr)
        try: res = R.company(q, e.get("country_hint"))
        except Exception as ex: res = {"gleif": None, "error": str(ex)}
        g = res.get("gleif") or {}
        par = res.get("parents") or {}
        p = profiles.get(q) or next((v for k, v in profiles.items() if R.match_score(q, k) >= .6), None)
        c = comps.get(q) or next((v for k, v in comps.items() if R.match_score(q, k) >= .6), None)
        rs = e["rows"]; prices = [r["price"] for r in rs if r.get("price")]
        pli = [r["ppe"] for r in rs if r.get("ppe")]
        f = (p or {}).get("facts") or {}
        rec = {
          "slug": slug(g.get("legal_name") or q), "name": q, "role": e["role"],
          "legal_name": g.get("legal_name"), "lei": g.get("lei"),
          "register_id": g.get("register_id"), "register_authority": g.get("register_ra"),
          "fn": ("FN " + g["register_id"].replace("FN","").strip()) if g.get("register_ra") == "RA000017" and g.get("register_id") else None,
          "legal_form_code": g.get("legal_form"), "country": g.get("country") or e.get("country_hint"),
          "address": g.get("address"), "entity_status": g.get("status"),
          "parent_direct": (par.get("direct_parent") or {}).get("legal_name"), "parent_ultimate": (par.get("ultimate_parent") or {}).get("legal_name"),
          "parent_ultimate_lei": (par.get("ultimate_parent") or {}).get("lei"),
          "founded": f.get("gruendung"), "owners": f.get("eigentuemer"), "management": f.get("geschaeftsfuehrung"),
          "employees": f.get("mitarbeiter"), "revenue": f.get("umsatz"),
          "website": f.get("website") or (c or {}).get("website"),
          "plants": [{"address": x["address"], "approval_code": x.get("approval_code"), "lat": x.get("lat"), "lon": x.get("lon"), "source": x.get("source")} for x in (c or {}).get("plant_addresses", [])],
          "approval_codes": f.get("identitaetskennzeichen"), "brands": sorted({r.get("brand") for r in rs if r.get("brand")} | set(e.get("brands", []))),
          "chains": sorted({r["store"] for r in rs}), "product_count": len(rs),
          "median_price_eur": round(statistics.median(prices), 2) if prices else None,
          "median_eur_per_10g_protein": round(statistics.median(pli), 3) if pli else None,
          "nace": None,
          "sources": [s for s in [g.get("source")] + ((p or {}).get("sources") or []) if s],
          "gleif_match_score": g.get("match_score"), "fetched_at": R.now(),
        }
        out.append(rec)
    seen = {}
    for r in out:
        k = (r["legal_name"] or r["name"]).lower()
        if k in seen:
            o = seen[k]; o["product_count"] += r["product_count"]; o["brands"] = sorted(set(o["brands"]) | set(r["brands"])); o["chains"] = sorted(set(o["chains"]) | set(r["chains"]))
            if r["role"] != o["role"]: o["role"] = o["role"] + "+" + r["role"]
        else: seen[k] = r
    out = list(seen.values())
    store_rows = collections.Counter(r["store"] for r in rows)
    for r in out:
        ch = next((c for s_, q, c_ in RETAIL if q == r["name"] for c in [s_]), None)
        if ch: r["chain_product_count"] = sum(v for k, v in store_rows.items() if k.lower() == ch)
        r["registry_status"] = "verified_gleif" if r["lei"] else "not_found_in_gleif"
    out.sort(key=lambda r: (-r["product_count"], r["name"]))
    used = set()
    for r in out:
        b, n = r["slug"], 2
        while r["slug"] in used: r["slug"] = f"{b}-{n}"; n += 1
        used.add(r["slug"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(f"{OUT}/companies.json", "w"), ensure_ascii=False, indent=1)
    flat = ["slug","name","role","legal_name","lei","fn","register_id","register_authority","legal_form_code","country","address","entity_status","parent_direct","parent_ultimate","founded","owners","employees","revenue","website","product_count","median_price_eur","median_eur_per_10g_protein","fetched_at"]
    with open(f"{OUT}/companies.csv","w",newline="") as fh:
        w = csv.DictWriter(fh, flat + ["brands","chains","plants_count"]); w.writeheader()
        for r in out: w.writerow({**{k: r[k] for k in flat}, "brands": "|".join(r["brands"]), "chains": "|".join(r["chains"]), "plants_count": len(r["plants"])})
    print(len(out), "companies;", sum(1 for r in out if r["lei"]), "with LEI")
if __name__ == "__main__": main()
