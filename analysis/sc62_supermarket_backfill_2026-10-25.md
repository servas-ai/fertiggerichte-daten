# Sensecheck 62 – P1 (P1b + P1a), P2 (P2a + P2b), P3 & Verified Supermarket Backfills (2026-10-25)

- **Baseline (`SC62_FIXES=0`)**: `dataVersion = b5508366fdef`, `rankable = 169`, `rankableLight = 94`
- **SC62 (`SC62_FIXES=1`)**: `dataVersion = 4644adb26ffa`, `rankable = 186` (+17), `rankableLight = 105` (+11)

## Summary of Changes
1. **P1b (Rescue Real Complete Meals from `stage in ('base', 'side', 'veg')` Before P1a)**:
   - Added `lasagne|auflauf|gratin|tikka|mediterran` to the `raw` exclusion regex in `export_app.py` (line 120) and included `'linz_providers_src.json'` in the `MEALPREP_ONLY` check (line 144).
   - Upgraded 30 verified complete meals in `_reconcile_sc48`:
     - Newly `rankable = True` (+4): `#23` Billa Iglo Lachs-Spinat-Lasagne (`PLI 32.5`), `#3050` bofrost Lachs-Lasagne (`PLI 26.4`), `#3668` FitTaste hähnchen tikka masala (`PLI 35.1`), `#3037` bofrost Moussaka Kartoffelauflauf (`PLI 30.2`).
     - Newly `rankableLight = True` (+5): `#3660` FitTaste hähnchen mediterran (`pliLight 28.7`), `#3662` FitTaste hähnchengeschnetzeltes (`pliLight 32.6`), `#3672` FitTaste hähnchen kürbis-erdnuss (`pliLight 32.8`), `#35` Billa Schär glutenfreie Lasagne (`pliLight 26.9`), `#2119` Billa Iglo Fisch'n"Rösti (`pliLight 33.5`).
2. **P2a & P2b (Linz Complete Meals Falsely Blocked as `component=True` or `multi_portion`)**:
   - **P2a (`rankable = True`, +7)**: `#626` Billa Omis Schmankerl Kalbsbutterschnitzel (`PLI 43.6`, #2 in Linz local Top-10!), `#938` Billa Inzersdorfer Zwiebelrindsbraten (`PLI 27.6`), `#922` Billa & `#2777` Spar Inzersdorfer Champignonschnitzerl mit Gemüsereis (`PLI 23.8`), `#400` Billa Iglo Faschierte Laibchen (`PLI 30.4`), `#598` Billa Backhendl Bowl (`PLI 29.0`), `#3151` Goldblatt Chili con Tempeh (`PLI 35.9`).
   - **P2a (`rankableLight = True`, +3)**: `#612` Billa Omis Schmankerl Cevapcici Letscho (`pliLight 36.0`), `#614` Billa Omis Schmankerl Surbraten (`pliLight 28.0`), `#605` Billa Simply Good Kichererbsencurry mit Tofu (`pliLight 24.0`).
   - **P2b (`rankable = True`, +5)**: 800-g 2-Portionen cans (`portion = 400 g`): `#495` Spar (`PLI 37.0`) & `#1033` Billa (`PLI 35.3`) Inzersdorfer Linsen mit Speck, `#2257` Spar Felix Linsen im Speck (`PLI 37.4`, with `#1031` Billa demoted as cross-store twin), `#395` Billa Felix Chili Con Carne (`PLI 34.4`), `#397` Billa Felix Höllenfeuer Chili Con Carne (`PLI 36.1`).
3. **P1a (Sync All Remaining `stage in ('base', 'side', 'veg')` Rows)**:
   - Every remaining row with `stage in ('base', 'side', 'veg')` now has `component = True`, `meal_class = 'raw_ingredient'` (for `base`) or `'snack_side'` (for `side`/`veg`, preserving `'dry'/'baby'/'drink'/'dessert'`), `meal_check['ok'] = False`, and `rankable = rankableLight = False`. Zero raw meats (`#1323`, `#3362`), canned beans (`#529, #579, #582, #596, #597, #643`), or sides remain with `meal_class == 'meal'` or `'light_meal'`.
4. **P3 Data Hygiene & Verified Supermarket Nutrition Backfills**:
   - Fixed `#2878` LiveFresh Tikka Masala – Vegane Bowl `fat: 0.5 -> 5.0`.
   - Fixed 10× decimal-shifted macros/salt on `#3265, #3282, #3317, #3357, #810, #833, #3470, #1426` and set `meal_class = 'dry'` on `#199, #246, #1379`.
   - Backfilled `#453` Spar Youcook Tikka Huhn India Style (`rankable = True, PLI 31.9`), `#2663` Spar Inzersdorfer Bohnensuppe (`score 32.7`), `#496` Spar Inzersdorfer Paprikahendl (`score 35.1`), `#102` Spar Inzersdorfer Suppentopf Bohnensuppe 12 Portionen (`score 28.7`), `#1091` Spar Süsskartoffel-Eintopf Vegan (`rankableLight = True, pliLight 18.9`), `#51` & `#52` Spar BEN's ORIGINAL Express Risotto (`rankableLight = True, pliLight 25.5 / 23.3`), `#2660`, `#2765`, `#502, #2750, #2761, #121, #2762, #3492-#3494`, and same-store Spar/Billa twins (`#212/#1471, #1087/#185, #1091/#240, #1092/#237, #235/#3411, #236/#3439, #1125/#1370, #1399/#1005`).
