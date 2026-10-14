"""iss mich! (issmich.at) Wiener Bio-Eintöpfe & Suppen im WECK-Pfandglas → evidence snapshot raw/issmich_<stamp>.json
(Daten-Squad 2026-10-14T0636).

Source: food-connectors `issmich` adapter (9650f94) — Shopware 6 storefront: sitemap.xml → sales-channel sitemap
.xml.gz + category listings → product pages (schema.org microdata: price incl. MwSt. + Streichpreis, 2,00 € Pfand,
Inhalt g, GTIN-13, SKU, availability, packshots, Zutaten, Allergene). robots.txt `User-agent: * Allow: /`
(only */?, account, checkout, widgets, navigation, bundles disallowed). No login/cookies, 1 req/s.
Nährwerte exist only as the official Nährwerttabelle image (NT_…jpg). VISION below = vision transcription of
those images (2026-10-14T0636, every row cross-checked: per100 × portion/100 = printed per-portion kcal and
protein, Atwater kcal); the adapter's strict tesseract OCR is run as an independent second reader and its
accepted values must equal VISION (mismatch → abort). Ready meals = course Eintopf/Suppe; Beilage/Süßspeise/
Sauce kept only in the evidence. Every packshot is HEAD-checked. Duplicate shop GTINs → ean null (conflict).
Usage: python3 scripts/enrich_issmich.py"""
import sys, json, time, datetime, urllib.request, collections
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import issmich as I
from food_connectors.http import UA

