# UI-QA v3: Fertiggerichte-Vergleich (live, 12.10.2026)
Method: headless Playwright (Chromium), all 16 tabs (`#tab=…`) at 1920×1080 and 390×844, full-page captures, plus each Analyse recharts chart on its own. DOM checks covered broken `<img>`, empty recharts, NaN/undefined, horizontal overflow, console errors and HTTP ≥400. The `dist/data.json` data was checked as well.
Screenshots: `qa/render/v3/<tab>_<1920|390>.png`, `analyse_chartNN_<w>.png`. Raw metrics: `qa.json`, `qa2.json`.

## P0 bugs
1. **SPA crash after a redeploy: no ErrorBoundary.** During the run, `assets/Packaging-*.js` returned 404 (a stale chunk after the redeploy). The dynamic import threw, and every later tab (Hersteller, Matrix, Kombi, …) rendered **blank** until a hard reload. Fix in `App.tsx` (lazy imports + `<Suspense>`): wrap it in an ErrorBoundary that calls `location.reload()` once on `ChunkLoadError`/"Failed to fetch dynamically imported module". Optionally keep the old assets on gh-pages (`deploy.sh` should not wipe `assets/`).
2. **Non-food in "Komplettmahlzeit" (stage=meal):** Tupperware 3-BowlSet, Tupperware Everyday Bowl Set, Tupperware Wonderlier Bowl Set, Grand Marnier Cordon Rouge Likör (all Spar). They are not rankable, but they appear in the Alle and Kategorien lists. Fix in the data build (stage classifier): add a non-food blacklist (tupper|likör|cognac|bowl set …).
3. **Knödel, pasta and raw items count as meal:** 180/716 meal+stew items match component patterns. Examples:
   - Leberknödel, Grammel-, Wurst-, Selchfleisch- and Spinatknödel ("4/6/10/12/20 Stück", S-BUDGET, SPAR Feine Küche, Iglo Hausmannskost).
   - Fresh ravioli and tortellini (Cecchin, Rana, Hilcona, Recheis, La Nova, Johanna Maier).
   - Meica Currywurst.
   - **Clever Leberknödel (0,44 €/10 g)** and **Tortelloni Carne** sit right on the Analyse Pareto front.
   Fix: Knödel without a sauce or dish go to `side`/`prot`, plain fresh pasta goes to `side` or `base`. Same stage classifier as above.
4. **Wikimedia state flags are 404** (curl confirms 404). The 6 Bundesland flags (OÖ, NÖ, W, Stmk, K, Vbg) are broken on Hersteller-Seiten, Marken-Matrix and Alle (390). The thumb URLs have the wrong hash paths. Fix: host the flags locally under `public/flags/` (component: flag helper in `components/info.tsx` / `lib.ts`).

## P1: implausible values
- **Kilo prices shown as pack prices:** 26 meal rows have size=1000 and price==ppk. Examples: BILLA Genusswelt Roastbeef Sous Vide 36,99 €, SPAR Natur*pur Bio-Rindsgulasch "ca. 300g" 23,99 €, TANN Rinds-Bratengulasch 21,99 €. The price per portion and per 10 g protein are wrong as a result. Use a "€/kg" flag in the data, or compute the pack price from the actual weight.
- **Multipacks** (Inzersdorfer Suppentopf 12 Portionen 19,99 €; Inzersdorfer Rindsgulasch 10,49 € in the hero Top 8): check the price per pack against the portion count.
- Ja! Natürlich Soja Geschnetzeltes p100=50 g is a dry product. Make sure `dry` is set, otherwise it skews the protein stats.
- Hero Top-8 places #1 and #2 on **4 Diamanten Thunfisch** (canned tuna snack). That's debatable as a "Komplettmahlzeit"; consider moving it to `prot`.
- Brand ranking (Analyse) shows "(ohne Marke)" at rank 10. Hide it, or resolve the brand.
- Store "unbekannt (OFF)" shows up in lists. Filter it out of rankings.
- 327 of 716 meal/stew rows have no logo and 265 have no image. Fall back to the brand initials (already partly there, e.g. "VD", "A").

## P2: UI/labels
- **Verpackungen** (`views/Packaging.tsx`): raw JSON keys are shown as chips (`n_products: 160`, `median_protein_100`, `median_price_per_10g_protein` …). Map them to German labels.
- Verpackungen chart "Mediane je Verpackung": the Pouch/Retort and Unklar bars are empty (n=5, no values). Hide categories without data. Glas €/10 g Protein = 12,82 is an outlier (n=12); clamp it or note it.
- Matrix (`views/Matrix.tsx`): Heiploeg International B.V. (Zoutkamp) has **no flag** (NL missing) because the flag only renders for AT.
- **Horizontal overflow at 390 px:** Kategorien, Marken, Analyse, Läden & Werke, Kombi-Ideen. Charts/tables need `overflow-x-auto` or a responsive width (ResponsiveContainer min-width).
- Sticky tab nav (`App.tsx` nav top-[49px]) covers content mid-page in full-page screenshots. It's fine in normal scrolling, but check the scroll anchors.
- Kombi list: entries read "price · g P · Brand Name", so the brand appears twice (brand chip + name prefix, e.g. "BILLA Immer Gut BILLA Langkornreis"). Strip the brand from the name.

## OK
- No console errors after a fresh load; 0 NaN/undefined in the text; Analyse has 6 recharts, all filled; Verpackungen 6, Läden & Werke 4, Scatter and FtG 1 each, none empty. Leaflet map renders.
