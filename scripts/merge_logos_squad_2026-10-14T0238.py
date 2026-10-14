"""Daten-Squad 2026-10-14T0238: bofrost* wordmark for the new online provider bofrost* Austria.
Source: official https://www.bofrost.at/_ui/responsive/theme-main/css/images/bofrost_logo.svg (the logo URL in bofrost.at's own
schema.org Organization JSON-LD; robots allows it). Paths unchanged; the single fill #ffffff (white-on-header) recoloured to
#1f1f1f for the light UI (same practice as Englert T15). Vision gate via Read of an 800 px render on white: 'bofrost*' wordmark, sharp."""
import json, os, csv, hashlib, shutil, datetime
D = "/workspace/fertiggerichte-daten"; P = "/workspace/fertig/analysis/logos.json"; LOGOS = "/workspace/fertig/analysis/logos"
src = f"{D}/scripts/logo_work_T0238/bofrost.svg"
d = json.load(open(P))
sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
if not (d.get("bofrost") or {}).get("file"):
    dest = f"{LOGOS}/bofrost.svg"; assert not os.path.exists(dest); shutil.copy(src, dest)
    d["bofrost"] = dict(slug="bofrost", name="bofrost*", brands=["bofrost*", "bofrost", "Bofrost", "bofrost* Austria GmbH"], logo_category="Online-Mealprep", file="logos/bofrost.svg",
        source="https://www.bofrost.at/_ui/responsive/theme-main/css/images/bofrost_logo.svg", size="svg", hq=True,
        note="Vision gate 2026-10-14T0238 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar) · offizielles bofrost.at Logo-SVG (aus dem Organization-JSON-LD der Website), Pfade unverändert, Füllfarbe weiß → #1f1f1f für helle UI")
    tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)
rows = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"), "source_url": v.get("source"), "brands": v.get("brands")} for k, v in d.items()]
json.dump(rows, open(f"{D}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{D}/data/logos.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, ["slug", "name", "category", "file", "source_url", "brands"]); w.writeheader()
    for r in rows: w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
json.dump({"run": "2026-10-14T0238 Daten-Squad", "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
           "added": [{"slug": "bofrost", "source": d["bofrost"]["source"], "sha256": sha, "note": d["bofrost"]["note"]}],
           "vision_gate": {"bofrost": "PASS — dark bofrost* wordmark on white (800 px render)"},
           "counts": {"total_rows": len(d), "with_file": sum(1 for v in d.values() if (v.get("file") or "").strip())}},
          open(f"{D}/raw/logos_squad_2026-10-14T0238.json", "w"), ensure_ascii=False, indent=1)
print(len(d), sum(1 for v in d.values() if (v.get("file") or "").strip()))