# sku: (portion_g, kcal, fat, satfat, carbs, sugar, protein, salt  [per 100 g], kcal_portion, protein_portion, label)
VISION = {
 "SW10021": (280, 152.4, 10.0, 4.4, 5.1, 3.6, 9.8, 0.77, 426.7, 27.4, None),  # Bio Kashmir Curry vom Huhn
 "VH0002M": (280, 214.4, 21.0, 11.1, 3.4, 2.9, 3.2, 0.45, 600.3, 9.0, 'Vegetarisch'),  # Bio Schwammerl á la Créme
 "BE0001": (200, 166.4, 3.0, 0.5, 27.9, 2.2, 6.6, 1.47, 332.8, 13.2, 'Vegan'),  # Bio Semmelknödel (der wahrscheinlich fla
 "FL0001": (280, 232.4, 17.2, 4.9, 3.5, 3.4, 12.2, 0.34, 650.7, 34.2, None),  # Bio Rotweingulasch vom Freilandrind
 "FL0002": (280, 120.7, 7.3, 2.4, 5.8, 1.3, 7.2, 0.31, 338.0, 20.2, None),  # Tex-Mex Bio Chili con Carne
 "FL0003": (280, 104.5, 5.6, 0.6, 3.3, 2.0, 9.6, 0.35, 292.6, 26.9, None),  # Bio Marokko Huhn mit Salzzitrone
 "FL0004": (280, 102.7, 6.9, 1.5, 2.9, 1.6, 7.1, 0.49, 287.6, 19.9, None),  # Bio Polpette al Sugo
 "FL0005": (280, 150.9, 8.0, 1.6, 3.4, 2.9, 0.9, 0.32, 422.5, 2.5, None),  # Bio Lammragout vom Weidelamm
 "SW10022": (280, 93.0, 5.0, 1.2, 2.9, 2.7, 8.5, 0.32, 260.4, 23.8, None),  # Wiener Bio Saftgulasch
 "SW10023": (280, 103.5, 5.4, 0.8, 7.1, 3.4, 6.3, 0.59, 289.8, 17.6, None),  # Bio Kürbispfanne mit Faschiertem
 "SW10025": (280, 127.9, 8.0, 0.9, 3.8, 2.7, 9.5, 0.62, 358.1, 26.6, None),  # Marokkanische Bio Hühnertajine mit Olive
 "SW10036": (280, 141.2, 8.7, 2.3, 3.1, 2.6, 11.4, 0.49, 395.4, 31.9, None),  # Bio Paprika Hendl nach pannonischer Art
 "SW10061": (280, 140.6, 9.9, 5.3, 3.9, 3.4, 8.6, 0.6, 393.7, 24.1, None),  # Bio Rindergeschnetzeltes Stroganoff Art
 "SW10091": (280, 59.2, 1.0, 0.1, 8.4, 2.0, 2.7, 0.21, 165.8, 7.6, 'Vegan'),  # Serbischer Veganer Bio Erbseneintopf
 "VN0001": (280, 70.9, 1.6, 0.2, 9.4, 3.2, 3.4, 0.44, 198.5, 9.5, 'Vegan'),  # Cremiges Bio Bohnen Chili
 "VN0002": (280, 80.6, 3.6, 0.5, 6.9, 1.5, 3.6, 0.65, 225.7, 10.1, 'Vegan'),  # Bio Erdäpfelgulasch mit gebratenem Räuch
 "VN0003": (280, 40.5, 1.7, 0.2, 4.1, 2.9, 1.3, 0.44, 113.4, 3.6, 'Vegan'),  # Griechische Bio Riesenbohnen in Tomatens
 "VN0004": (280, 81.2, 2.7, 1.0, 9.9, 3.2, 2.7, 0.4, 227.4, 7.6, 'Vegan'),  # Indisches Bio Curry mit Kichererbsen
 "VN0005": (280, 121.8, 5.4, 0.7, 11.0, 2.1, 4.9, 1.08, 341.0, 13.7, 'Vegan'),  # Mama's Bio Linseneintopf
 "VN0006": (280, 64.9, 4.2, 0.6, 4.4, 4.2, 1.3, 0.13, 181.7, 3.6, 'Vegan'),  # Bio Ratatouille - provenzalischer Gemüse
 "VN0007": (280, 82.7, 3.8, 1.2, 9.2, 5.8, 1.5, 0.35, 231.6, 4.2, 'Vegan'),  # Bio Rote Rüben Kokos Curry
 "VN0008": (280, 68.0, 4.3, 0.6, 5.3, 4.6, 1.3, 0.13, 190.4, 3.6, 'Vegan'),  # Bio Peperonata siciliana
 "VN0010": (280, 85.0, 6.6, 0.9, 4.2, 3.3, 1.3, 0.48, 238.0, 3.6, 'Vegan'),  # Bio Caponata - sizilianische Spezialität
 "SW10027": (280, 104.7, 2.5, 1.1, 13.9, 2.2, 5.1, 0.31, 293.2, 14.3, 'Vegan'),  # Bio Dal Eintopf aus Roten Linsen
 "SW10031": (280, 69.3, 2.9, 0.3, 8.8, 3.7, 1.3, 0.57, 194.0, 3.6, 'Vegan'),  # Bio Kürbis Gulasch
 "SW10019": (280, 154.2, 11.1, 2.9, 2.7, 2.4, 10.6, 0.5, 431.8, 29.7, None),  # Bio Ragu alla Bolognese für 2
 "SS0001": (160, 252.9, 16.7, 6.9, 15.4, 14.3, 8.5, 2.94, 404.6, 13.6, 'Vegetarisch'),  # Bio Mohnsoufflé aus feinem Blaumohn
 "SW10020": (260, 149.6, 3.7, 2.2, 26.3, 11.2, 2.6, 0.05, 389.0, 6.8, 'Vegetarisch'),  # Bio Milchreis mit Apfel Zimt Kompott
 "SW10028": (280, 221.2, 23.8, 10.1, 0.9, 0.6, 0.6, 0.04, 619.4, 1.7, None),  # Bio Knochenbrühe vom Rind
 "SN0001": (280, 28.0, 1.5, 0.1, 2.7, 2.4, 0.5, 0.35, 78.4, 1.4, 'Vegan'),  # Bio Sellerie-Apfel Suppe
 "SN0004": (280, 78.6, 5.6, 3.7, 4.4, 4.0, 1.4, 0.4, 220.1, 3.9, 'Vegan'),  # Bio Tomaten Kokos Suppe
 "SW10026": (304, 50.7, 2.8, 1.6, 4.3, 3.4, 0.8, 0.21, 154.1, 2.4, 'Vegan'),  # Bio Karotten-Miso Suppe
 "SW10060": (280, 51.2, 1.7, 0.2, 7.1, 6.7, 0.9, 0.36, 143.4, 2.5, 'Vegan'),  # Bio Rote Rüben Suppe mit Apfel und Kren
 "SH0001": (280, 135.4, 10.2, 5.4, 9.0, 1.2, 1.6, 0.04, 379.1, 4.5, 'Vegetarisch'),  # Bio Chili-Maiscreme Suppe
 "SH0002": (298, 105.0, 8.5, 5.0, 5.3, 2.1, 1.6, 0.53, 312.9, 4.8, 'Vegetarisch'),  # Bio Erdäpfel-Lauchcreme Suppe mit Thymia
 "SW10024": (280, 76.9, 4.5, 1.9, 7.9, 4.2, 1.1, 0.37, 215.3, 3.1, 'Vegetarisch'),  # Weinviertler Bio Kürbissuppe
 "SW10040": (310, 126.3, 11.5, 6.6, 4.4, 1.0, 1.2, 0.11, 391.5, 3.7, 'Vegetarisch'),  # Bio Knoblauchcreme Suppe
 "SW10071": (280, 47.7, 2.3, 1.2, 4.1, 3.2, 0.9, 0.03, 133.6, 2.5, 'Vegetarisch'),  # Französische Bio Zwiebelsuppe
 "SW10147": (280, 72.8, 5.3, 1.8, 2.9, 1.1, 3.0, 0.09, 203.8, 8.4, None),  # Kafanska - Serbische Bio Hühnersuppe
}
NUT_FLAGS = {
    "FL0005": "Etikett unplausibel: 0,9 g Eiweiß/100 g (2,5 g/Portion) bei 150,9 kcal – Atwater ≈ 89 kcal; Werte wie veröffentlicht, Eiweiß vermutlich Tippfehler",
    "SW10028": "Etikett: 23,8 g Fett/100 g für Knochenbrühe (Atwater-konsistent, 221 kcal) – wie veröffentlicht",
}
K = ("kcal", "fat", "satfat", "carbs", "sugar", "protein", "salt")


