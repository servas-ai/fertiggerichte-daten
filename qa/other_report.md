# QA report – non-Billa/non-Hofer products

Scope: 631 unique products (scored.json ∪ expand.json, deduped by URL): SPAR ≈ 500, OFF-only/unknown store 75, Fit to Go 24, Lidl 16, dm 13, Penny 2, misc.

## Fixes (qa/other_fixes.json)
- price_eur: 5
- size_g: 5
- is_meal: 34
- store: 138
- dry: 3
- kcal_pack: 1
- kcal_100: 1
- image_url: 1
- price_per_kg: 1

- **store**: OFF "stores" tags (e.g. "Le retour a la terre, biocoop", "Billa, Carrefour…", "Lidl, NORMA", "Merkur") are crowd-sourced and not AT-chain assignments → set to null; Aldi→HOFER; labels normalized (INTERSPAR variants→SPAR, LIDL/Lidl→LIDL, "Fit to Go online"→Fit to Go).
- **is_meal=false** (34): drinks (Reis-Drink), sausages (Wiesbauer Knacker/Käsekrainer/Pastrami/Bergsteiger, Greisinger Puten-Knacker, Gulaschfleisch raw), spices (Kotanyi Curry-Madras, Sonnentor Curry süß, McCormick), dry risotto rice (Gallo, Rapunzel, Saskia, Natur Aktiv), Lebkuchen, hummus, Vegini nuggets, Rauchkarree, Brühen, Couscous, Sauerkraut.
- **dry=true**: Le Gusto Kürbiscreme (337 kcal), Clever Eiermuschel Suppe (306), Le Gusto Knoblauchcreme (379) – powder values; must not be ranked per 100 g.
- **price/size** from heisse-preise Spar ids where they differ.
- **Fit to Go BBQ Chicken Mac & Cheese**: filled size 400 g, 576 kcal/pack, image from fittogo.at.

## Flags (qa/other_flags.json, not fixable from source)
- Spar price last changed : 68
- no image: 378
- no nutrition data: 444
- size_g: 20
- kcal mismatch: 9
- Store unknown (OFF-only product, no verified AT retailer/pri: 75
- Fit to Go: 1
- Missing from dataset but on fittogo: 1
- URL slug says Hühnerfilet/Kichererbsen but page title is Lin: 1

Key points:
- 444 items have no nutrition (mostly Spar expand, Spar blocks product pages) – correctly “nur Preis”.
- 378 Spar items have no image_url (heisse-preise has no images).
- 68 Spar prices last changed before 2026 on heisse-preise → possibly stale or delisted.
- 9 kcal mismatches >15% (see flags; e.g. Steinpilz Risotto Bio Natura 342 kcal with 15 g carbs = OFF data error).
- Dry-pack sizes (Knorr/Maggi soups 57–92 g) make per-pack protein/price per kg misleading.
- All 253 image URLs load (HTTP 200, image/*). Fit to Go images & sizes verified against fittogo.at (all match). Visual match of OFF/Spar photos not individually verified.
- Fit to Go: 5 products on fittogo.at missing from dataset (listed in flags). Pollo Picante size 430 g not confirmed on current page (no Einwaage shown).
- OFF-only items (75) have no price and no verified AT store → recommend dropping from rankings or showing as “Info”.
- Lidl/dm/Penny: no live price source beyond existing dm_live/hofer_lidl; prices not re-verified.