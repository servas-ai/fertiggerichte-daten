# Datensatz-Richtlinien

1. **Nur echte, verifizierte Daten.** Keine geschätzten, generierten oder „plausiblen“ Werte. Fehlt ein Wert, bleibt das Feld leer.
2. **Herkunft pro Feld.** Jede Zeile nennt ihre Quelle (`source`, `price_source`, `sources`) und das Abrufdatum (`fetched_at`). Registry-Treffer tragen `gleif_match_score`; nur Treffer ≥ 0,75 werden übernommen, sonst `registry_status=not_found_in_gleif`.
3. **Erlaubte Quellen:** offizielle Register (GLEIF, Firmenbuch HVD, EU VIES, Handelsregister), Statistik Austria/ÖVIS, Händler-Onlineshops (öffentliche Produktseiten), Herstellerwebsites, Open Food Facts, heisse-preise.io, OpenStreetMap (Overpass, ODbL), Presse mit Link.
4. **Nutzungsbedingungen respektieren.** Rate-Limits (≥1 s zwischen Requests, Backoff bei 429), keine Umgehung von Bot-Schutz, kein Login-Scraping. North Data nur öffentliche Einzelseiten oder offizielle API mit Key.
5. **Personendaten:** nur Geschäftsführung/Eigentümer aus öffentlichen Registern, keine Privatadressen.
6. **Aktualisierung:** stündlicher Lauf exportiert neu (`scripts/export.py`), Firmendaten täglich (`companies_enrich.py`). Vor jedem Push muss `scripts/validate.py` grün sein.
7. **Lizenz:** eigene Zusammenstellung CC BY 4.0 („Fertiggerichte-Daten, servas-ai“). Daten aus Open Food Facts bleiben unter ODbL 1.0 (Share-Alike, Namensnennung), **Filialdaten in `data/stores.*` © OpenStreetMap contributors, ODbL 1.0**, GLEIF CC0, Händler-Preise/Fotos sind Fakten bzw. verlinkt, nicht weiterlizenziert.
8. **Beiträge:** PR mit Quelle pro geändertem Wert; `validate.py` muss durchlaufen.
