"""T1540: Hartl's Kulinarikum nutrition per 100 g from the producer's own product page
(https://www.hartls-kulinarikum.at/hartls-produkte/, 'Nährwerte' toggles = label images
'NÄHRWERTE JE 100 GRAMM' with the dish name printed under the table; transcribed by vision).
Cross-check: myProduct's own published values for Bohnentopf toskana and Puten Kokos Curry
equal these tables exactly. Gate: Atwater (9F+4C+4P) within ±15% of printed kcal or kJ/4.184;
kJ/kcal mismatch >5% is flagged. Applied to myProduct + ADAMAH rows of brand Hartls Kulinarikum."""
import csv, json, re
SRC = "https://www.hartls-kulinarikum.at/hartls-produkte/"
IMG = "https://www.hartls-kulinarikum.at/wp-content/uploads/"
# name: (kJ, kcal, fat, satfat, carbs, sugar, protein, salt, image file)
T = {
 "kichererbsen": (287,73,2.1,0.3,9.1,3.0,2.8,0.8,"Kichererbseneintopf.jpg"),
 "bohnentopf":   (303,72,1.8,0.3,9.2,2.4,3.5,0.7,"Bohnentopf.jpg"),
 "gemüsetopf":   (246,64,1.8,0.3,7.3,3.4,2.7,1.0,"Gemuesetopf.jpg"),
 "kalbsbeuscherl":(397,103,5.3,1.3,6.4,1.1,5.1,1.0,"Kalbsbeuscherl.jpg"),
 "chili con carne":(424,107,5.0,1.2,8.0,3.8,5.7,1.3,"Chili-con-carne.jpg"),
 "puten kokos curry":(330,79,4.6,1.5,5.3,2.8,2.8,1.1,"Puten-Kokos-Curry.jpg"),
 "paprikahendl": (431,111,5.7,1.7,4.3,1.9,8.4,1.1,"Paprikahendl.jpg"),
 "burgunder":    (460,121,5.7,1.1,5.2,2.9,9.0,0.6,"Burgunder-Rindsbraten.jpg"),
 "rehragout":    (334,89,4.0,0.4,4.6,2.5,5.7,0.8,"Rehragout.jpg"),
 "kartoffelgulasch":(278,66,2.9,0.2,8.3,2.5,1.5,0.7,"Kartoffelgulasch.jpg"),
}
P = "data/online_mealprep.csv"
rows = list(csv.DictReader(open(P, encoding="utf-8"))); fields = list(rows[0].keys())
log = []
for r in rows:
    if "Hartl" not in r["brand"] or r["kcal_100"]: continue
    n = r["name"].lower(); key = next((k for k in T if k in n), None)
    if not key: continue
    kj,kcal,f,sf,c,s,p,salt,img = T[key]
    at = 9*f+4*c+4*p; kjk = kj/4.184
    ok = min(abs(kcal-at), abs(kjk-at)) <= 0.15*at
    entry = {"name": r["name"], "store": r["store"], "table": key, "atwater": round(at,1), "kcal": kcal, "kJ_kcal": round(kjk,1), "ok": ok}
    log.append(entry)
    if not ok: continue
    r.update(kcal_100=f"{float(kcal)}", fat_100=str(f), satfat_100=str(sf), carbs_100=str(c), sugar_100=str(s), protein_100=str(p), salt_100=str(salt))
    size = float(r["size_g"]); price = float(r["price_eur"])
    pp = round(p*size/100, 1); r["protein_pack"] = str(pp); r["kcal_pack"] = str(round(kcal*size/100))
    r["eur_per_10g_protein"] = f"{price/pp*10:.2f}" if pp else ""
    r["nut_source"] = f"hartls-kulinarikum.at Produktseite (Hersteller, Nährwert-Etikett '{img}') je 100 g, 2026-10-25"
    flags = [] if "myproduct" in r["store"].lower() else ["adamah.at nennt keine Nährwerte; Werte vom Hersteller Hartl's Kulinarikum"]
    if abs(kjk-kcal) > 0.05*kcal: flags.append(f"Etikett: {kj} kJ ≙ {kjk:.0f} kcal, gedruckt {kcal} kcal")
    flags.append("Ballaststoffe nicht angegeben")
    r["nut_flag"] = "; ".join(x for x in [r["nut_flag"]]+flags if x)
w = csv.DictWriter(open(P, "w", encoding="utf-8", newline=""), fieldnames=fields); w.writeheader(); w.writerows(rows)
json.dump({"source": SRC, "images": {k: IMG+v[-1] for k,v in T.items()}, "tables": T, "applied": log,
           "no_table_published": ["Bio Rindssuppe","Bio Hendlsuppe","Berglinseneintopf","Berglinsencurry","Rindsgulasch","Kalbsrahmgulasch","Szegediner Gulasch","Zwiebelrostbraten","Tafelspitz"]},
          open("raw/hartls_nutrition_2026-10-25T1540.json","w"), ensure_ascii=False, indent=1)
print(sum(e["ok"] for e in log), "filled /", len(log)); [print(e) for e in log]
