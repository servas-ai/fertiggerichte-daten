"""Daten-Squad 2026-10-18T0102 (daten-only while the fertig uid freeze is on):
GOURMET Daheim follow-up — +2 vision-gated logos (GOURMET Daheim store/brand logo, Mahlzeit Linz seller logo),
+1 alias (GMS GOURMET GmbH → gms-gourmet), +8 vision-gated dish photos on GOURMET Daheim rows from Mahlzeit's
public WordPress media library (5 by exact article number in the file name, 3 by unique dish-name match)."""
import csv, json, hashlib, os, datetime, collections
D = "/workspace/fertiggerichte-daten"
W = os.path.join(D, "scripts/logo_work_T0102")
NOW = datetime.datetime.now(datetime.UTC).isoformat()

# ---------- logos ----------
GD_SRC = "https://www.gourmet-daheim.at/_assets/5e439985603ece5f8b37fa61dd03305a/Logos/gourmet-daheim-logo-vector.svg"
MZ_SRC = "https://www.mahlzeit.co.at/wp-content/uploads/2021/01/icon.png"
new_rows = [
    {"slug": "gourmet-daheim", "name": "GOURMET Daheim", "category": "Handelskette", "file": "logos/gourmet-daheim.png",
     "source_url": GD_SRC + " (gourmet-daheim.at header logo; robots Allow: /; official grey vector, rendered 800 px with rsvg-convert, unmodified; vision gate PASS)",
     "brands": ["GOURMET Daheim", "Gourmet Daheim", "Online: GOURMET Daheim (Mahlzeit Linz)", "Online: GOURMET Daheim"]},
    {"slug": "mahlzeit", "name": "Mahlzeit Linz", "category": "Handelskette", "file": "logos/mahlzeit.png",
     "source_url": MZ_SRC + " (mahlzeit.co.at homepage hero logo wp-image-1367, 428x225 RGBA; robots Disallow: empty; unmodified; vision gate PASS)",
     "brands": ["Mahlzeit", "Mahlzeit Linz", "Mahlzeit Linz (Mahlzeit Vertriebsges.m.b.H.)", "Mahlzeit Vertriebsges.m.b.H.",
                "MAHLZEIT Vertriebsgesellschaft m.b.H."]},
]
rows = json.load(open(f"{D}/data/logos.json"))
known = {b.lower(): r["slug"] for r in rows for b in (r.get("brands") or [])}
for nr in new_rows:
    assert not any(r["slug"] == nr["slug"] for r in rows), nr["slug"]
    coll = [b for b in nr["brands"] if b.lower() in known]
    assert not coll, ("alias collision", coll)
    rows.append(nr)
alias_added = []
for r in rows:
    if r["slug"] == "gms-gourmet":
        if "gms gourmet gmbh" not in known:
            r["brands"] = list(r.get("brands") or []) + ["GMS GOURMET GmbH"]; alias_added.append("GMS GOURMET GmbH → gms-gourmet")
