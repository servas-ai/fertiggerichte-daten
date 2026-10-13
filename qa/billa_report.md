# BILLA QA-Report (2026-10-12)

Quelle: live BILLA-Shop-API `shop.billa.at/api/product-discovery/products/<SKU>` (404 von 404 URLs erfolgreich), Rohdaten in `qa/billa_src.json`. Alle 405 Bild-URLs geprüft: HTTP 200, image/jpeg; Bild-Dateiname enthält bei allen die SKU, passt also zum Produkt.

## Umfang
- 495 BILLA-Einträge (scored.json + expand.json; Überschneidungen werden pro Datei gezählt), 404 eindeutige Shop-URLs, 3 Einträge ohne URL
- 1126 Korrekturen an 211 Produkten in `billa_fixes.json` (Felder: id=url, file, field, old, new, reason)
- 181 Hinweise, die sich nicht aus der Quelle beheben lassen, in `billa_flags.json`

## Korrekturen nach Feld
|Feld|Anzahl|
|---|---|
|price_date|162|
|price_status|162|
|kcal_100|80|
|fat_100|79|
|carbs_100|79|
|protein_100|78|
|sugar_100|78|
|fiber_100|78|
|salt_100|78|
|satfat_100|77|
|dry|63|
|is_meal|61|
|size_g|18|
|kcal_pack|11|
|price_per_kg|10|
|protein_pack|8|
|price_eur|4|

