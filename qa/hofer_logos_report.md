# QA HOFER-Produkte, Logos, Hersteller (12.10.2026)

Maschinenlesbare Fixes: `qa/hofer_logos_fixes.json` (Skript: `qa/hofer_qa.py`). Die App wurde nicht verändert.

## 1. HOFER-Produkte (115 in scored.json, plus hofer_goodchoice.json und hofer_lidl.json)
- **Herkunftsland:** Alle 35 Open-Food-Facts-EANs unter HOFER sind laut OFF in Österreich bei Hofer gelistet. Es gibt keine reinen DE- oder CH-Artikel, deshalb wird nichts entfernt.
- **Bilder:** Alle 50 Bild-URLs laden (HTTP 200, image/*).
- **Preis-Stichprobe:** Good Choice Käsespätzle 380 g kostet laut wokostswas 3,06 € (12.10.2026). Das stimmt.
- **Entfernen, weil kein Fertiggericht oder trockene bzw. Konzentrat-Werte (9):** Rohkost-Salatmix, Snack Fun Chips, Mürbteig, Cucina Nobile LASAGNE di semola (trockene Blätter, 354 kcal), Le Gusto Klare Gemüsesuppe und Klare Rindsuppe (Konzentrat, 0–3 kcal), Le Gusto Hühnersuppe mit Nudeln (Instantsuppe 61 g, 328 kcal), Le Gusto „Curry“ (ohne Daten), BRUNCH Mango Curry (Brotaufstrich).
- **Aus dem Ranking nehmen, weil Beilage oder Snack (7):** die 3 Primana-Snackboxen, Frittaten, Grießnockerl, Eiersalat und Mürbteig.
- **Datenfehler:**
  - FairHOF Maishendl Ministeaks: 36 kcal bei 23 g Protein ist unmöglich. Den Wert auf null setzen und das Produkt aus dem Ranking nehmen.
  - Risotto con i funghi: 3,1 g Salz pro 100 g, das ist wahrscheinlich der Trockenwert.
  - Chili con carne (OFF): aktuelle Werte sind 99 kcal, 4,7 g Protein und 2,8 g Salz.
  - Faschierte Laibchen: Packungsgröße ist 400 g, nicht 430 g.
  - XXL Lasagne und Gefüllte Gnocchi: Größe fehlt.
  - Pikante Knödel: Der Preis von 2,39 € ist ein Flugblatt-Aktionspreis.
- **18 Duplikate:** Die hofer.at-Datensätze von 2025 kommen doppelt vor (einmal ohne Marke mit Preis, einmal mit Marke ohne Preis). Dazu kommen OFF- und wokostswas-Doppelungen bei Käsespätzle, Schwammerlsauce, Laibchen, Chili, Bohnensuppe, Knödeln und Risotto. Die Datensätze mergen und einen behalten.
- **Fehlende Marke:** In 36 Datensätzen fehlt `brand`, sie steht nur im Produktnamen.
- **Alte oder fehlende Preise:** 35 Preise stammen aus 2025 und gelten als veraltet. 35 OFF-Datensätze haben gar keinen Preis.
- **Fehlen in scored.json, obwohl sie in hofer_goodchoice.json stehen:**
  - Good Choice Lasagne Bolognese 1 kg (EAN 4099200163659, AT 41586 EG Hochreiter)
  - Primana Gulaschsuppe (4099200121567)
  - Lasagne 400 g (4099200053707)

## 2. Logos (analysis/logos und logos.json)
- **Ersetzt: hofer.svg.** Vorher war das Aldi-Süd-Logo von 2017 drin, jetzt ist es das aktuelle HOFER-Logo (Commons, File:Hofer_Logo_2017.svg). logos.json ist aktualisiert, die Sicherung liegt in qa/logo_backup/.
- **Ersetzt: knorr.png.** Das alte Logo ist durch Knorr Logo 2020 ersetzt (als PNG mit 300 px gerendert).
- **Schlechte Qualität, besseres Logo nötig:** gms-gourmet (nur Favicon), graninger (Favicon), hochreiter (winzig), karnerta (abgeschnitten), wiesbauer und wiesbauer-gourmet (identisches 718-Byte-Favicon).
- **Sonst in Ordnung:** Alle übrigen rendern mit der richtigen Marke. Die zwei rewe-*.svg zeigen das REWE-Group-Konzernlogo, das ist korrekt. Kontaktbogen: qa/render/sheet.png.
- **Hinweis:** Die Hersteller-PNGs sind (noch) nicht in logos.json eingetragen. Ein anderer Strang legt dort parallel Dateien an.

## 3. Hersteller
- **Bundesland:** Bei allen 15 AT-Kennzeichen passt das Präfix zum angegebenen Bundesland.
- **Belegt:**
  - GMS Gourmet ↔ Good Choice Gemüsecurry
  - Hochreiter ↔ Good Choice Lasagne 1 kg (OFF emb_codes)
  - Hubers ↔ FairHOF Ministeaks
  - Landena ↔ Primana Chili und S-Budget/Clever Gulasch
- **Probleme:**
  - FSC-C010395 steht bei Leibspeis Kasnudeln als producer_id. Das ist ein FSC-Verpackungszertifikat und muss raus.
  - AT 92584 EG ist nicht aufgelöst.
  - Wiesbauer Wurstspezialitäten (AT 92556 EG) hat ein Profil ohne Produkte.
  - Bei Greisinger sind nur Würste zugeordnet, keine Fertiggerichte.
  - Landena „Curry Madras – Pure Beef“: Marke und Kette prüfen.
  - Hofer Pastasalat und Tortelloni Käse haben DE-Kennzeichen. Das ist plausibel, im UI sollte DE als Herkunft angezeigt werden.
