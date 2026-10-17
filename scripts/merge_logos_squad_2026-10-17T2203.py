"""Daten-Squad 2026-10-17T2203 logo merge (daten-only while the fertig uid freeze is on):
+1 vision-gated brand logo Vifon (vifon.pl official footer SVG). File staged in scripts/logo_work_T2203;
copy to fertig/analysis/logos waits for the Orchestrator to lift the uid freeze."""
import csv, json, hashlib, os, datetime, collections
D = "/workspace/fertiggerichte-daten"
W = os.path.join(D, "scripts/logo_work_T2203")
SRC = "https://vifon.pl/wp-content/themes/vifon2025b/img/logo/logo-vifon-footer-pl.svg"
row = {"slug": "vifon", "name": "Vifon", "category": "Markenhersteller", "file": "logos/vifon.png",
       "source_url": SRC + " (vifon.pl footer logo; robots Disallow only /wp-admin/; white wordmark+slogan recoloured #1f1f1f for light backgrounds, emblem unchanged; vision gate PASS)",
       "brands": ["Vifon", "VIFON", "Vifon S.A."]}
rows = json.load(open(f"{D}/data/logos.json"))
assert not any(r["slug"] == "vifon" for r in rows)
known = {b.lower() for r in rows for b in (r.get("brands") or [])}
assert not any(b.lower() in known for b in row["brands"]), "alias collision"
rows.append(row)
json.dump(rows, open(f"{D}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{D}/data/logos.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, ["slug", "name", "category", "file", "source_url", "brands"]); w.writeheader()
    for r in rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
bc = collections.Counter(r["brand"].strip() for r in csv.DictReader(open(f"{D}/data/products.csv")))
sha = hashlib.sha256(open(f"{W}/vifon.png", "rb").read()).hexdigest()
ev = {"run": "2026-10-17T2203 Daten-Squad", "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
      "added": [{**row, "sha256": sha, "size_px": "800x215 RGBA", "products_impacted": sum(bc.get(b, 0) for b in row["brands"]),
                 "entity_check": "MPreis rows EAN 5901882944596/5901882944565 (GS1 590 = Poland); Vifon is the Polish instant-noodle brand (vifon.pl, Kraków)",
                 "vision": "PASS — red circular emblem with white tureen and gold ring + VIFON wordmark + 'To Dzisiaj Od 1963', legible on white after recolouring only the wordmark/slogan"}],
      "rejected": {
          "Pierre Baguette": "pierrebaguette.com (robots allow) only ships an animated loader chef figure SVG cropped to viewBox 20 0 50 80, no standalone logo asset → not taken",
          "Pasta Box": "pastabox.cz is a parked Gransy domain; robots.txt HTTP 500 → treated as disallow-all",
          "The Green Garden": "thegreengarden.cz unreachable (no HTTP response)",
          "SPAR Asia": "spar.at/eigenmarken* HTTP 403 (Cloudflare) → not bypassed",
          "Wiener Virtshaus": "BS Gastro has no website (known dead end)"},
      "staging": "file only in scripts/logo_work_T2203 until the fertig uid freeze lifts (same as T2102 adamah)"}
json.dump(ev, open(f"{D}/raw/logos_squad_2026-10-17T2203.json", "w"), ensure_ascii=False, indent=1)
print("ok", len(rows), ev["added"][0]["products_impacted"])