def head(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", None) or repr(e)[:60]


def main(stamp=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    prods = [p.to_dict() for p in I.IssMich().fetch(category="all", ocr=True)]
    gt = collections.Counter(p["extra"]["gtin_raw"] for p in prods if p["extra"]["gtin_raw"])
    ocr_ok = ocr_rej = 0
    for p in prods:
        x = p["extra"]; sku = p["source_id"]; v = VISION.get(sku)
        if x["nut_ocr"]:
            ocr_ok += 1
            if v:
                diff = {k: (p["nutrition_100g"].get(k), val) for k, val in zip(K, v[1:8]) if abs((p["nutrition_100g"].get(k) or -1) - val) > 0.011}
                assert not diff, (sku, diff)  # two independent readers must agree
        else:
            ocr_rej += 1
        if v:
            por = v[0]
            p["nutrition_100g"] = dict(zip(K, v[1:8]))
            x["portion_g"] = por; x["pack_nutrition"] = {"kcal": v[8], "protein": v[9]}
            x["nut_source"] = "vision transcription of official Nährwerttabelle image (cross-checked per-portion + Atwater)" + ("; tesseract OCR agrees" if x["nut_ocr"] else "")
            if v[10]:
                x["label"] = v[10]; x["vegan"] = v[10] == "Vegan"; x["vegetarian"] = True
        x["nut_flag"] = NUT_FLAGS.get(sku)
        if p["ean"] and gt[p["extra"]["gtin_raw"]] > 1:
            x["gtin_conflict"] = f"GTIN {p['ean']} on {gt[p['extra']['gtin_raw']]} shop products → ean null"; p["ean"] = None
        x["image_head"] = head(p["image_url"]) if p["image_url"] else None
        time.sleep(0.3)
    meals = [p for p in prods if p["extra"]["course"] in I.MEAL_COURSES and p["price_eur"] and p["size_g"] and p["nutrition_100g"].get("protein") is not None and p["extra"]["image_head"] == 200]
    out = {
        "source": "issmich.at Shopware 6 storefront (food-connectors issmich adapter 9650f94) + vision-verified Nährwerttabelle images",
        "fetched": stamp,
        "robots": "User-agent: * Allow: / ; Disallow */? */account/ */checkout/ */widgets/ */navigation/ */bundles/ */imprint$ */privacy$ */gtc$",
        "operator": {
            "name": "iss mich! GmbH", "seat": "Erlafstraße 7, 1020 Wien (AT)", "register": "FN 471722i (Handelsgericht Wien)",
            "founded_register": "2017-05-23 (Eintragung; Rechtsform seit 2014-04-05 lt. Firmenmonitor)", "capital": "EUR 35.000",
            "business": "Handel mit Biolebensmittel; Catering und Lieferservice, Produktion von Speisen und Fertiggerichten",
            "management": "Tobias Judmaier, MSc (Geschäftsführer + Alleingesellschafter lt. Firmenbuch/evi.gv.at)",
            "vat": "ATU72305301", "vies": {"valid": True, "name": "iss mich! GmbH", "address": "Erlafstraße 7\nAT-1020 Wien", "checked": "2026-10-14T06:52:31Z"},
            "bio_control": "AT-BIO-401", "gleif": None,
            "insolvency": "Sanierungsverfahren HG Wien 6 S 177/25h eröffnet 19.12.2025, Unternehmen fortgeführt (08.01.2026), Sanierungsplan 21 % Quote angenommen 24.02.2026, Verfahren aufgehoben 18.03.2026 (ra-jahn.at; Firmenbuch-Eintragungen 23.12.2025 / 14.+21.03.2026)",
            "sources": ["https://www.issmich.at/impressum", "https://www.evi.gv.at/f/471722i", "https://ec.europa.eu/taxation_customs/vies/", "https://www.ra-jahn.at/insolvenz-iss-mich-gmbh-471722i/", "https://firmenmonitor.com/firma/iss-mich-gmbh-471722i"],
        },
        "shipping_at": {"evidence": "https://www.issmich.at/versand-und-bezahlung — 'Wir liefern NICHT ins Ausland sondern ausschließlich in Österreich'; POST-Service (Bestellungen bis So 18:00 → Versand Montag), Wien Fahrrad/Auto; Standardversand Österreich 9,90 €, versandkostenfrei ab 99 €; Selbstabholung Fr 10–13 Uhr", "fee": 9.90, "free_from": 99.0, "carrier": "Österreichische Post", "deposit_per_jar": 2.0},
        "ocr_second_reader": {"accepted": ocr_ok, "rejected": ocr_rej, "mismatches_vs_vision": 0},
        "shop_products": len(prods), "meals_kept": len(meals),
        "excluded": [{"sku": p["source_id"], "name": p["name"], "course": p["extra"]["course"]} for p in prods if p not in meals],
        "products": prods,
    }
    path = f"raw/issmich_{stamp}.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "shop", len(prods), "meals", len(meals), "ocr ok/rej", ocr_ok, ocr_rej, "img200", sum(p["extra"]["image_head"] == 200 for p in prods))
    return path


if __name__ == "__main__":
    main("2026-10-14T0636")
