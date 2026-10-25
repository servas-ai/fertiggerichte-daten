# STAGING_INDEX (hourly Fertiggerichte → Orchestrator merges)

Note 2026-10-24T17: the box was restored; the previous STAGING_INDEX.md and all staged_2026-10-1x files
(97 open rows as of 2026-10-18T06, incl. T04 Gurkerl batch and pending OFF retry for T01/T02) are gone
and were never committed. Those rows must be re-fetched if still wanted.

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-24T17.json | MPreis webshop (food-connectors `mpreis-shop --enrich`) | 19 | 2 meal (Jeden Tag Lasagne Bolognese 1000 g, M Faschiertes Laibchen mit Püree 450 g), 4 dessert (Della Mamma / Dolce Italia Tiramisu ×2, Ehrmann High Protein Mousse), 13 dry instant noodles | open |

Skipped as components/raw (not staged): tofu, vegan cold cuts, spätzle, pasta, püree, knödel, Cordon Bleu, Grießnockerl, pudding powder.
dm fetch (26 products): 0 new.

### Daten-Squad 2026-10-24T1734 (online meal-prep, for the Orchestrator merge)
- New store **Online: Sperchenedergut** (Aspach OÖ): 3 rows in servas-ai/fertiggerichte-daten `data/online_mealprep.csv` (commit d897e4e): Gulaschsuppe, Beuschel, Chili con Carne vom (Bio-)Angusrind, Glas 330 ml, 9,50 €, photos vision PASS, no nutrition/GTIN (size_g empty). Logo staged in daten `scripts/logo_work_T1734/sperchenedergut.png` (logos.json slug `sperchenedergut`).

