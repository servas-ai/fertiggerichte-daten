"""CI-free validation. Uses `frictionless validate datapackage.json` if installed, plus own plausibility rules. Exit 1 on error."""
import re, csv, json, os, sys, shutil, subprocess
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); err = []; warn = []
pkg = json.load(open(f"{R}/datapackage.json"))
tab = {r["name"]: list(csv.DictReader(open(f"{R}/{r['path']}"))) for r in pkg["resources"]}
for r in pkg["resources"]:
    rows = tab[r["name"]]; s = r["schema"]
    if [f["name"] for f in s["fields"]] != list(rows[0]): err.append(f"{r['name']}: header != schema")
    pk = s.get("primaryKey")
    if pk:
        ks = [x[pk] for x in rows]
        if len(ks) != len(set(ks)): err.append(f"{r['name']}: duplicate {pk}")
ids = {x["product_id"] for x in tab["products"]}
for n in ("prices", "nutrition"):
    bad = [x for x in tab[n] if x["product_id"] not in ids]
    if bad: err.append(f"{n}: {len(bad)} orphan product_id")
for x in tab["prices"]:
    if not (0.1 <= float(x["price_eur"]) <= 200): err.append(f"price out of range {x['product_id']} {x['price_eur']}")
    if not x["price_source"]: warn.append(x["product_id"])
for x in tab["nutrition"]:
    for k, hi in (("kcal_100g", 900), ("protein_100g", 100), ("salt_100g", 30)):
        if x[k] and not (0 <= float(x[k]) <= hi): err.append(f"nutrition {k} implausible {x['product_id']}={x[k]}")
for x in tab.get("companies", []):
    if x["lei"] and len(x["lei"]) != 20: err.append(f"bad LEI {x['slug']}")
    if x.get("uid") and not re.fullmatch(r"(ATU\d{8}|DE\d{9}|IT\d{11}|[A-Z]{2}[0-9A-Z]{8,12})", x["uid"]): err.append(f"bad UID {x['slug']}")
    if x.get("fn") and not re.fullmatch(r"FN \d{1,6}[a-z]", x["fn"]): err.append(f"bad FN {x['slug']} {x['fn']}")
if shutil.which("frictionless"):
    p = subprocess.run(["frictionless", "validate", f"{R}/datapackage.json"], capture_output=True, text=True)
    if p.returncode: err.append("frictionless: " + p.stdout[-800:])
print(f"warnings: {len(warn)} prices without source");print("\n".join(err[:50]) or "OK", f"({len(err)} errors)"); sys.exit(1 if err else 0)
