# Fertiggerichte nach Verpackungsart – Gesundheits-KPI-Vergleich

Stand 12.10.2026 · 882 Produkte nach Dedupe (davon 842 Gerichte, 40 Nicht-Gerichte wie Teigblätter oder Kräuter ausgeschlossen) · Quellen: billa.json, spar.json, spar_live.json, hofer_lidl.json, frozen_quick.json, other.json

## Medianwerte je Verpackungsart

| Typ | n | Protein g/100g | Protein g/100kcal | Salz g/100g | ges. Fett | Zucker | Ballaststoffe (n) | €/kg | € pro 10 g Protein | Health-Score |
|---|---|---|---|---|---|---|---|---|---|---|
| Sous-vide (vakuum) | 9 | 14.5 | 11.1 | 1.4 | 1.85 | 2.25 | 0.5 (1) | 24.96 | 1.63 | 57.85 |
| Tiefkühl (TK) | 94 | 9.5 | 6.05 | 1.3 | 2.2 | 1.0 | 1.8 (21) | 15.61 | 1.87 | 46.35 |
| Glas | 12 | 1.9 | 4.46 | 0.95 | 0.15 | 2.85 | – (0) | 10.14 | 10.42 | 39.3 |
| Kühlregal (Menüschale/frisch) | 224 | 7.0 | 4.3 | 1.1 | 1.9 | 1.9 | 2.1 (34) | 11.86 | 1.9 | 34.5 |
| Dose/Konserve | 84 | 4.7 | 4.27 | 1.2 | 1.45 | 1.6 | 1.1 (5) | 8.11 | 1.86 | 32.7 |
| Unklar (keine Lagerangabe) | 204 | 5.3 | 3.71 | 1.1 | 1.1 | 2.2 | 1.5 (28) | 9.8 | 1.68 | 31.9 |
| Trocken/Instant | 215 | 9.2 | 3.32 | 2.5 | 1.9 | 4.3 | 2.5 (129) | 11.96 | 2.3 | 23.3 |

**Achtung:** Bei Trocken-/Instant-Produkten beziehen sich die Nährwerte oft auf das **Trockenpulver**. Das bläht Protein und Salz pro 100 g auf, deshalb ist dort *Protein pro 100 kcal* die faire Kennzahl. „Unklar“ heißt, dass die Quelle keine Kategorie oder Lagerart nennt. „Glas“ hat nur n=10, das ist nicht belastbar.

## Kernaussagen
1. **Sous-vide (z. B. BILLA Genusswelt Rindsbackerl, Ripperl)** liegt beim Protein klar vorne, mit ~14,5 g/100 g und ~11 g pro 100 kcal. Der Health-Score liegt im Median bei 58, dafür ist es am teuersten (~25 €/kg). Pro 10 g Protein ist Sous-vide trotzdem eine der günstigsten Varianten, weil es fast reines Fleisch ist.
2. **Tiefkühl (TK)** ist der beste Allrounder: Median 9,5 g Protein, ~6 g Protein pro 100 kcal, wenig Zucker und ein Health-Score von ~46. Darunter fallen viele Rohprodukte wie Fisch, Spieße und Ripperl, die im Multipot ideal sind.
3. **Kühlregal-Menüschalen (Good Choice, Omis Schmankerl, Hofstädter, Clever)** liegen im Mittelfeld: ~7 g Protein, ~1,1 g Salz und ein Score von ~35. Sie haben die kürzeste Haltbarkeit, sind am wenigsten hitzebelastet und oft eher NOVA 3 als 4.
4. **Dose/Konserve** ist am billigsten pro kg (~8 €/kg), aber proteinarm (~4 g/100 g, Eintöpfe und Suppen ziehen den Wert nach unten). Das Salz liegt mit ~1,2 g ähnlich wie bei Kühlware, der Score bei ~33. Ausreißer nach oben sind Gulasch-Dosen (S-Budget Rindsgulasch: ~38 g Protein für 2,99 €).
5. **Trocken/Instant (Knorr, Maggi, Becher-Nudeln)** schneidet am schlechtesten ab: Salz-Median 2,5 g/100 g, nur ~3,3 g Protein pro 100 kcal, Zucker 4,3 g und fast immer NOVA 4 (Aromen, Geschmacksverstärker, Maltodextrin). Der Score liegt bei ~23, die Kosten bei ~2,3 € pro 10 g Protein.