json.dump(rows, open(f"{D}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{D}/data/logos.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, ["slug", "name", "category", "file", "source_url", "brands"]); w.writeheader()
    for r in rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

# ---------- photos ----------
BASE = "https://www.mahlzeit.co.at/wp-content/uploads/"
PHOTOS = {  # article no -> (url, match basis, vision note)
    "2301928": (BASE + "2021/01/2301928_Topfenknoedel_Erdbeermus_web.jpg", "article no. in file name", "4 Topfenknödel in Bröseln on Erdbeermus — PASS"),
    "2302287": (BASE + "2021/01/2302287_Schweinsbraten_Serviettenknoedel_web.jpg", "article no. in file name", "Schweinsbraten, Serviettenknödel, warmer Krautsalat — PASS"),
    "2302564": (BASE + "2021/01/2302564_Ausgeloestes_Backhenderl_web.jpg", "article no. in file name", "breaded chicken with Risipisi — PASS"),
    "2310057": (BASE + "2021/01/2310057_Rindsgulasch_Spaetzle_web-1.jpg", "article no. in file name", "Rindsgulasch with Spätzle — PASS"),
    "2311070": (BASE + "2021/01/2311070_Schweinsmedaillons_web.jpg", "article no. in file name", "pork medallions, rosemary potatoes, mixed vegetables — PASS"),
    "2313494": (BASE + "2025/01/Salbeihuhn_2023_quer_wb-scaled.jpeg", "unique dish name 'Salbeihuhn' (1 of 141 rows)", "chicken ragout in sauce with rice — PASS"),
    "2310182": (BASE + "2025/01/Krautfleckerl_2023_quer_wb-scaled.jpeg", "unique dish name 'Krautfleckerl' (1 of 141 rows)", "Krautfleckerl (pasta squares with cabbage) — PASS"),
    "2302188": (BASE + "2025/01/Zwiebelrostbraten_2023_quer_36203_wb-scaled.jpeg", "unique dish name 'Zwiebelrostbraten' (1 of 141 rows)", "Rostbraten with fried onions and Bratkartoffeln — PASS"),
}
p = f"{D}/data/online_mealprep.csv"
rd = list(csv.DictReader(open(p, newline="")))
fields = list(rd[0].keys())
done = []
for r in rd:
    if r["brand"] != "GOURMET Daheim": continue
    art = r["url"].split("art=")[-1]
    if art in PHOTOS and not r["image_url"]:
        r["image_url"] = PHOTOS[art][0]; done.append({"art": art, "name": r["name"], "image_url": PHOTOS[art][0],
                                                      "match": PHOTOS[art][1], "vision": PHOTOS[art][2]})
assert len(done) == 8, len(done)
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, fields); w.writeheader(); w.writerows(rd)
gd = [r for r in rd if r["brand"] == "GOURMET Daheim"]

bc = collections.Counter(r["brand"].strip() for r in rd)
ev = {"run": "2026-10-18T0102 Daten-Squad", "generated_at": NOW,
      "logos_added": [{**nr, "sha256": hashlib.sha256(open(f"{W}/{nr['slug']}.png", "rb").read()).hexdigest(),
                       "online_mealprep_rows_impacted": sum(bc.get(b, 0) for b in nr["brands"])} for nr in new_rows],
      "logo_vision": {"gourmet-daheim": "PASS — three chef's-hat outline + GOURMET wordmark + DAHEIM, grey #6b6b6b-ish on transparent, legible on white",
                      "mahlzeit": "PASS — 'mahlzeit' wordmark (mahl red, zeit grey) in grey swoosh ellipse, slogan 'Das Menü das zu Ihnen kommt', partner line Rotes Kreuz | Volkshilfe | Samariterbund"},
      "aliases_added": alias_added,
      "photos": done, "photo_source": "Mahlzeit WordPress media library via public REST /wp-json/wp/v2/media (452 items, 5 pages; robots: Yoast Disallow empty); food-connectors 4dab3a4 maps the article-number files live",
      "photos_rejected": {
          "Huehnerschnitzel_Kartoffelpueree_2023_Panorama-quer_sRGB_36257_wb-scaled.jpeg": "pureed (Breikost) dish; probably 2310273 'Hühnerschnitzel in Zwiebelsauce mit Püree' but the file name omits the sauce and 2301562 'Gebackenes Hühnerschnitzel mit Kartoffeln' also fits the words → ambiguous, not taken",
          "2313512.jpg / 2313521.jpg / 2313159.jpg / 2313251.jpg": "7-digit names without a matching article in the 2026 price list → not mapped",
          "Schweinsbraten_-Serviettenknoedel_Krautsalat_2023_...": "duplicate subject of 2302287 (article-number file preferred)",
          "Breikost-Potpourri_web.jpg, medailloons-scaled.jpg, 2.jpg, 3.jpg": "generic/collage or no unique dish → not mapped",
          "shopmahlzeit.gourmet.at": "registration webshop; TLS reset from the box (T0006) → not used"},
      "gourmet_daheim_photos": f"{sum(1 for r in gd if r['image_url'])}/{len(gd)}",
      "staging": "logo files only in scripts/logo_work_T0102 until the fertig uid freeze lifts; online_mealprep.csv updated in daten only"}
json.dump(ev, open(f"{D}/raw/gourmet_daheim_photos_logos_2026-10-18T0102.json", "w"), ensure_ascii=False, indent=1)
print("ok logos", len(rows), "photos", ev["gourmet_daheim_photos"], [x["online_mealprep_rows_impacted"] for x in ev["logos_added"]], alias_added)
