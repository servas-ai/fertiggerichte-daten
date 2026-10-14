"""Daten-Squad 2026-10-14T0202: Juit (juit.com) wordmark for the new online meal-prep provider.
Source: official https://www.juit.com/favicon/transparent.svg (robots: only /order /profile /checkout /thankyou disallowed);
paths unchanged, only the viewBox tightened from 0 0 16 16 to 2.8 5.3 10.5 5 (wordmark crop). Vision gate via Read of a
630 px render on white: black block 'JUIT' wordmark, legible, no placeholder."""
import json, os, csv, hashlib, shutil, datetime
D = "/workspace/fertiggerichte-daten"; P = "/workspace/fertig/analysis/logos.json"; LOGOS = "/workspace/fertig/analysis/logos"
src = f"{D}/scripts/logo_work_T0202/juit.svg"
d = json.load(open(P))
sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
if not (d.get("juit") or {}).get("file"):
    dest = f"{LOGOS}/juit.svg"; assert not os.path.exists(dest); shutil.copy(src, dest)
    d["juit"] = dict(slug="juit", name="Juit", brands=["Juit", "JUIT", "Juit GmbH"], logo_category="Online-Mealprep", file="logos/juit.svg",
        source="https://www.juit.com/favicon/transparent.svg", size="svg", hq=True,
        note="Vision gate 2026-10-14T0202 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar) · offizielles juit.com Favicon-SVG = JUIT-Wordmark (#1C1C1C), Pfade unverändert, nur viewBox auf die Wortmarke zugeschnitten")
    tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)
rows = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"), "source_url": v.get("source"), "brands": v.get("brands")} for k, v in d.items()]
json.dump(rows, open(f"{D}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{D}/data/logos.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, ["slug", "name", "category", "file", "source_url", "brands"]); w.writeheader()
    for r in rows: w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
json.dump({"run": "2026-10-14T0202 Daten-Squad", "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
           "added": [{"slug": "juit", "source": d["juit"]["source"], "sha256": sha, "note": d["juit"]["note"]}],
           "vision_gate": {"juit": "PASS — black JUIT block wordmark on white (630x300 render)"},
           "counts": {"total_rows": len(d), "with_file": sum(1 for v in d.values() if (v.get("file") or "").strip())}},
          open(f"{D}/raw/logos_squad_2026-10-14T0202.json", "w"), ensure_ascii=False, indent=1)
print(len(d), sum(1 for v in d.values() if (v.get("file") or "").strip()))