## Gesundheitsaspekte je Verpackungsart (Recherche)
- **Nährstoffverlust durch Hitze:** Sterilisieren in der Dose (Retort, ~116–121 °C) zerstört wasserlösliche, sauerstoffempfindliche Vitamine (C, B) stärker. Beim Konservieren gehen im Schnitt >60 % Vitamin C verloren, beim Tiefkühlen inkl. Blanchieren ~50 % (Spanne 10–80 %). Danach ist die Dose dank Sauerstoffausschluss stabil, TK verliert bei langer Lagerung weiter (20–50 % nach 1 Jahr bei −18 °C). Protein, Mineralstoffe und Ballaststoffe bleiben weitgehend erhalten. Quelle: Rickman, Barrett & Bruhn 2007, J Sci Food Agric 87:930 – https://onlinelibrary.wiley.com/doi/10.1002/jsfa.2825 (Volltext: https://ucanr.edu/sites/default/files/2010-06/19187.pdf); Teil 2 (Vitamin A, Mineralstoffe, Ballaststoffe): https://doi.org/10.1002/jsfa.2833
- **Kühlregal/Sous-vide:** Pasteurisiert (meist 70–95 °C) statt sterilisiert, daher schonender, aber nur Tage bis wenige Wochen haltbar (Kühlkette ≤ 4 °C nötig).
- **BPA/Dosenbeschichtung:** Die EFSA hat den TDI für BPA 2023 um den Faktor ~20.000 auf 0,2 ng/kg KG/Tag gesenkt; die Exposition liegt in allen Altersgruppen darüber – https://www.efsa.europa.eu/de/news/bisphenol-efsa-draft-opinion-proposes-lowering-tolerable-daily-intake (Gutachten: https://doi.org/10.2903/j.efsa.2023.6857). Die EU-VO 2024/3190 verbietet BPA in Lebensmittelkontaktmaterialien inkl. Doseninnenlacken. Für Einwegdosen gilt eine Übergangsfrist bis **20.07.2026**, für Obst/Gemüse- und Fischkonserven bis 20.01.2028, danach noch 12 Monate Befüllung und Abverkauf bis die Bestände aufgebraucht sind. Ältere Ware im Regal kann also noch BPA-Lacke haben – https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=OJ%3AL_202403190
- **Kunststoffschalen/Beutel:** Mikrowellen-Erhitzen in der Kunststoffschale fördert die Migration. Besser ist es, den Inhalt in einen Edelstahl- oder Glaseinsatz für den Multipot umzufüllen.
- **NOVA-Verarbeitungsgrad** (Monteiro et al. 2019, https://doi.org/10.1017/S1368980018003762): Instant/Trocken ist fast immer **NOVA 4** (Hefeextrakt, Aromen, Glutamat, Maltodextrin, modifizierte Stärke). Dosen-Fertiggerichte sind meist NOVA 4 (modifizierte Stärke, Aromen) und Kühl-Menüschalen schwanken zwischen 3 und 4. Pures TK-/Sous-vide-Fleisch oder -Fisch ist NOVA 1–3. Hoher UPF-Konsum ist mit höherem Risiko u. a. für Herz-Kreislauf-Erkrankungen und Mortalität assoziiert (Lane et al. 2024, BMJ, https://doi.org/10.1136/bmj-2023-077310).
- **Haltbarkeit (typisch):** Dose 2–4 Jahre · Trocken/Instant 12–24 Monate · Glas 1–2 Jahre · TK 12–24 Monate bei −18 °C · Retort-Pouch 12–18 Monate · Sous-vide gekühlt 2–6 Wochen · Kühl-Menüschale 5–21 Tage. (Branchenübliche Werte, keine Einzelquelle; MHD auf der Packung ist maßgeblich.)

## Health-KPI-Score (0–100) – Formel
Basis 30 Punkte, dann:
- **Protein-Dichte** +0…40: `min(Protein g / 100 kcal ÷ 10, 1) × 40` (≥10 g/100 kcal ergibt volle Punktzahl)
- **Salz-Malus** 0…−20: `−min(max(Salz − 0,6, 0) / 1,4, 1) × 20` (ab 2,0 g/100 g volle Strafe)
- **Gesättigte-Fette-Malus** 0…−15: `−min(max(ges. Fett − 1,5, 0) / 4,5, 1) × 15` (ab 6 g volle Strafe)
- **Ballaststoff-/Gemüse-Bonus** 0…+20: `min(Ballaststoffe / 6, 1) × 15` plus +5, wenn Gemüse oder Hülsenfrüchte im Namen stehen
- **Verarbeitungs-Malus** 0…−10: `−(NOVA-Schätzung − 3) × 10`, NOVA je Typ: Dose/Instant/Pouch 4, TK/Kühl/Glas 3,5, Sous-vide 3, rohe/marinierte Fleischstücke 3
- Auf 0–100 begrenzt. Fehlende Werte geben weder Bonus noch Malus. Ohne kcal/Protein gibt es keinen Score.

Die Felder pro Produkt in `scored.json` sind `packaging`, `health_score`, `protein_per_euro` (g Protein/€), `price_per_10g_protein`, `protein_per_100kcal` und `is_meal`.

## Top 10 je Verpackungsart (Health-Score)


### Dose/Konserve

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [Njami Chicken Bowl Mexicana](https://shop.billa.at/produkte/njami-chicken-bowl-mexicana-00885825) | Njami | BILLA | 55.1 | 11.3 | 1.1 | 3.49 | 5.19 |
| 2 | [Inzersdorfer Rindsgulasch 400 G](https://www.interspar.at/p/145664) | Inzersdorfer | INTERSPAR (live) | 49.2 | 10 | 1.1 | 6.99 | 5.72 |
| 3 | [Inzersdorfer Rindsgulasch](https://shop.billa.at/produkte/inzersdorfer-rindsgulasch-002154) | Inzersdorfer | BILLA | 48.9 | 10.0 | 1.1 | 6.99 | 5.72 |
| 4 | [BILLA Chili Con Carne XXL](https://shop.billa.at/produkte/billa-chili-con-carne-xxl-00771705) | BILLA Immer Gut | BILLA | 48.3 | 7.2 | 0.91 | 3.99 | 8.12 |
| 5 | [S-BUDGET Rindsgulasch 400 G](https://www.interspar.at/p/7442025) | S-BUDGET | INTERSPAR (live) | 48.0 | 9.4 | 1.1 | 2.99 | 12.58 |
| 6 | [Veganer Eintopf | Linsen](https://world.openfoodfacts.org/product/4061459832143) | My Vay |  | 46.8 | 3.1 | None | – | – |
| 7 | [Inzersdorfer Rindsgulasch 800 G](https://www.interspar.at/p/145930) | Inzersdorfer | INTERSPAR (live) | 46.4 | 9.7 | 1.2 | 10.49 | 7.4 |
| 8 | [Inzersdorfer Rindsgulasch](https://shop.billa.at/produkte/inzersdorfer-rindsgulasch-0011369) | Inzersdorfer | BILLA | 46.1 | 9.7 | 1.2 | 10.49 | 7.4 |
| 9 | [BILLA Bio Linseneintopf](https://shop.billa.at/produkte/billa-bio-linseneintopf-00747939) | BILLA Bio | BILLA | 46.1 | 3.7 | 0.85 | 2.39 | 6.19 |
| 10 | [Curry Madras - Pure Beef](https://world.openfoodfacts.org/product/9002600632279) | inzersdorfer | Billa, tegut... | 45.7 | 7.4 | 1 | – | – |

### Glas

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [BILLA Bio Gemüsebrühe im Glas](https://shop.billa.at/produkte/billa-bio-gemuesebruehe-im-glas-00890306) | BILLA Bio | BILLA | 66.9 | 0.5 | 0.82 | 3.99 | 0.33 |
| 2 | [Jürgen Langbein Gemüse Fond](https://shop.billa.at/produkte/juergen-langbein-gemuese-fond-00937647) | Jürgen Langbein | BILLA | 55.7 | 0.5 | 0.8 | 2.49 | 0.4 |
| 3 | [Little Lunch Protein Bowl Kichererbsen & Linsen](https://www.dm.at/p/d/1923464/little-lunch-eintopf-protein-bowl-kichererbsen-und-linsen) |  | dm | 44.3 | 4.6 | 1.1 | 3.55 | 4.54 |
| 4 | [Little Lunch Chili Sin Carne](https://www.dm.at/p/d/1923461/little-lunch-eintopf-chili-sin-carne-vegan) |  | dm | 44.1 | 4.4 | 1.0 | 3.55 | 4.34 |
| 5 | [Steirerkraft Steirische Käferbohnensuppe g.U.](https://shop.billa.at/produkte/steirerkraft-steirische-kaeferbohnensuppe-gu-00665193) | Steirerkraft | BILLA | 34.5 | 3.5 | 1.4 | 3.99 | 3.51 |
| 6 | [Little Lunch Little Italy Suppe](https://shop.billa.at/produkte/little-lunch-little-italy-suppe-00545362) | Little Lunch | BILLA | 29.8 | 0.8 | 0.74 | 3.59 | 0.78 |
| 7 | [Little Lunch Karotten Orange Suppe](https://shop.billa.at/produkte/little-lunch-karotten-orange-suppe-00452802) | Little Lunch | BILLA | 25.3 | 0.6 | 0.9 | 3.59 | 0.58 |
| 8 | [Auinger Klare Suppe](https://shop.billa.at/produkte/auinger-klare-suppe-00639588) | Auinger | BILLA | 11.9 | 3.0 | 50.0 | 12.99 | 1.25 |

### Kühlregal (Menüschale/frisch)

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [Ja! Natürlich Soja Geschnetzelts](https://shop.billa.at/produkte/ja-natuerlich-soja-geschnetzelts-00726269) | Ja! Natürlich | Billa | 79.7 | 50.0 | 0.02 | 1.49 | 33.56 |
| 2 | [Clever Lachsfilet](https://shop.billa.at/produkte/clever-lachsfilet-00738040) | CLEVER | Billa | 69.0 | 22.0 | 0.11 | 9.99 | 11.01 |
| 3 | [Clever Lachsfilet mit Haut](https://shop.billa.at/produkte/clever-lachsfilet-mit-haut-00487616) | CLEVER | Billa | 68.3 | 21.0 | 0.09 | 6.59 | 9.56 |
| 4 | [Die Grillerei Torpedospieße Chili](https://shop.billa.at/produkte/die-grillerei-torpedospiesse-chili-00775395) | Die Grillerei | Billa | 65.0 | 16.0 | 1.3 | 3.99 | 4.01 |
| 5 | [Hofstädter Fair zum Tier Putengeschnetzeltes](https://shop.billa.at/produkte/hofstaedter-fair-zum-tier-putengeschnetzeltes-00743364) | Hofstädter | Billa | 65.0 | 23.0 | 0.13 | 7.59 | 13.64 |
| 6 | [Revo Lachsfilet](https://shop.billa.at/produkte/revo-lachsfilet-00755952) | Revo | Billa | 63.7 | 13.9 | 0.85 | 4.19 | 3.32 |
| 7 | [Planted Grillspieß](https://shop.billa.at/produkte/planted-grillspiess-00745527) | Planted | Billa | 62.9 | 20.0 | 1.8 | 4.99 | 8.02 |
| 8 | [Bohnen Gulasch Xxl](https://world.openfoodfacts.org/product/9009865004353) | Chef Menü |  | 62.5 | 5.5 | None | – | – |
| 9 | [Omis Schmankerl Szegediner Krautfleisch](https://shop.billa.at/produkte/omis-schmankerl-szegediner-krautfleisch-00869832) | Omis Schmankerl | BILLA | 62.2 | 5.8 | 0.66 | 4.49 | 4.52 |
| 10 | [Simply Good Huhn Rosmarin mit Kartoffeln](https://shop.billa.at/produkte/simply-good-huhn-rosmarin-mit-kartoffeln-00891786) | Simply Good | BILLA | 62.1 | 6.4 | 0.45 | 7.99 | 3.37 |

### Sous-vide (vakuum)

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [BILLA Genusswelt Roastbeef Sous Vide](https://shop.billa.at/produkte/billa-genusswelt-roastbeef-sous-vide-00517799) | BILLA Genusswelt | BILLA | 68.6 | 26.0 | 0.7 | 36.99 | 7.03 |
| 2 | [BILLA Genusswelt Rindsbackerl Sous Vide](https://shop.billa.at/produkte/billa-genusswelt-rindsbackerl-sous-vide-00346357) | BILLA Genusswelt | BILLA | 59.5 | 10.0 | 0.57 | 6.99 | 4.01 |
| 3 | [Die Grillerei Spareribs Sous-Vide BBQ](https://shop.billa.at/produkte/die-grillerei-spareribs-sousvide-bbq-00392364) | Die Grillerei | Billa | 58.8 | 16.0 | 1.4 | – | – |
| 4 | [Hofstädter Rindsschnitzel Sous Vide](https://shop.billa.at/produkte/hofstaedter-rindsschnitzel-sous-vide-00739211) | Hofstädter | BILLA | 58.6 | 12.0 | 1.4 | 7.99 | 3.9 |
| 5 | [Hofstädter Die Grillerei Pulled Beef Sous Vide mit BBQ](https://shop.billa.at/produkte/hofstaedter-die-grillerei-pulled-beef-sous-vide-mit-bbq-00730190) | Hofstädter | BILLA | 57.1 | 16.0 | 1.5 | 10.99 | 7.28 |
| 6 | [Hofstädter Rindsgulasch Sous Vide](https://shop.billa.at/produkte/hofstaedter-rindsgulasch-sous-vide-00739286) | Hofstädter | BILLA | 55.8 | 13.0 | 1.5 | 7.99 | 4.56 |
| 7 | [BILLA Genusswelt Kalbsrahmgulasch Sous Vide](https://shop.billa.at/produkte/billa-genusswelt-kalbsrahmgulasch-sous-vide-00718376) | BILLA Genusswelt | BILLA | 53.9 | 14.0 | 1.4 | 7.99 | 6.13 |
| 8 | [Hofstädter Die Grillerei Beef Ribs Sous Vide](https://shop.billa.at/produkte/hofstaedter-die-grillerei-beef-ribs-sous-vide-00477837) | Hofstädter | BILLA | 34.2 | 15.0 | 1.3 | 17.99 | 8.34 |

### Tiefkühl (TK)

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [Iglo Schlemmerfilet Rotes Curry](https://shop.billa.at/produkte/iglo-schlemmerfilet-rotes-curry-00732067) | iglo | Billa | 72.9 | 9.7 | 0.87 | 6.99 | 5.28 |
| 2 | [Clever Alaska-Seelachsfilets ohne Haut](https://shop.billa.at/produkte/clever-alaskaseelachsfilets-ohne-haut-00261657) | CLEVER | Billa | 70.0 | 17.0 | 0.2 | 6.59 | 24.51 |
| 3 | [Clever Wildlachsfilet ohne Haut](https://shop.billa.at/produkte/clever-wildlachsfilet-ohne-haut-00743965) | CLEVER | Billa | 70.0 | 20.0 | 0.13 | 4.49 | 11.14 |
| 4 | [Teriyaki-Huhn mit Brokkoli und Basmatireis](https://fittogo.at/products/teriyaki-huhn-mit-brokkoli-und-basmatireis) | fit2go.meals (Fit2go GmbH) | Fit to Go online | 68.6 | 11.0 | None | 9.99 | 4.4 |
| 5 | [Hühnerstreifen in Paprikasauce mit Reis](https://fittogo.at/products/huhnerstreifen-in-paprikasauce-mit-reis) | fit2go.meals (Fit2go GmbH) | Fit to Go online | 68.4 | 12.0 | None | 9.99 | 4.2 |
| 6 | [Mozzarella Hühnchen mit Erbsenreis](https://fittogo.at/products/mozzarella-huhnchen-mit-erbsenreis) | fit2go.meals (Fit2go GmbH) | Fit to Go online | 67.8 | 13.5 | None | 9.99 | 5.01 |
| 7 | [BILLA Bio Lachsfilet](https://shop.billa.at/produkte/billa-bio-lachsfilet-00878884) | BILLA Bio | Billa | 67.3 | 20.0 | 0.12 | 7.19 | 5.56 |
| 8 | [Clever Schlemmerfilet Broccoli](https://shop.billa.at/produkte/clever-schlemmerfilet-broccoli-00312930) | CLEVER | Billa | 66.4 | 10.0 | 0.85 | 3.29 | 12.16 |
| 9 | [Pollo Picante](https://fittogo.at/products/pollo-picante) | fit2go.meals (Fit2go GmbH) | Fit to Go online | 65.0 | 15.1 | None | 9.99 | 6.51 |
| 10 | [Auberginen-Chili con Carne mit Käse Überbacken](https://fittogo.at/products/auberginen-chili-con-carne-mit-kase-uberbacken) | fit2go.meals (Fit2go GmbH) | Fit to Go online | 64.4 | 11.0 | None | 9.99 | 4.4 |

### Trocken/Instant

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [4 Diamanten Thunfisch French Dressing](https://shop.billa.at/produkte/4-diamanten-thunfisch-french-dressing-00864957) | Vier Diamanten | BILLA | 55.7 | 19.0 | 0.9 | 0.99 | 16.26 |
| 2 | [Hink Wien Wiener Kalbsrahmgulasch](https://shop.billa.at/produkte/hink-wien-wiener-kalbsrahmgulasch-00949710) | Hink Wien | BILLA | 54.0 | 6.8 | 0.9 | 11.49 | 2.37 |
| 3 | [4 Diamanten Thunfisch Getrocknete Tomaten & Kräuter](https://shop.billa.at/produkte/4-diamanten-thunfisch-getrocknete-tomaten-und-kraeuter-00864927) | Vier Diamanten | BILLA | 52.9 | 19.0 | 1.1 | 0.99 | 16.26 |
| 4 | [Knorr Meisterkessel Bohnen-Speck Suppe](https://shop.billa.at/produkte/knorr-meisterkessel-bohnenspeck-suppe-00414166) | Knorr | BILLA | 51.1 | 6.2 | 0.63 | 2.99 | 10.37 |
| 5 | [4 Diamanten Thunfisch Red Curry](https://shop.billa.at/produkte/4-diamanten-thunfisch-red-curry-00864947) | Vier Diamanten | BILLA | 46.6 | 13.0 | 1.2 | 0.99 | 11.21 |
| 6 | [Knorr Meisterkessel Rindsgulasch](https://shop.billa.at/produkte/knorr-meisterkessel-rindsgulasch-00826519) | Knorr | BILLA | 45.9 | 6.0 | 0.83 | 5.49 | 5.46 |
| 7 | [Gulasch](https://world.openfoodfacts.org/product/9000275639012) | Knorr |  | 45.9 | 6 | 0.83 | – | – |
| 8 | [Rindsgulasch](https://www.interspar.at/shop/lebensmittel/inzersdorfer-rindsgulasch/p/145664) | Inzersdorfer | INTERSPAR/SPAR Online | 45.3 | 9.9 | 1.18 | 6.99 | 5.67 |
| 9 | [Knorr Meisterkessel Hühnersuppe](https://shop.billa.at/produkte/knorr-meisterkessel-huehnersuppe-00867874) | Knorr | BILLA | 43.8 | 2.6 | 0.8 | 2.99 | 4.35 |
| 10 | [Hink Wien Wiener Paprika Henderl](https://shop.billa.at/produkte/hink-wien-wiener-paprika-henderl-00949725) | Hink Wien | BILLA | 43.7 | 6.2 | 1.1 | 10.49 | 2.36 |

### Unklar (keine Lagerangabe)

| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |
|---|---|---|---|---|---|---|---|---|
| 1 | [Edelpilz Gulasch](https://world.openfoodfacts.org/product/9120118928834) | Goldblatt |  | 72.0 | 5.5 | 0.65 | – | – |
| 2 | [Maishendl Ministeaks](https://world.openfoodfacts.org/product/4099200135892) | FairHOF | HOFER | 65.0 | 23 | 0.1975 | – | – |
| 3 | [Brühe - Klare Suppe](https://world.openfoodfacts.org/product/4008391033009) | Seitenbacher |  | 65.0 | 1 | 0.6 | – | – |
| 4 | [Gemüsebrühe](https://world.openfoodfacts.org/product/4006040271130) | Rapunzel | Le retour a la terre, biocoop la Marigoule | 65.0 | 0.5 | 0.95 | – | – |
| 5 | [Klare Suppe Mit Rind](https://world.openfoodfacts.org/product/9002682104336) | Delikatessa |  | 65.0 | 0.5 | None | – | – |
| 6 | [Rindsgulaschfleisch](https://world.openfoodfacts.org/product/2308325005020) | Greisinger |  | 63.3 | 21 | 0.1275 | – | – |
| 7 | [Klare Gemüsesuppe](https://world.openfoodfacts.org/product/4099200008196) | Le Gusto | HOFER | 61.4 | 0.5 | 1.2 | – | – |
| 8 | [Riesengarnelen Thai Curry](https://world.openfoodfacts.org/product/4099200011288) | Almare | Hofer | 61.4 | 12 | 1.2 | – | – |
| 9 | [Bersteiger](https://world.openfoodfacts.org/product/9002668541018) | Wiesbauer |  | 58.6 | 31 | None | – | – |
| 10 | [Pho Suppe mit Huhn](https://world.openfoodfacts.org/product/9010437032780) | Billa |  | 55.1 | 11 | 0.56 | – | – |