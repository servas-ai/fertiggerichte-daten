"""Daten-Squad 2026-10-17T0502: company row for the new store Biohof Achleitner (Achleitner Biohof GmbH, Eferding).
Sources (all fetched this run): biohof.at/impressum (FN, court, UID, GF), EU VIES REST (UID valid, name+address),
GLEIF API (LEI by fulltext; registeredAs = FN), evi.gv.at/f/154057f (official Firmenbuch publication page: Eintragungsdatum,
Stammkapital, Geschäftszweig, Gesellschafter — natural persons counted, not named). Idempotent (replaces slug)."""
import json, csv, datetime
SLUG = "achleitner-biohof-gmbh"
NOW = "2026-10-17T05:10:00Z"
row = {"slug": SLUG, "name": "Biohof Achleitner (Achleitner Biohof GmbH)", "role": "producer", "legal_name": "Achleitner Biohof GmbH",
       "lei": "529900GY1B6OGAMV9D95", "register_id": "154057f", "register_authority": "RA000017", "fn": "FN 154057f", "legal_form_code": None,
       "country": "AT", "address": "Unterm Regenbogen 1, 4070 Eferding, AT", "entity_status": "ACTIVE (GLEIF; LEI ISSUED; Firmenbuch eingetragen)",
       "parent_direct": None, "parent_ultimate": None, "parent_ultimate_lei": None,
       "founded": "1996-12-23", "owners": "1 natürliche Person (Gesellschafter/in lt. Firmenbuch/evi.gv.at, eingetragen 29.12.2023)",
       "management": "Andreas Achleitner (Geschäftsführer lt. Impressum und Firmenbuch)", "employees": None, "revenue": None,
       "website": "https://www.biohof.at", "plants": [], "approval_codes": None, "brands": ["Biohof Achleitner", "Hausg'mocht", "Bio-Kulinarium Achleitner"],
       "chains": ["Biohof Achleitner"], "product_count": 13, "median_price_eur": 6.8, "median_eur_per_10g_protein": None,
       "nace": "Handelsgewerbe (Geschäftszweig lt. Firmenbuch); Biokiste-Lieferdienst, Bio-Frischmarkt, Bio-Kulinarium (Küche), Bio-Großhandel, Landwirtschaft (Unternehmensangaben biohof.at)",
       "sources": ["https://www.biohof.at/impressum", "https://ec.europa.eu/taxation_customs/vies/", "https://api.gleif.org/api/v1/lei-records/529900GY1B6OGAMV9D95", "https://www.evi.gv.at/f/154057f"],
       "gleif_match_score": 1.0, "fetched_at": NOW, "chain_product_count": 13,
       "registry_status": "verified_gleif+vies+impressum (Impressum FN 154057f = GLEIF registeredAs; VIES name+address match)",
       "founded_source": "GLEIF legal-entity creationDate 1996-12-22T23:00Z (= 23.12.1996 MEZ); Firmenbuch Eintragungsdatum 15.01.1997 (evi.gv.at/f/154057f)",
       "share_capital": "EUR 40 000 (lt. evi.gv.at)", "register_status": "Eingetragen", "register_entry_date": "1997-01-15", "register_court": "Landesgericht Wels",
       "imprint_url": "https://www.biohof.at/impressum", "uid": "ATU41942706", "uid_vies_name": "Achleitner Biohof GmbH",
       "uid_vies_address": "Unterm Regenbogen 1, AT-4070 Eferding", "uid_checked_at": "2026-10-17T05:09:50Z",
       "gleif_ultimate_parent_exception": "NO_KNOWN_PERSON"}
P = "data/companies.json"
d = [r for r in json.load(open(P)) if r["slug"] != SLUG]; d.append(row)
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
C = "data/companies.csv"
cur = list(csv.DictReader(open(C, encoding="utf-8"))); cols = list(cur[0].keys())
cur = [r for r in cur if r["slug"] != SLUG]
out = {c: row.get(c) for c in cols}
out["brands"] = "|".join(row["brands"]); out["chains"] = "|".join(row["chains"]); out["hrb"] = None; out["plants_count"] = 0
with open(C, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur); w.writerow({k: ("" if v is None else v) for k, v in out.items()})
ev = {"run": "2026-10-17T0502 Daten-Squad", "company": row,
      "vies": json.load(open("/tmp/vies_ach.json")),
      "gleif_fulltext_query": "Achleitner Biohof", "gleif_hits": 1,
      "evi_extract": {"Firmenbuchnummer": "154057f", "Adresse": "Unterm Regenbogen 1, 4070 Eferding", "Sitz": "Eferding", "Eintragungsdatum": "15.01.1997",
                      "Rechtsform": "Gesellschaft mit beschränkter Haftung", "Stammkapital": "EUR 40 000", "Geschäftszweig": "Handelsgewerbe",
                      "Geschäftsführer/in": "1 Person (Andreas Achleitner)", "Gesellschafter/in": "1 Person (natürliche Person; eingetragen 29.12.2023)", "Prokurist/in": "1 Person"},
      "note": "natural-person shareholder counted, not named in owners (dataset rule); GF name is published in the Impressum"}
json.dump(ev, open("raw/companies_achleitner_2026-10-17T0502.json", "w"), ensure_ascii=False, indent=1)
print("companies", len(d))
