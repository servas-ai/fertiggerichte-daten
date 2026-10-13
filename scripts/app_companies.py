"""Derive the app's companies.json (logos + numeric revenue/employees/founding parsed from sourced text)."""
import json, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("FERTIG_SRC", "/workspace/fertig"); APPDIR = os.environ.get("FERTIG_APP", "/workspace/fertig-app/public")
sys.path.insert(0, R)
from food_company.registries import match_score
cs = json.load(open(f"{R}/data/companies.json"))
logos = json.load(open(f"{SRC}/analysis/logos.json")); comp = json.load(open(f"{SRC}/analysis/companies.json"))
def num(s):
    return float(s.replace(".", "").replace(",", "."))
for c in cs:
    lg = None
    for x in comp:
        if match_score(x["name"], c["name"]) >= .6 and x.get("logo_path"): lg = "analysis/logos/" + os.path.basename(x["logo_path"])
    if not lg:
        for k, v in logos.items():
            if v.get("file") and (match_score(v.get("name"), c["name"]) >= .5 or any(b.lower() == k for b in c["brands"]) or (c.get("legal_name") or c["name"]).lower().startswith(k.replace("-", " "))):
                lg = "analysis/" + v["file"] if not v["file"].startswith("analysis") else v["file"]; break
    c["logo"] = lg
    if c["name"] in ("BILLA AG",) and "retailer" not in c["role"]: c["role"] = "retailer+producer"
    for k in ("revenue", "employees", "founded"):
        if (c.get(k) or "").lower().startswith(("nicht", "unbekannt", "in dieser")): c[k] = None
    rv = c.get("revenue") or ""
    m = re.search(r"(\d[\d.,]*)\s*(Mio|Mrd|Milliard|Million)", rv)
    c["revenue_eur_m"] = (num(m.group(1)) * (1000 if m.group(2).startswith(("Mrd", "Milliard")) else 1)) if m else None
    y = re.search(r"(20\d\d)", rv); c["revenue_year"] = y.group(1) if y else None
    e = re.search(r"(\d[\d.]*)", c.get("employees") or ""); c["employees_n"] = int(e.group(1).replace(".", "")) if e else None
    f = re.search(r"(1[89]\d\d|20\d\d)", c.get("founded") or ""); c["founded_year"] = int(f.group(1)) if f else None
json.dump(cs, open(f"{APPDIR}/companies.json", "w"), ensure_ascii=False)
print(len(cs), "->", APPDIR + "/companies.json", sum(1 for c in cs if c["logo"]), "logos")
