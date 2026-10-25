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
