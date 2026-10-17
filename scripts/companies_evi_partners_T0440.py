"""Daten-Squad T0440 (2026-10-17): owners for partnerships + 2 FN from legal notices.

T1907 parsed only the evi.gv.at 'Gesellschafter/in' section (GmbH), so KG/OG partners
('Unbeschränkt haftende/r Gesellschafter/in', 'Kommanditist/in') were missed. Re-fetched evi.gv.at /f/<FN>
(official Firmenbuch publication platform, robots allows /f/, food-connectors polite gate, 1 req/s).
FN for Recheis and Wech taken from the company's own legal notice and confirmed on evi.gv.at (name = row legal name).
Natural persons are counted, not named (T1907 rule). Eintragungsdatum 1991-1995 = FBG-1991 bulk transfer → not a founding date.
Evidence: raw/companies_evi_2026-10-17T0440.json; probe scripts in scripts/evi_T0440/.
"""
import csv, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(f"{R}/scripts/evi_T0440/evi2_out.json")); I = json.load(open(f"{R}/scripts/evi_T0440/imp_out.json"))
LEGAL = ("GmbH", "m.b.H", "AG", "Privatstiftung", "KG", "OG", "eGen", "B.V.", "S.A.")
def owners(e):
    ents, nat, roles = [], 0, []
    for sec, v in e["sections"].items():
        if "Gesellschafter" not in sec and "Kommanditist" not in sec: continue
        n = 0
        for it in v["items"]:
            if (it["href"] or "").startswith("/f/") or any(x in it["name"] for x in LEGAL):
                ents.append(it["name"] + (f" (FN {it['href'].rsplit('/',1)[1]})" if it["href"] else ""))
            else: nat += 1; n += 1
        roles.append((sec, len(v["items"])))
    parts = ents + ([f"{nat} natürliche Person{'en' if nat > 1 else ''}"] if nat else [])
    kind = "; ".join(f"{c}× {s}" for s, c in roles)
    return "; ".join(parts) + f" (Gesellschafter lt. Firmenbuch/evi.gv.at: {kind})"
FN = {"recheis-teigwaren-gmbh": ("FN 47864p", "Landesgericht Innsbruck"), "wech-gefluegel-gmbh": ("FN 118996w", "Landesgericht Klagenfurt")}
U, prev = {}, {}
cj = json.load(open(f"{R}/data/companies.json"))
for c in cj:
    s = c["slug"]
    if s not in E: continue
    e = E[s]; u = {}
    assert e["status"] == "Eingetragen"
    if s in FN:
        assert e["name"] == c["legal_name"], (e["name"], c["legal_name"])
        u["fn"], u["register_court"] = FN[s]
    u["owners"] = owners(e); u["owners_source"] = e["url"]
    if e.get("stammkapital"): u["share_capital"] = e["stammkapital"]
    u["register_status"] = e["status"]
    prev[s] = {k: c.get(k) for k in u}
    c.update(u); c.setdefault("sources", [])
    for src in (e["url"], I.get(s, {}).get("url")):
        if src and src not in c["sources"]: c["sources"].append(src)
    U[s] = u
with open(f"{R}/data/companies.json", "w") as fh: fh.write(json.dumps(cj, ensure_ascii=False, indent=1) + "\n")
rows = list(csv.DictReader(open(f"{R}/data/companies.csv", newline="")))
for r in rows:
    for k, v in U.get(r["slug"], {}).items():
        if k in r: r[k] = v
with open(f"{R}/data/companies.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump({"run": "2026-10-17T0440", "method": __doc__, "updates": U, "previous": prev, "evi": E,
           "imprint_probe": I, "not_taken": {
             "recheis/wech Eintragungsdatum": "1993-09-08 / 1994-09-23 = FBG-1991 bulk transfer window, not a founding date (rows keep company statements 1889 / 1958)",
             "deflorian-srl": "legal notice prints 'Firmenbuchnummer: AT70258EG' — not an Austrian FN format, not taken",
             "dm, morgentau, amlacher, bs-gastro, hartls": "no FN printed on the fetched legal notice (dm imprint is JS-rendered); Hartl is a sole trader",
             "caro-fratello-gmbh": "imprint URL 404"}},
          open(f"{R}/raw/companies_evi_2026-10-17T0440.json", "w"), ensure_ascii=False, indent=1)
r2 = list(csv.DictReader(open(f"{R}/data/companies.csv")))
print("updated", list(U), "| fn", sum(1 for x in r2 if x["fn"].strip()), "owners", sum(1 for x in r2 if x["owners"].strip()), "/", len(r2))
for s, u in U.items(): print(s, u["owners"])
