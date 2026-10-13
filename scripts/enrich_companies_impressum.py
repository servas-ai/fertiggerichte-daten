"""Overlay verified legal-notice facts (Impressum) onto data/companies.json + companies.csv.
Evidence: raw/impressum_vies_*.json written from food-connectors `food company NAME --impressum DOMAIN`
(public legal notice, robots.txt respected) where every UID was checked live against EU VIES.
Accepted only when `accepted` is true in the evidence (VIES valid + VIES name matches the company,
or for DE ids – VIES returns no name – the company name is on the page; each accepted row was reviewed).
FN from the page is stored only when the page carries exactly one FN and the accepted UID is Austrian.
Never overrides a GLEIF value; adds uid*, imprint_url, register_court, and fn/website/country when empty."""
import csv, glob, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{R}/data"
FLAT = ["slug","name","role","legal_name","lei","fn","register_id","register_authority","legal_form_code","country","address","entity_status",
        "parent_direct","parent_ultimate","founded","owners","employees","revenue","website","product_count","median_price_eur",
        "median_eur_per_10g_protein","fetched_at"]
EXTRA = ["uid","uid_vies_name","uid_vies_address","uid_checked_at","imprint_url","register_court","hrb","registry_status"]

def apply(cs):
    ev = {}
    for p in sorted(glob.glob(f"{R}/raw/impressum_vies_*.json")):
        for e in json.load(open(p))["results"]:
            if e.get("accepted"): ev[e["company"]] = e
    n = 0
    for c in cs:
        e = ev.get(c["name"])
        if not e: continue
        n += 1
        if e.get("fn_only"):
            if not c.get("fn") and len(e.get("fn") or []) == 1: c["fn"] = e["fn"][0]
            c.update(imprint_url=e["imprint_url"], register_court=e.get("court"))
            if not c.get("website"): c["website"] = "https://" + e["domain"].split("/")[0]
            c.setdefault("sources", []); e["imprint_url"] in c["sources"] or c["sources"].append(e["imprint_url"])
            if not c.get("lei"): c["registry_status"] = "fn_from_imprint"
            continue
        b = e["best"]
        c.update(uid=b["uid"], uid_vies_name=b.get("vies_name"), uid_vies_address=(b.get("vies_address") or "").replace("\n", ", ") or None,
                 uid_checked_at=b.get("checked_at"), imprint_url=e["imprint_url"], register_court=e.get("court"),
                 hrb=(e["hrb"][0] if len(e.get("hrb") or []) == 1 and b["uid"][:2] == "DE" else None))
        if e.get("legal_name_imprint") and not c.get("lei"): c["legal_name"] = e["legal_name_imprint"]
        if not c.get("fn") and len(e.get("fn") or []) == 1 and b["uid"].startswith("ATU"): c["fn"] = e["fn"][0]
        if not c.get("country"): c["country"] = b["uid"][:2]
        if not c.get("website"): c["website"] = "https://" + e["domain"].split("/")[0]
        if not c.get("address") and c.get("uid_vies_address"): c["address"] = c["uid_vies_address"]
        if not c.get("legal_name") and b.get("vies_name"): c["legal_name"] = b["vies_name"]
        src = e["imprint_url"]; c.setdefault("sources", [])
        for s in (src, "EU VIES " + b["uid"]):
            if s not in c["sources"]: c["sources"].append(s)
        c["registry_status"] = "verified_gleif+vies" if c.get("lei") else "verified_vies_imprint"
    return n

def write(cs):
    json.dump(cs, open(f"{D}/companies.json", "w"), ensure_ascii=False, indent=1)
    with open(f"{D}/companies.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, FLAT + ["brands","chains","plants_count"] + EXTRA); w.writeheader()
        for r in cs: w.writerow({**{k: r.get(k) for k in FLAT + EXTRA}, "brands": "|".join(r["brands"]), "chains": "|".join(r["chains"]), "plants_count": len(r.get("plants") or [])})

if __name__ == "__main__":
    cs = json.load(open(f"{D}/companies.json")); n = apply(cs); write(cs)
    print(n, "companies from legal notices;", sum(1 for c in cs if c.get("uid")), "with VIES-verified UID;", sum(1 for c in cs if c.get("uid") or c.get("lei")), "/", len(cs), "with LEI or UID;",
          sum(1 for c in cs if c.get("fn")), "with FN")