- 2026-10-24T1811 Daten-Squad: fertiggerichte-daten d18fa19 adds 3 Bauernladen.at rows (Dunzinger's Ruck Zuck Rehragout / Hirschragout vom heimischen Wild 370 g 9,50 €, BBQ Kokos Eintopf VEGAN 330 ml 8,40 €; no photo, no nutrition/GTIN) to data/online_mealprep.csv — candidates for the Orchestrator merge; nothing staged in fertig itself.

- 2026-10-24T1833 Daten-Squad: new store **Online: Wagyuhof** (Wagyuhof GmbH, Haag NÖ, FN 478220s): fertiggerichte-daten c75731c + a711e18 add 4 rows to data/online_mealprep.csv — Wagyu Gulasch, Ragout (Steinpilz-Rahmsoße), Beuschel (13,20 €) and Rouladen (14,90 €, sold out), Frischglas 300 g, full nutrition per 100 g, photos vision PASS, no GTIN. Logo staged in daten `scripts/logo_work_T1833/wagyuhof.png` (logos.csv row slug `wagyuhof`). Candidates for the Orchestrator merge; nothing exported or pushed from fertig.

### hourly 2026-10-24T18 (Gurkerl.at re-fetch of the lost T04 batch)
| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-24T18.json | Gurkerl.at (food-connectors `gurkerl` fetch, then enrich via composition API: EAN + nutrition/100 g + ingredients) | 27 | 2 meal (PICARD Hachis Parmentier 1000 g TK, Ben's Original Street Food Thai Style Noodles 250 g), 2 starter (PICARD 15 Mini Quiches, PICARD 2 Quiches Lorraine), 1 dessert (PICARD 2 Vanille Crème Brûlées), 1 soup (Suppito Brodo vom Rind 510 g, no nutrition), 21 dry instant noodles/pasta snacks (Mama, Nongshim, Acecook, Maggi, Knorr, Oyakata, Namdong) | open |

Dedupe vs fertig-app/public/data.json by gurkerl id, EAN and exact name: dropped as already present Pappudia Spaghetti Bolognese, Iglo Lasagne al Forno, Felix Linsen mit Speck, Knorr Kaiserteller Minestrone, Knorr Pasta Snack Pilz Rahm, Knorr Bitte zu Tisch Frühlingssuppe. 5 dry rows share an EAN with existing MPreis rows (store-specific Gurkerl rows, noted per row).
Skipped as components/raw/sauces (not staged): fonds (Englert, Belfond, Esterhazy), Wonton/Gyoza/Frühlingsrollen sheets, Ben's Express plain rice, sides (Speckkraut, Gabelkraut, Sauerkraut, Rotkraut, Rahmfisolen), meat components (Gansl gebraten, Bedford Hähnchenbrust, Wiesbauer Schweinebacken, PICARD Hühner Cordon Bleu), sauces (Radatz Bolognese, Esterhazy Wild Sugo, Sempio), soup bases/pastes, grains, ice-cream Eisknödel, Knorr Spaghetteria (rejected earlier), Synear sticks. Fetch hit the 500-row limit, so the pizza/fish/M&S categories were not reached this run.

- 2026-10-24T1904 Daten-Squad: new store **Online: Draxler Geflügel-Wild** (Draxler Geflügel-Wild GmbH, Mooskirchen Stmk, FN 214255g, ATU52668607): fertiggerichte-daten 0275fd5 adds 9 rows to data/online_mealprep.csv — Rehragout 10,00 €, Gulasch vom Wild 9,80 €, Wildfleisch Chili 9,80 €, Curry vom Maishendl 9,00 €, Gulasch vom Maishendl 8,80 €, Einmachsuppe vom Maishendl 7,60 €, Suppe vom Maishendl 6,90 €, Vegetarisches Gulasch 6,90 €, Veganes Chili sin Carne 6,90 € (all Glas 360 g, chilled, photos vision PASS 9/9, no nutrition/GTIN, shipping fee only in checkout). Company row draxler-gefluegel-wild + logo (staged daten scripts/logo_work_T1904/draxler.png). Connector `draxler` (food-connectors 187aeb1). Not merged into fertig-app (Orchestrator).

- 2026-10-24T1936 Daten-Squad: no new rows. GOURMET Daheim photo map from Speisekarte 2026 e-paper (127/141 dish pages) in daten af80136 raw/gourmet_daheim_speisekarte2026_photo_map_2026-10-24T1936.json; image_url unchanged (no per-dish linkable URL), decision needed whether page PNGs or hosted dish JPEGs may be used.

### hourly 2026-10-24T19

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-24T19.json | BILLA, Gurkerl, Online: bofrost*, Fit2go, myProduct | 9 | meal 2, soup 2, dessert 2, starter 1, component 2 | open |

- Rows: Omis Schmankerl Kaiserschmarrn (BILLA); bofrost Ente in Orangensauce, Hirschgulasch in Schwarzer-Ribisel-Sauce, Champignon-Steinpilz Cremesuppe; Fit2go Topfennockerl mit Erdbeersauce; myProduct Little Lunch Bio Gulaschsuppe 6er; Gurkerl Gissinger Schinkenrollen, Iglo Brezel Fischstäbchen, M&S Battered Haddock.
- Online rows (bofrost/Fit2go/myProduct) belong to online_mealprep.csv, not data.json rows; deduped against data.json (case-insensitive store), T17/T18 staged files and online_mealprep.csv.
- Skipped: followfood Kabeljau (shop nutrition implausible, protein 0.9 g), Ben's Express / M&S Rice & Veg (sides), Auinger Klare Suppe (concentrate, salt 50 g), bofrost chocolates/Rotkrautknödel/Pfannengemüse/Putenrolle/Brioche, Penny (no nutrition/EAN, raw or multi-variety), Hofer Flammkuchen (no price), denn's offer (no size), Alfies (no 4020 delivery).
- Goal of 20 not reached: all Gurkerl meal categories now fully fetched (rest is components); spar-shop, gourmetfein, prepmymeal, livefresh, every had 0 new rows; adeg, bio-kistl, foodora-market, unimarkt-shop returned 0 products.

### hourly 2026-10-24T20

No file staged (0 new rows). Fresh fetches of billa, dm, mpreis-shop, juit, loewenanteil, kernbeisser, goldblatt, issmich, adamah, gerbl, ruckzuck, penny-shop, hofer-shop, gourmet-daheim and subway-at, deduped against data.json, all staged_*.json files and fertiggerichte-daten online_mealprep.csv (by EAN, URL and name):
- 0 new from adamah, dm, gerbl, goldblatt, gourmet-daheim, issmich, juit, kernbeisser, loewenanteil, ruckzuck.
- BILLA 53 "new" are all ingredients, soup bases, sauces, baby jars, spreads or dry pasta (search-term hits for Lasagne/Curry/Bolognese/Suppe); none are heat-up meals.
- MPreis shop 18 "new" in the Fertiggerichte category are tofu, vegan cold cuts, fresh pasta, potato mash, Spätzle and pudding powder; the only meat item (AIA Geflügel Cordon Bleu) is a component, skipped like PICARD Cordon Bleu.
- Penny 27 are multi-variety offers or raw meat without EAN/nutrition (skipped per earlier rule); Hofer 4 are non-food or without price; Subway is a restaurant (not staged).
- Goal of 20 not reached: the live connector sources are exhausted for now; new rows need a new store/connector (Daten-Squad lead: shopbio.at jar 6-packs vs iss mich).

- 2026-10-24T2111 Daten-Squad: new online store **Wiesbauer Gourmet webshop** — 20 rows 'Online: Wiesbauer Gourmet' added directly to fertiggerichte-daten data/online_mealprep.csv (daten 6ea27f8, connector food-connectors d5f1b52 `wiesbauer_gourmet`); nothing staged here, pick up from the daten CSV on the next merge.

### hourly 2026-10-24T21

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-24T21.json | Online: Bauernladen.at (food-connectors `bauernladen`), denn's BioMarkt (`denns` offers) | 7 | meal 6, soup 1 | open |

- Rows: Dunzingers Ruck Zuck at Bauernladen.at — Erdäpfel Gulasch VEGAN 330 g 7,60 €, Curry vegan 350 g 8,40 €, Gemüse Linsen Eintopf VEGAN 360 g 8,40 €, Gulasch vom Österreichischen Rind 315 g 9,20 €, Ragout vom Rind 370 g 9,90 € (store-specific rows; similar dishes exist under "Online: Ruck Zuck Laden (Dunzinger's)" in online_mealprep.csv); Bio Galloway Hof Kerschbaumlehen Rindsbeuscherl 1000 g 36,00 €; denn's Biopolar Bio-Pizza Margherita 310 g 3,79 € (weekly offer price only). All with shop photo, none with nutrition or GTIN.
- Online Bauernladen rows belong in online_mealprep.csv, not data.json rows. Deduped against data.json, all staged_*.json and fertiggerichte-daten online_mealprep.csv by EAN, URL and normalized name.
- Skipped: Danke Bauer Schweinsbraten 2 Scheiben (meat component without side), denn's Currysauce/Antipasti/Strudelteig (not meals), NaBio "Eintopf oder Suppe" (multi-variety offer, no size).
- 0 new from fittogo, draxler, sperchenedergut, wagyuhof, wiesbauer_gourmet; myproduct and bofrost timed out after 240 s (retry next run with a smaller limit).
- Goal of 20 not reached: existing connectors stay exhausted; new rows need new stores (Daten-Squad).

### hourly 2026-10-24T23

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-24T23.json | SPAR/INTERSPAR (food-connectors `spar-shop`) | 5 | meal 4, stew 1 | open |

- Rows: SPAR Feine Küche Paprika-Huhn mit Eierspätzle 400 g 4,99 € (chilled); S-BUDGET Fusilli mit Käsesauce 1,39 €, S-BUDGET Fusilli mit Tomatensauce 1,39 €, S-BUDGET Penne mit Pilzsauce 1,39 € (dry pasta-in-sauce packs); Knorr Kaiser Teller Kartoffeltopf mit Bohnen und Speck 1,59 € (store-specific row, BILLA has the same product). Shop photos for all; no nutrition, no GTIN; size_g null for the 4 dry packs because the SPAR API gives no pack size.
- Deduped against data.json (EAN, URL, normalized name and SPAR article id in raw JSON), all staged_*.json and fertiggerichte-daten online_mealprep.csv. Most SPAR "new" names were renamed duplicates of existing rows (Inzersdorfer soups, Johanna Maier Tomatensuppe/Topfen-Spätzle, Asia Noodles).
- Skipped: SPAR PREMIUM Ravioli Bufala (fresh pasta, raw), hummus, baguettes, Blätterteig, Eierspätzle, Kokosflocken; Gurkerl 8 (sides, sauces, meat components, all rejected before); bofrost Putenrolle, Rotkrautknödel, chocolates. Lidl returned 0 products; myproduct timed out again after 300 s at --limit 80.
- Goal of 20 not reached: live connector sources stay exhausted; new rows come from new stores (Daten-Squad).

### hourly 2026-10-25T00

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-25T00.json | Alfies (food-connectors `alfies`, --limit 30) | 4 | meal 2, soup 2 | open |

- Rows: Iglo Paprikahuhn mit Spiralen 350 g 5,99 € (TK), Iglo Risibisi mit Huhn 330 g 3,99 € (TK; BILLA has it as "Iglo Tagesteller Risibisi mit Huhn"), Knorr Bitte zu Tisch Nudelsuppe 1,19 € (BILLA has the same product), Knorr Kaiser Teller Frittatensuppe 1,69 €. All store-specific Alfies rows with shop photo and nutrition per 100 g as published by alfies.at; no GTIN; size_g null for the two Knorr soups.
- Deduped against data.json, all staged_*.json and fertiggerichte-daten online_mealprep.csv by EAN, URL and store+normalized name.
- Skipped: Land Leben Frittaten (soup insert, component); Nah&Frisch weekly offers iglo Mehlspeistraum Süße Knödel and Knorr Bitte zu Tisch Suppen (multi-variety offer tiles, no size; price OCR partly unreadable) and Goldaugen Suppenwürfel (soup base); PrepMyMeal 32 "new" are bundles, sets, Body-Challenge passes, Müsli and Whey, plus a renamed URL of the existing Hähnchen im Kokosmantel.
- 0 new from biohof-achleitner (13), steiramarkt (22), livefresh (10); heisse-preise returned 0; myproduct --limit 30 finished but had 0 new; alfies and myproduct time out at --limit 300 (240 s), so keep small limits.
- Goal of 20 not reached: live connector sources stay exhausted; new rows keep coming from new online stores (Daten-Squad, e.g. Deflorian 27 rows added directly to online_mealprep.csv at 2026-10-25T0006).

### hourly 2026-10-25T01

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-25T01.json | PENNY (food-connectors `penny` / `penny-shop` weekly offers) | 2 | dessert 1, snack 1 | open |

- Rows: BÄCKERKRÖNUNG Mohnnudeln 500 g TK 1,99 € (offer 2026-10-22 to 10-28, standard price 2,49 €; other stores carry Iglo/Toni Kaiser Mohnnudeln, this is a different product); PENNY READY Chicken Cheese Burger 320 g 1,99 € (chilled heat-up burger, offer valid 2026-10-29 to 11-04, origin Deutschland; tagged snack, the Orchestrator may decide whether it belongs in meal rankings). Shop photos for both; no nutrition, no GTIN.
- Deduped against data.json (case-insensitive store + normalized name, EAN, URL), all staged_*.json and fertiggerichte-daten online_mealprep.csv. BILLA Inzersdorfer Rindsgulasch 800 g, BILLA Lasagne Bolognese and Iglo Lasagne al Forno were already in data.json as store "Billa" (the connector writes "BILLA", so a case-sensitive store match gives false positives).
- Skipped: dry lasagne sheets, Gulaschsaft/soup cubes, curry spices and spreads (BILLA search hits); Gourmetfein 60 (sausages, Leberkäse, ham, no meals); MPreis "Fertigmenüs" hits (tofu, vegan cold cuts, Cordon Bleu component, Eierspätzle, pudding powder); HOFER (bird feed, pan, Flammkuchen without price); PENNY multi-variety offers (Bitte zu Tisch Suppen, Kaiserteller od. Schnelle Feine, Meisterkessel Suppen, Pfannengerichte, Cevapcici od. Pljeskavica), raw meat, sides.
- 0 new from juit, issmich, adamah, dm, gerbl, suppito, loewenanteil, goldblatt, ruckzuck, kernbeisser, gourmet-daheim (all fetched fine at --limit 60, 4 in parallel, ~4 min total).
- Goal of 20 not reached: live connector sources stay exhausted; new rows keep coming from new online stores (Daten-Squad).

### hourly 2026-10-25T02

| file | source | rows | tags | status |
|---|---|---|---|---|
| (none) | 12 rotated connectors | 0 | – | – |

- No staged file this hour: every candidate was a duplicate or not a heat-up meal.
- Fetched at --limit 60 (4 parallel, ~2.5 min, all exit 0): gurkerl 60, mpreis-shop 60, spar-shop 60, bofrost 60, prepmymeal 60, deflorian 27, hofer-shop 21, wiesbauer_gourmet 20, voeslauermanufaktur 13, draxler 9, denns 5, lomoalto 3.
- The 22 "new" spar-shop rows were all already in data.json as store "Spar": the connector writes store "SPAR/INTERSPAR" and URLs like interspar.at/shop/lebensmittel/<slug>/p/<id>, while data.json has interspar.at/p/<id>. Dedupe SPAR by the trailing article id, not by store name or full URL (Reisfleisch, Schinkenfleckerl, Fleischbällchen mit Kartoffelpürree, S-BUDGET Gefüllte Paprika, Kärntner Kasnudeln, Johanna Maier Tomatensuppe/Topfen-Spätzle, Asia Noodles Gemüse all present).
- Skipped again: Gurkerl 7 (Speckkraut, Gabelkraut, Rotkraut, Sauerkraut, Rahmfisolen, Frittaten, Bedford Hähnchenbrust; sides and components), bofrost 3 (Putenrolle, Rotkrautknödel, Feine Trüffel), MPreis 8 (tofu, vegan cold cuts, Cordon Bleu, Eierspätzle, pudding powder), HOFER 4 (bird feed, pan, Käsekrainer, Flammkuchen without price), PrepMyMeal 4 (bundles, renamed Hähnchen im Kokosmantel), SPAR non-meals (hummus, baguettes, Blätterteig, Eierspätzle, Kokosflocken, Bruschetta, raw fresh pasta).
- 0 new from deflorian, wiesbauer_gourmet, voeslauermanufaktur, draxler, denns, lomoalto.
- Goal of 20 not reached: live connector sources stay exhausted; new rows keep coming from new online stores (Daten-Squad).

### hourly 2026-10-25T03

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-25T03.json | Alfies (6), Bauernladen.at (1) | 7 | main 2, dessert 1, snack 3, main-component 1 | open |

- Rows: Alfies Mama Lucia Lasagne Bolognese 1 kg 5,49 € (TK; first Mama Lucia row), Followfood Pizza Gamberi Bio 293 g 5,89 € (TK), Iglo Powidltascherl 410 g 5,39 € (TK dessert; no Powidltascherl in data.json yet), Iglo Hühner Flügerl 580 g 8,99 €, Iglo Green Cuisine Gemüse Stangerl 360 g 5,19 € and Süßkartoffel Laibchen 270 g 4,79 € (snack); Bauernladen.at Danke Bauer Schweinsbraten 2 Scheiben 190 g 7,90 € (meat without side, tagged main-component for the Orchestrator to decide). Shop photos for all; Alfies nutrition per 100 g as published, no GTIN.
- QA: Alfies Hühner Flügerl kcal 862 looks like kJ (macros give about 205 kcal), so kcal is null; Mama Lucia salt 0.0 is implausible, so salt is null. Notes are in extra.qa_note.
- Skipped: BILLA 23 (Gulaschsaft and soup cubes, dry lasagne sheets, curry spices, spreads and salads), Alfies Land Leben Frittaten (soup insert) and Wiesbauer Nockerl spezial (side), every. 5 (no AT delivery, unrankable per Orchestrator).
- 0 new from fittogo 32, livefresh 10, buchberger 5, kumitzberg 5, wagyuhof 4, fichtenbauer 3, diechtl 1, thaller 1 (fetched at --limit 60, 4 parallel, ~3 min, all exit 0).
- Goal of 20 not reached: live connector sources stay exhausted; new rows keep coming from new online stores (Daten-Squad).

### hourly 2026-10-25T04

| file | source | rows | tags | status |
|---|---|---|---|---|
| (none) | 12 rotated connectors | 0 | – | – |

- No staged file this hour: every candidate was a duplicate, a multi-variety offer, raw meat, a side or a non-meal.
- Fetched (4 parallel, ~5 min, all exit 0; myproduct at --limit 30, rest at --limit 60): billa 60, bauernladen 51, penny 31, subway-at 29, penny-shop 27, steiramarkt 22, biohof-achleitner 13, jenichl 11, myproduct 11, bernos 4, nah-frisch 3, lidl 0 (known upstream 401/HTTPError).
- Skipped: BILLA 23 again (Gulaschsaft and soup cubes, dry/fresh lasagne sheets, curry spices, spreads and salads); PENNY Gustavo Gusto Amore Pizza 320 g 3,29 € (multi-variety "Salame od. Mozzarella" offer valid 2026-11-02 to 11-04; Amore Napoli Salame/Mozzarella already in data.json via Billa/Gurkerl/MPreis), Gustoria Snack-Sortiment and Pfannengerichte, Knorr Snackbecher, Bitte zu Tisch, Kaiserteller (multi-variety), Mini-Fleischlaibchen mit Käse 400 g (Fleisch category, not verifiable as cooked; no nutrition), raw meat, Onion Rings (side), pans and kitchen tools; Nah&Frisch offer tiles (multi-variety, no size); Subway (restaurant, not staged).
- 0 new from bauernladen, steiramarkt, biohof-achleitner, jenichl, myproduct, bernos.
- Goal of 20 not reached: live connector sources stay exhausted; new rows keep coming from new online stores (Daten-Squad).

### hourly 2026-10-25T05

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-25T05.json | Alfies (28) | 28 | main 22, main-component 1, snack 5 | open |

- Rows: Rex Eat Kichererbsencurry mit Reis, Paprikahendl mit Spätzle, Cannelloni Tomate-Ricotta, Cannelloni alla Bolognese, Krautfleckerl (400 g, 9,90–11,90 €; first Rex Eat rows); Radatz Veggie Chili sin Carne 1,2 kg 9,99 €; Every Foods Green Dal, Pumpkin Pasta, Green Boost, Naked Taco, Oriental Bulgur (TK 450 g 8,99 €, Alfies offers); getvoila Grünes Täschle, Bella Cannellona, Neapolitanische Pizza vegetarisch; Rana Korean Style BBQ Noodles mit Rind and Thai Gelbes Curry Chicken mit Reis; pizzas (Followfood Spinaci e Feta, Die Protein Pizza Salami and Margherita, Ronca Pinsa Margherita and Salamino, Dr. Oetker La Mia Pinsa Mozzarella); Wiesbauer Gourmet Hirschgulasch sous vide 300 g (main-component, no nutrition); snacks Kirn Elsässer Quiche Lachs/Lorraine/Lauch, Ajinomoto Gyoza Chicken & Vegetable, Bibigo Gyoza Tofu & Gemüse. Shop photos, ingredients and per-100 g nutrition as published for all except Hirschgulasch; no GTIN.
- Found by fetching alfies at --limit 400 (299 rows, ~7 min, exit 0): the usual --limit 60 only ever sees the first 60 items, so items 61–299 had never been diffed. Deduped against data.json by name and by Alfies URL slug without the trailing -N (34 hits by slug only).
- QA: Every Foods Green Boost kcal 558 is a per-portion value (macros give about 129 kcal), so kcal is null; Kirn Quiche Lachs and Lorraine show identical nutrition on Alfies (flagged in qa_note). Alfies reported hasAvailableStock=false for 298 of 299 items at fetch time (Sunday early morning snapshot), noted per row; Alfies does not deliver to 4020, so rows stay unrankable anyway.
- Skipped from the Alfies tail: dry/instant products (Knorr Spaghetteria, Kaiser Teller, Cup a Soup, Pho, Miso, Maggi Quick Snack and Asia Beutel, Feel Food 85 g packs, Ashoka), sides and components (Spätzle, Schupfnudeln, Gnocchi, Lasagneblätter, Pommes, Kochsalat, Baked Beanz, Fleischlaibchen, Wings, Nuggets, Patties, Fischstäbchen), cold wraps, Aumaerk sous-vide meat cuts (meat only, 13,90–39,90 €), smoothies, Blinis, aperitif bites, Camembert, Rana fresh ravioli.
- Rotated --limit 60 batch (adamah, dm, gerbl, scheffknecht, suppito, loewenanteil, goldblatt, ruckzuck, kernbeisser, gourmet-daheim, juit, issmich; 4 parallel, ~4.5 min, all exit 0) gave 0 new. Note: online stores (ADAMAH, Gerbl, Suppito, Ruck Zuck, Scheffknecht, GOURMET Daheim) live in fertiggerichte-daten/data/online_mealprep.csv, not data.json, so dedupe against both or they all look new.
- Goal of 20 reached this hour (28), all from the Alfies tail; next idea: fetch other connectors with a high limit too (gurkerl, billa, spar-shop) in small batches when the box is idle.

### hourly 2026-10-25T06

| file | source | rows | tags | status |
|---|---|---|---|---|
| staged_2026-10-25T06.json | gurkerl | 5 | main-component 5 | staged, not merged |

- Rows: Wegschaider Haschee Knödel, Grammel Knödel and Speck Knödel (400 g, 4,59 €, GTIN, ingredients; nutrition for Grammel and Speck; the Haschee values published by the shop are implausible (carbs 1 g, saturated fat equal to fat 6 g), so they are kept only in extra.published_nutrition_suspect); Gissinger Grammelknödel 210 g 4,49 € and Wurstknödel 210 g 3,69 € (ingredients, no nutrition published; the Wurstknödel code 211… is an in-store code, not a GTIN, so ean is null). All are pre-cooked filled Knödel from Kühlregal > Schnelle Küche > Knödel, Spätzle & Co, which the Hourly Fertiggerichte sweep had never walked.
- Fetches with 0 new meals: gurkerl all meal categories (553 rows at --limit 1000), billa 135, spar-shop 202, mpreis-shop 155, hofer-shop 21, bofrost 60, leitgeb 29, nudlkudlmudl 7, Gurkerl search sweep over 43 stems (958 rows). Everything was a duplicate, a side, a sauce, raw food, baby food or an item rejected in earlier hours. Store ids are mpreis-shop and hofer-shop (mpreis and hofer are invalid).
- Skipped: Spätzle, Schupfnudeln, Nockerl, Knödel and potato doughs, Polentarolle, plain Gissinger Waldviertler Knödel (sides); Gurkerl sous-vide meat cuts (Wech chicken wings, duck fillet and legs, goose legs, Nemetz Surstelze, Wiesbauer Beef Ribs, Windisch Porchetta 2,3 kg), meat only, as in T05; Wiesbauer Mediterrane Schweinebacken sous vide (no ingredients or nutrition published, unclear whether sauced).
- Goal of 20 not reached (5). Next idea: walk the remaining Gurkerl Kühlregal > Schnelle Küche subcategories (Kochboxen 137493 are kits, Salate & Bowls 989 are cold) and Tiefkühl Knödel 606 for filled varieties not yet in data.json.
- No export, commit, push or deploy from fertig or fertig-app.
