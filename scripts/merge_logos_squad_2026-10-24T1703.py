"""Daten-Squad 2026-10-24T1703 logo merge (daten-only; files staged in scripts/logo_work_T1703 for the Orchestrator merge):
+3 vision-gated producer logos for the Bauernladen.at producers added T0439/T0506: FAIRKOCHT, Christöphl Manufaktur, Genusss-Manufaktur Bruckner."""
import csv, json, hashlib, os, datetime, collections
D = "/workspace/fertiggerichte-daten"
W = os.path.join(D, "scripts/logo_work_T1703")
NEW = [
 ({"slug": "fairkocht", "name": "FAIRKOCHT", "category": "Markenhersteller", "file": "logos/fairkocht.png",
   "source_url": "https://www.fairkocht.at/wp-content/uploads/2023/10/fairkocht_logo_quer.png (fairkocht.at header logo 586x131 RGBA, robots Disallow only /wp-admin/; unmodified; vision gate PASS)",
   "brands": ["FAIRKOCHT", "Fairkocht", "fairkocht gmbh", "FAIRKOCHT (fairkocht gmbh)"]},
  "PASS — round black jar emblem + script 'Geschichten im Glas' + 'HEIMISCHES FAIRKOCHT' wordmark, same mark as on the jar labels"),
 ({"slug": "christoephl", "name": "Christöphl Manufaktur", "category": "Markenhersteller", "file": "logos/christoephl.png",
   "source_url": "https://christoephl.at/cdn/shop/t/5/assets/christoephl-logo.svg (christoephl.at Shopify header logo SVG, /cdn/shop not disallowed in robots.txt; rendered 800 px, unmodified; vision gate PASS)",
   "brands": ["Christöphl", "Christöphl Manufaktur", "Christöphl Manufaktur GmbH"]},
  "PASS — black script wordmark 'Christöphl', the site header logo"),
 ({"slug": "genusss-manufaktur", "name": "Genusss-Manufaktur Bruckner", "category": "Markenhersteller", "file": "logos/genusss-manufaktur.png",
   "source_url": "https://nudelmanufaktur.at/images/branding-footer.png (nudelmanufaktur.at footer branding 130x75 RGBA, low resolution; no robots.txt (404 = allow); unmodified; vision gate PASS)",
   "brands": ["GENUSSS-MANUFAKTUR BRUCKNER KG", "Genusss-Manufaktur", "Nudelmanufaktur Bruckner", "Genusss-Manufaktur Bruckner KG (Nudelmanufaktur Yppenplatz)", "\"GENUSSS-MANUFAKTUR\" Bruckner KG"]},
  "PASS (low-res 130x75) — red-white-red flag carried by a running figure followed by cow, pig, hen and rabbit silhouettes + 'www.genusss-manufaktur.at'; header variant branding.png rejected because its figure is greyed out"),
]
rows = json.load(open(f"{D}/data/logos.json"))
known = {b.lower() for r in rows for b in (r.get("brands") or [])}
slugs = {r["slug"] for r in rows}
bc = collections.Counter(r["brand"].strip() for r in csv.DictReader(open(f"{D}/data/online_mealprep.csv")))
bc.update(r["brand"].strip() for r in csv.DictReader(open(f"{D}/data/products.csv")))
added = []
for row, vis in NEW:
    assert row["slug"] not in slugs, row["slug"]
    assert not any(b.lower() in known for b in row["brands"]), ("alias collision", row["slug"])
    rows.append(row)
    p = os.path.join(W, os.path.basename(row["file"]))
    added.append({**row, "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
                  "products_impacted": sum(bc.get(b, 0) for b in row["brands"]), "vision": vis})
json.dump(rows, open(f"{D}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{D}/data/logos.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, ["slug", "name", "category", "file", "source_url", "brands"]); w.writeheader()
    for r in rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
ev = {"run": "2026-10-24T1703 Daten-Squad", "generated_at": datetime.datetime.now(datetime.UTC).isoformat(), "added": added,
      "rejected": {
        "Hackls Happy Turkey / Marillenhof Hackl": "www.hackls-marille.at answers every request (incl. robots.txt) with a hoster ModSecurity 'Access denied by security policy' page -> not bypassed",
        "Venatio": "venatio.at and www.venatio.at gave no HTTP response within 30 s (http and https) -> retry later",
        "vom Sandriegel": "no legal identity / website published (T0506)"},
      "staging": "files only in scripts/logo_work_T1703 until the Orchestrator merges them into fertig/analysis/logos"}
json.dump(ev, open(f"{D}/raw/logos_squad_2026-10-24T1703.json", "w"), ensure_ascii=False, indent=1)
print("ok", len(rows), [(a["slug"], a["products_impacted"]) for a in added])
