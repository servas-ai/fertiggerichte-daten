# Datensatz-Richtlinien

1. **Nur echte, verifizierte Daten.** Keine geschätzten, generierten oder „plausiblen“ Werte. Fehlt ein Wert, bleibt das Feld leer.
2. **Herkunft pro Feld.** Jede Zeile nennt ihre Quelle (`source`, `price_source`, `sources`) und das Abrufdatum (`fetched_at`). Registry-Treffer tragen `gleif_match_score`; nur Treffer ≥ 0,75 werden übernommen, sonst `registry_status=not_found_in_gleif`.
3. **Erlaubte Quellen:** offizielle Register (GLEIF, Firmenbuch HVD, EU VIES, Handelsregister), Statistik Austria/ÖVIS, Händler-Onlineshops (öffentliche Produktseiten), Herstellerwebsites, Open Food Facts, heisse-preise.io, OpenStreetMap (Overpass, ODbL), Presse mit Link.
4. **Nutzungsbedingungen respektieren.** Rate-Limits (≥1 s zwischen Requests, Backoff bei 429), keine Umgehung von Bot-Schutz, kein Login-Scraping. North Data nur öffentliche Einzelseiten oder offizielle API mit Key.
5. **Personendaten:** nur Geschäftsführung/Eigentümer aus öffentlichen Registern, keine Privatadressen.
6. **Aktualisierung:** stündlicher Lauf exportiert neu (`scripts/export.py`), Firmendaten täglich (`companies_enrich.py`). Vor jedem Push muss `scripts/validate.py` grün sein.
7. **Lizenz:** eigene Zusammenstellung CC BY 4.0 („Fertiggerichte-Daten, servas-ai“). Daten aus Open Food Facts bleiben unter ODbL 1.0 (Share-Alike, Namensnennung), **Filialdaten in `data/stores.*` © OpenStreetMap contributors, ODbL 1.0**, GLEIF CC0, Händler-Preise/Fotos sind Fakten bzw. verlinkt, nicht weiterlizenziert.
8. **Beiträge:** PR mit Quelle pro geändertem Wert; `validate.py` muss durchlaufen.

## Supplemental rows and raw crawls

- `data/supplemental/{products,prices,nutrition}.json` hold rows that are not (yet) part of the app build, e.g. MPreis
  live-shop rows (food-connectors `mpreis-shop`) and Unimarkt rows from the heisse-preise.io dump. `scripts/export.py`
  re-appends them on every refresh (deduped by `product_id` and chain+name), so hourly refreshes never drop them.
- `raw/` keeps the unfiltered connector output a supplemental table was derived from (e.g. `raw/mpreis_shop_crawl_2026-10-13.json`).
- Stale dump rows are replaced once a live source exists: on 2026-10-13 the 149 MPreis rows from the 2023/2024
  heisse-preise dump were replaced by 101 live-verified MPreis webshop rows (only 52 of the old rows still exist in the shop sitemap).
- Export applies a nutrition plausibility gate (macros ≤ 100 g/100 g, salt ≤ 30 g, kcal ≤ 900); failing rows are dropped, not corrected.
