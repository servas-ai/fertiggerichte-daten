"""Build Good Choice public files for non-supermarket Linz providers from food-connectors outputs.
Writes (under flock /tmp/fertig-data.lock): fertig-app/public/linz_providers.json, public/stores_linz_providers.json"""
import json, fcntl, glob, datetime
D = "/workspace/wt-linz-providers/data/linz"
PUB = "/workspace/fertig-app/public"
deliv = json.load(open(f"{D}/delivery_4020_2026-10-13.json"))
dmap = {p["id"]: p for p in deliv["providers"]}
DEL = {"fit2go": "fit2go", "fittaste": "fittaste", "nordsee": None, "subway": None, "prepmymeal": "prepmymeal", "livefresh": "livefresh"}
KIND = {"fit2go": "meal-prep (TK, Linz)", "fittaste": "Glasgerichte (Versand)", "nordsee": "to-go Kette (Filialen)", "subway": "to-go Kette (Filialen)", "prepmymeal": "meal-prep (TK, Versand)", "livefresh": "meal-prep (TK, Versand)"}
rows = []
for src in ("fit2go", "fittaste", "nordsee", "subway", "prepmymeal", "livefresh"):
    for p in json.load(open(sorted(glob.glob(f"{D}/{src}_*.json"))[-1])):
        n = p.get("nutrition_100g") or {}; ex = p.get("extra") or {}; g = p.get("size_g")
        dv = dmap.get(DEL[src]) if DEL[src] else None
        rows.append({"provider": src, "provider_type": KIND[src], "segment": ex.get("segment", "ready_meal"),
            "name": p["name"], "brand": p.get("brand"), "store": p["store"], "img": p.get("image_url"), "url": p.get("source_url"),
            "price": p.get("price_eur"), "size": g, "ppk": p.get("unit_price_eur"),
            "kcal": n.get("kcal"), "p100": n.get("protein"), "fat": n.get("fat"), "sat": n.get("satfat"), "carbs": n.get("carbs"),
            "sugar": n.get("sugar"), "fib": n.get("fiber"), "salt": n.get("salt"),
            "kcalpack": round(n["kcal"] * g / 100) if n.get("kcal") and g else None, "protpack": round(n["protein"] * g / 100, 1) if n.get("protein") and g else None,
            "allergens": ex.get("allergens"), "ingredients": ex.get("ingredients"), "nutriscore": None, "nova": None,
            "delivers_4020": dv["delivers_4020"] if dv else "n/a (Filiale)", "delivery_source": dv["source_url"] if dv else None,
            "ppp": ex.get("price_per_portion_eur") or (p.get("price_eur") if src in ("fit2go", "fittaste", "prepmymeal", "livefresh") else None), "per_portion": ex.get("per_portion"), "price_variants": ex.get("price_variants_eur"), "traces": ex.get("traces"),
            "nut_basis": ex.get("nutrition_basis") or ("pro 100 g lt. Anbieter"), "fetched_at": p.get("fetched_at")})
stores = json.load(open(sorted(glob.glob(f"{D}/stores_osm_*.json"))[-1]))
f2g = json.load(open(sorted(glob.glob(f"{D}/fit2go_*.json"))[-1]))[0]["extra"]["stores"]
stores += [dict(s, chain="fit2go", segment="ready_meal", provider_type="meal-prep", source="fittogo.at Impressum") for s in f2g]
for _st in stores:
    if _st.get("chain") == "Nordsee":
        _st["chain"] = "NORDSEE"
meta = {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "reference": deliv["address"],
        "ref_latlon": [deliv["lat"], deliv["lon"]], "delivery": deliv["providers"],
        "counts": {"rows": len(rows), "ready_meal": sum(r["segment"] == "ready_meal" for r in rows), "stores": len(stores)}}
with open("/tmp/fertig-data.lock", "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    json.dump({"meta": meta, "rows": rows}, open(f"{PUB}/linz_providers.json", "w"), ensure_ascii=False)
    json.dump({"meta": {k: meta[k] for k in ("generated_at", "reference", "ref_latlon")}, "license": "Stores: ODbL © OpenStreetMap contributors", "stores": stores},
              open(f"{PUB}/stores_linz_providers.json", "w"), ensure_ascii=False)
print(meta["counts"])