## Wichtigste Befunde
1. **Trockenprodukte (Knorr-Beutelsuppen, Spaghetteria, Pasta Snack, Asia Noodles, Cup a Soup, Sweety):** 63 waren mit `dry=false` und Pulver-Nährwerten markiert, z. B. 13–17 g Protein und 330–550 kcal pro 100 g. Sie sind jetzt `dry=true` und auf die Herstellerangabe *zubereitet* umgestellt, etwa Knorr Eiermuschelsuppe mit 17 → 1,0 g Protein und Spaghetteria Carbonara mit 13 → 3,4 g. Damit fallen viele künstliche Protein-Spitzenreiter weg. Werte pro Packung werden bei Trockenware nicht berechnet, weil Wasser und Milch dazukommen.
2. **Keine Fertiggerichte (`is_meal → false`):** Desserts und Süßes wie Omis Kaiserschmarrn, Strudel, Germknödel, Eisknödel und Germknödeldonut, dazu Suppengemüse, Rohreis (Risottoreis, Ben's Sticky/Curry-Reis lt. Kategorie Rundkorn), Suppenwürze und Bouillon (Knorr Goldaugen, Klare Suppe), Würzmischungen (MAGGI Fix, Knorr Basis, Kräuterlinge), Dressings, eine Suppenterrine aus Zuckerrohr (Geschirr!) und ein Brotaufstrich (Billa Huhn-Curry-Salat).
3. **Preise:** 162 Einträge hatten Preise von 2025 (heisse-preise.io). Alle sind gegen den heutigen Regalpreis geprüft, Datum und Status sind aktualisiert. Wirklich geändert haben sich 4 Preise, darunter Iglo Lasagne (3,49 € bei 350 g → 7,69 € bei 700 g; vorher stand die kleine Variante) und Billa Lasagne Bolognese (4,99 € bei 700 g → 3,19 € bei 400 g). 56 Produkte sind gerade in Aktion; übernommen ist der Regalpreis.
4. **Packungsgrößen:** 18 Korrekturen per Abgleich von Nettogehalt, Menge und Grundpreis, z. B. Vegavita Nuggets 180 → 720 g, Omis Kalbsbutterschnitzel 370 → 330 g und Polly's Marilleneisknödel 840 (ml) → 456 g.
5. **Nährwerte:** 78 Produkte haben auf den aktuellen Datenstand (`validFrom`) umgestellte Werte, das meiste davon sind die Trockenprodukte. Fratelli Barbaro Gnocchi Kürbis hatte kJ im kcal-Feld: 577 → 138 kcal.

## Nicht behebbar (Hinweise)
- **BILLA Marillenknödel**: keine BILLA-Shop-URL – nicht verifizierbar (nur heisse-preise.io)
- **BILLA Nougatknödel**: keine BILLA-Shop-URL – nicht verifizierbar (nur heisse-preise.io)
- **Ben's Original Risotto-Reis**: keine BILLA-Shop-URL – nicht verifizierbar (nur heisse-preise.io)
- **Blue Elephant Tom Kha Suppenpasta**: nur Trockenwerte (Pulver) in Quelle, keine Werte für zubereitetes Gericht – /100g nicht vergleichbar, aus Ranking nehmen
- **Blue Elephant Tom Kha Suppenpasta**: Nährwert unplausibel: Salz>=5 g/100g
- **Germknödeldonut**: Packungsgröße 280.0 passt nicht zum Grundpreis (3.99€ / 3.99€/kg, impliziert 1000)
- **Indomie Instant Nudelsuppe Huhn**: Nährwert unplausibel: kcal 321.0 vs Makro-Rechnung 466
- **Suppengemüse**: keine Nährwerte in API; App-Wert aus Open Food Facts 4337256545266 Suppengemüse (1.00) beibehalten
- **Rana Teriyaki Style Noodels Hühnchen**: Nährwert unplausibel: kcal 113.0 vs Makro-Rechnung 155
- **Pop-Up Sushi Lachs mild**: Nährwert unplausibel: kcal 153.0 vs Makro-Rechnung 206
- **Knorr Asia Gebratene Nudeln Gemüse**: API-Daten inkonsistent: Nettogehalt 139.0 g vs. Menge 1396.0 (Grundpreis basiert vermutlich auf Tippfehler) – Nettogehalt behalten
- **Knorr Asia Gebratene Nudeln Gemüse**: Packungsgröße 139.0 passt nicht zum Grundpreis (2.99€ / 2.14€/kg, impliziert 1397)
- **Clever Grießnockerlsuppe**: Nährwert unplausibel: Salz>=5 g/100g
- **Clever Eiermuschelsuppe**: Nährwert unplausibel: Salz>=5 g/100g
- **Clever Kürbiscremesuppe**: Nährwert unplausibel: Salz>=5 g/100g
- **Clever Nudelsuppe**: nur Trockenwerte (Pulver) in Quelle, keine Werte für zubereitetes Gericht – /100g nicht vergleichbar, aus Ranking nehmen
- **Clever Nudelsuppe**: Nährwert unplausibel: Salz>=5 g/100g
- **Clever Knoblauchcremesuppe**: Nährwert unplausibel: Salz>=5 g/100g
- **Clever Buchstabensuppe**: nur Trockenwerte (Pulver) in Quelle, keine Werte für zubereitetes Gericht – /100g nicht vergleichbar, aus Ranking nehmen
- **Clever Buchstabensuppe**: Nährwert unplausibel: Salz>=5 g/100g
- **MAGGI Magic Asia Nudel Snack Curry**: Nährwert unplausibel: Salz>=5 g/100g
- **MAGGI Magic Asia Nudel Snack Huhn**: Nährwert unplausibel: Salz>=5 g/100g
- **MAGGI Magic Asia Nudel Snack Duck Taste**: Nährwert unplausibel: Salz>=5 g/100g
- **4 Diamanten Thunfisch Getrocknete Tomaten & Kräuter**: Thunfisch-Konserve – eher Zutat als Fertiggericht
- **4 Diamanten Thunfisch Red Curry**: Thunfisch-Konserve – eher Zutat als Fertiggericht
- **4 Diamanten Thunfisch Puttanesca**: Thunfisch-Konserve – eher Zutat als Fertiggericht
- **4 Diamanten Thunfisch French Dressing**: Thunfisch-Konserve – eher Zutat als Fertiggericht
- **Fratelli Barbaro Gnocchi mit Kürbis**: Quelle hat kJ im kcal-Feld; umgerechnet
- **Knorr Kraftbouillon Gemüse**: Nährwert unplausibel: Salz>=5 g/100g
- **MAGGI Fix Ofen-Spirelli alla Mamma**: Nährwert unplausibel: Salz>=5 g/100g
- **Knorr Kräuterlinge Frühlingskräuter**: nur Trockenwerte (Pulver) in Quelle, keine Werte für zubereitetes Gericht – /100g nicht vergleichbar, aus Ranking nehmen
- **Knorr Kräuterlinge Frühlingskräuter**: Nährwert unplausibel: Salz>=5 g/100g
- **Auinger Klare Suppe**: nur Trockenwerte (Pulver) in Quelle, keine Werte für zubereitetes Gericht – /100g nicht vergleichbar, aus Ranking nehmen
- **Auinger Klare Suppe**: Nährwert unplausibel: Salz>=5 g/100g

- Außerdem 91× Hinweis Trockenprodukt (Pro-Packung-Werte unsicher) und 56× aktuell in Aktion.
- 15 Produkte haben in der API keine Nährwerte. Die vorhandenen Werte aus Open Food Facts wurden nicht überprüft.
- Kategorien: Die App-Kategorien (z. B. Suppe/Eintopf, Beilage/Gemüse) sind abgeleitet. Ersetzt wurden sie nur, wenn die App die API-Kategorie falsch übernommen hatte. Alle fragwürdigen Einordnungen laufen über `is_meal`.
- Grenzfälle sind bewusst als Fertiggericht belassen: 4 Diamanten Thunfisch-Zubereitungen (eher Zutat) und Frosta Gemüsepfanne (Kategorie Gemüse, sie wurde trotzdem auf false gesetzt, das bitte prüfen).

Skripte: `qa/fetch.py`, `qa/qa.py`. Andere Dateien wurden nicht verändert.