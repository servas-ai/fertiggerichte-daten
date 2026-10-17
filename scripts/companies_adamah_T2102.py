"""Daten-Squad 2026-10-17T2102: operator company row + store logo row for the new store ADAMAH BioHof (ADAMAH Vertriebs GmbH,
Glinzendorf). Sources fetched this run: evi.gv.at/f/554551t (Firmenbuch publication: FN, Sitz, Eintragungsdatum, Rechtsform,
Stammkapital, Geschäftszweig, GF, Gesellschafter), EU VIES REST (ATU76911656 valid, name + address), GLEIF fulltext 'adamah'
(no AT record), adamah.at/AGB + Impressum mirror (FN + UID as printed). Logo: adamah.at /assets/icon/app_logo-192x192.png
(official shop icon = 'ADAMAH BioHof' wordmark on a green leaf; robots Allow: /; vision gate PASS, unmodified). Idempotent."""
import json, csv
SLUG = "adamah-vertriebs-gmbh"
row = {"slug": SLUG, "name": "ADAMAH BioHof (ADAMAH Vertriebs GmbH)", "role": "retailer", "legal_name": "ADAMAH Vertriebs GmbH",
       "lei": None, "register_id": "554551t", "register_authority": "RA000017", "fn": "FN 554551t", "legal_form_code": None,
       "country": "AT", "address": "Sonnenweg 11, 2280 Glinzendorf, AT", "entity_status": "Firmenbuch eingetragen (evi.gv.at); no GLEIF record",
       "parent_direct": "Zoubek Beteiligungs GmbH (Gesellschafter/in lt. evi.gv.at)", "parent_ultimate": None,
       "founded": "2021-05-15", "owners": "Zoubek Beteiligungs GmbH (1 Gesellschafter/in lt. Firmenbuch/evi.gv.at, eingetragen 15.05.2021)",
       "management": "Elisabeth Zoubek (Geschäftsführerin lt. Firmenbuch, vertritt seit 27.07.2021)", "employees": None, "revenue": None,
       "website": "https://www.adamah.at", "brands": ["ADAMAH BioHof", "ADAMAH"], "chains": ["ADAMAH BioHof"], "product_count": 27,
       "median_price_eur": 10.6, "median_eur_per_10g_protein": None, "fetched_at": "2026-10-17T21:31:30Z",
       "registry_status": "verified_vies_firmenbuch (VIES name+address match; FN on AGB/Impressum = evi.gv.at; no GLEIF record)",
       "uid": "ATU76911656", "uid_vies_name": "ADAMAH Vertriebs GmbH", "uid_vies_address": "Sonnenweg 11, AT-2280 Glinzendorf",
       "uid_checked_at": "2026-10-17T21:31:25Z", "imprint_url": "https://www.adamah.at/Impressum", "register_court": "Landesgericht Korneuburg",
       "founded_source": "Firmenbuch Eintragungsdatum 15.05.2021 (evi.gv.at/f/554551t) — legal entity; the farm brand ADAMAH BioHof exists since 1997 (Unternehmensangabe)",
       "share_capital": "EUR 35 000 (lt. evi.gv.at)", "nace": "Einzel- und Großhandel mit biologischen Lebensmitteln (Geschäftszweig lt. Firmenbuch)",
       "sources": ["https://www.evi.gv.at/f/554551t", "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/AT/vat/U76911656", "https://www.adamah.at/AGB"]}
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
LOGO = {"slug": "adamah", "name": "ADAMAH BioHof", "category": "Handelskette", "file": "logos/adamah.png",
        "source_url": "https://www.adamah.at/assets/icon/app_logo-192x192.png (official shop icon/wordmark; robots Allow: /; vision gate PASS)",
        "brands": ["ADAMAH BioHof", "Online: ADAMAH BioHof", "ADAMAH Vertriebs GmbH", "ADAMAH BioHof (ADAMAH Vertriebs GmbH)", "ADAMAH", "adamah.at"]}
L = "data/logos.json"
ls = [r for r in json.load(open(L)) if r["slug"] != LOGO["slug"]]; ls.append(LOGO)
json.dump(ls, open(L, "w"), ensure_ascii=False, indent=1)
LC = "data/logos.csv"
cur = list(csv.DictReader(open(LC, encoding="utf-8"))); cols = list(cur[0].keys())
cur = [r for r in cur if r["slug"] != LOGO["slug"]]
with open(LC, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur); w.writerow({**LOGO, "brands": "|".join(LOGO["brands"])})
ev = {"run": "2026-10-17T2102 Daten-Squad", "company": row, "logo": LOGO, "vies": json.load(open("/tmp/vies_adamah.json")),
      "gleif_fulltext_query": "adamah", "gleif_hits": ["894500V454VHD7KV3P06 ADAMAH, Grenoble FR (unrelated)"],
      "evi_extract": {"Firmenbuchnummer": "554551t", "Adresse": "Sonnenweg 11, 2280 Glinzendorf", "Eintragungsdatum": "15.05.2021",
                      "Rechtsform": "Gesellschaft mit beschränkter Haftung", "Stammkapital": "EUR 35 000", "Stichtag Jahresabschluss": "30.6.",
                      "Geschäftszweig": "Einzel- und Großhandel mit biologischen Lebensmitteln", "Geschäftsführer/in": "1 Person (Elisabeth Zoubek, seit 27.07.2021)",
                      "Gesellschafter/in": "1 Person (Zoubek Beteiligungs GmbH, eingetragen 15.05.2021)"}}
json.dump(ev, open("raw/companies_adamah_2026-10-17T2102.json", "w"), ensure_ascii=False, indent=1)
print("companies", len(d), "logos", len(ls))
