"""Overlay manually verified GLEIF LEI matches onto data/companies.json + companies.csv.
Evidence: raw/gleif_verified_*.json (GLEIF API v1, public, no key). A record is listed under `accepted` only after
review against the product label (exact legal name and/or label address = GLEIF legal address); rejected
candidates and their reasons stay in the same file. Never overrides an existing LEI.
Runs inside companies_enrich.py (so 24h GLEIF reruns keep these) and standalone."""
import glob, json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{R}/data"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def apply(cs):
    ev = {}
    for p in sorted(glob.glob(f"{R}/raw/gleif_verified_*.json")):
        for e in json.load(open(p))["accepted"]: ev[e["company"]] = e
    n = 0
    for c in cs:
        e = ev.get(c["name"])
        if not e or c.get("lei"): continue
        n += 1
        c.update(lei=e["lei"], legal_name=e["legal_name"], register_id=e.get("register_id"), register_authority=e.get("register_ra"),
                 legal_form_code=e.get("legal_form"), country=e.get("country") or c.get("country"), address=e.get("address"),
                 entity_status=e.get("status"), parent_direct=e.get("parent_direct"), parent_ultimate=e.get("parent_ultimate"),
                 parent_ultimate_lei=e.get("parent_ultimate_lei"), gleif_match_basis=e.get("match_basis"))
        if e.get("register_ra") == "RA000017" and e.get("register_id") and not c.get("fn"): c["fn"] = "FN " + e["register_id"].replace("FN", "").strip()
        c.setdefault("sources", []); e["source"] in c["sources"] or c["sources"].append(e["source"])
        c["registry_status"] = "verified_gleif+vies" if c.get("uid") else "verified_gleif"
    return n

if __name__ == "__main__":
    import enrich_companies_impressum as IMP
    cs = json.load(open(f"{D}/companies.json")); n = apply(cs); IMP.write(cs)
    print(n, "verified GLEIF overlays;", sum(1 for c in cs if c.get("lei")), "/", len(cs), "with LEI;",
          sum(1 for c in cs if c.get("lei") or c.get("uid")), "with LEI or UID;", sum(1 for c in cs if c.get("parent_ultimate")), "with ultimate parent")
