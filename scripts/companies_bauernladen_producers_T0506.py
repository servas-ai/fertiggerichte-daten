"""Daten-Squad 2026-10-18T0506: company rows for the 7 Bauernladen.at producers (T0439 open item 2).
Sources fetched this run: producer Impressum pages, EU VIES REST (AT numbers need the 'U' prefix), evi.gv.at /f/<FN>
(official Firmenbuch publication platform; script scripts/evi_T0506/evi.py, polite 1 req/s), GLEIF fulltext (AT).
Natural-person shareholders are counted, not named (dataset rule); a GF/owner name is only kept where the company's own
Impressum publishes it (management field). +4 new rows, Danke Bauer (existing roman-fenz-eu) gets chain Bauernladen.at,
Venatio = unregistered Einzelunternehmen (no FN/UID published) → impressum-only row; vom Sandriegel publishes no
legal identity (no website/Impressum; Bauernladen page lists only address/phone) → no row. Idempotent."""
import json, csv, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = "2026-10-18T05:12:00Z"
V = {}
for v in ["75453279", "68596628", "69302248", "57151209", "76907224", "63513488"]:
    V[v] = json.load(open(f"/tmp/vies_{v}.json"))
E = json.load(open(f"{R}/scripts/evi_T0506/evi_out.json")); EP = json.load(open(f"{R}/scripts/evi_T0506/evi_parent_out.json"))
def vaddr(v): return V[v]["address"].replace("\n", ", ")
def base(**k):
    r = {"role": "producer", "lei": None, "register_authority": "RA000017", "legal_form_code": None, "country": "AT", "parent_direct": None,
         "parent_ultimate": None, "parent_ultimate_lei": None, "employees": None, "revenue": None, "plants": [], "approval_codes": None,
         "chains": ["Bauernladen.at"], "median_eur_per_10g_protein": None, "fetched_at": NOW, "chain_product_count": None,
         "hrb": None, "former_names": None, "register_status": "Eingetragen", "management": None, "gleif_match_score": None}
    r.update(k); return r
rows = [
 base(slug="fairkocht-gmbh", name="FAIRKOCHT (fairkocht gmbh)", legal_name="fairkocht gmbh", fn="FN 531976v", register_id="531976v",
      address="Hof 437, 6866 Andelsbuch, AT", entity_status="Eingetragen (Firmenbuch, evi.gv.at)", founded="2020-05-06",
      owners="1 natürliche Person (Gesellschafter/in lt. Firmenbuch/evi.gv.at)", management="Wolfgang Mätzler (Geschäftsführung lt. Impressum)",
      website="https://www.fairkocht.at", brands=["FAIRKOCHT"], product_count=19, median_price_eur=13.5,
      nace="Lebensmittelerzeugung (Geschäftszweig lt. Firmenbuch)", share_capital=E["fairkocht-gmbh"]["stammkapital"],
      register_entry_date="2020-05-06", register_court="Landesgericht Feldkirch", imprint_url="https://www.fairkocht.at/impressum",
      uid="ATU75453279", uid_vies_name=V["75453279"]["name"], uid_vies_address=vaddr("75453279"), uid_checked_at=V["75453279"]["requestDate"],
      registry_status="verified_vies+impressum+firmenbuch (Impressum FN 531976v/ATU75453279 = evi.gv.at + VIES name+address; no GLEIF record)",
      sources=["https://www.fairkocht.at/impressum", "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/531976v"]),
 base(slug="christoephl-manufaktur-gmbh", name="Christöphl Manufaktur GmbH", legal_name="Christöphl Manufaktur GmbH", fn="FN 414202x", register_id="414202x",
      address="Erlenstraße 63, 8074 Raaba-Grambach, AT", entity_status="Eingetragen (Firmenbuch, evi.gv.at)", founded="2014-04-09",
      parent_direct="MACH Genussprodukte GmbH (FN 568278d, Graz; 100 %-Gesellschafterin lt. evi.gv.at)",
      parent_ultimate="MACH Genussprodukte GmbH (FN 568278d; deren Gesellschafter: 2 natürliche Personen lt. evi.gv.at)",
      owners="MACH Genussprodukte GmbH (FN 568278d) (Gesellschafter lt. Firmenbuch/evi.gv.at: 1× Gesellschafter/in)",
      website="https://christoephl.at", brands=["Christöphl", "Christöphl Manufaktur"], product_count=5, median_price_eur=8.0,
      nace="Herstellung, Haltbarmachung und Vertrieb regionaler Spezialitäten (Geschäftszweig lt. Firmenbuch)",
      share_capital=E["christoephl-manufaktur-gmbh"]["stammkapital"], register_entry_date="2014-04-09",
      register_court="Landesgericht für ZRS Graz", imprint_url="https://christoephl.at/pages/impressum",
      uid="ATU68596628", uid_vies_name=V["68596628"]["name"], uid_vies_address=vaddr("68596628"), uid_checked_at=V["68596628"]["requestDate"],
      registry_status="verified_vies+impressum+firmenbuch (Impressum FN 414202x/ATU68596628 = evi.gv.at + VIES name+address; Bauernladen origin address Sukdull 13, 8410 Wildon = production/pick-up site; no GLEIF record)",
      sources=["https://christoephl.at/pages/impressum", "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/414202x", "https://www.evi.gv.at/f/568278d"]),
 base(slug="genusss-manufaktur-bruckner-kg", name="Genusss-Manufaktur Bruckner KG (Nudelmanufaktur Yppenplatz)", legal_name="\"GENUSSS-MANUFAKTUR\" Bruckner KG",
      fn="FN 428315a", register_id="428315a", address="Yppenplatz 8, 1160 Wien, AT", entity_status="Eingetragen (Firmenbuch, evi.gv.at)", founded="2015-01-24",
      owners="2 natürliche Personen (Gesellschafter lt. Firmenbuch/evi.gv.at: 1× Unbeschränkt haftende/r Gesellschafter/in; 1× Kommanditist/in)",
      management="Dagmar Brandtner (Inhaber/Geschäftsführer lt. Impressum)", website="https://nudelmanufaktur.at",
      brands=["Genusss-Manufaktur", "Nudelmanufaktur Bruckner"], product_count=2, median_price_eur=7.9,
      nace="Erzeugung von und Handel mit Teigwaren (Geschäftszweig lt. Firmenbuch)", share_capital=None, register_entry_date="2015-01-24",
      register_court="Handelsgericht Wien", imprint_url="https://nudelmanufaktur.at/impressum.html",
      uid="ATU69302248", uid_vies_name=V["69302248"]["name"], uid_vies_address=vaddr("69302248"), uid_checked_at=V["69302248"]["requestDate"],
      registry_status="verified_vies+impressum+firmenbuch (Impressum FN 428315a/ATU69302248 = evi.gv.at + VIES name+address; no GLEIF record)",
      sources=["https://nudelmanufaktur.at/impressum.html", "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/428315a"]),
 base(slug="hackls-happy-turkey-gmbh", name="Hackls Happy Turkey GmbH (Marillenhof Hackl)", legal_name="Hackls Happy Turkey GmbH", fn="FN 550716b",
      register_id="550716b", address="Dorfstraße 20, 2191 Atzelsdorf, AT", entity_status="Eingetragen (Firmenbuch, evi.gv.at)", founded="2021-02-24",
      owners="1 natürliche Person (Gesellschafter/in lt. Firmenbuch/evi.gv.at)", website="https://www.hackls-marille.at",
      brands=["Hackls Happy Turkey", "Hackls Marille"], product_count=1, median_price_eur=9.9,
      nace="Landwirtschaftliche Nutztierhaltung (Geschäftszweig lt. Firmenbuch)", share_capital=E["hackls-happy-turkey-gmbh"]["stammkapital"],
      register_entry_date="2021-02-24", register_court=None,
      imprint_url="https://www.hackls-marille.at/impressum/",
      uid="ATU76907224", uid_vies_name=V["76907224"]["name"], uid_vies_address=vaddr("76907224"), uid_checked_at=V["76907224"]["requestDate"],
      registry_status="verified_vies+firmenbuch (Bauernladen seller 'Marillenhof Hackl & Hackls Happy Turkey'; Truthahn-Gulasch attributed to the turkey GmbH, FN 550716b on evi.gv.at, ATU76907224 VIES name+address match; the Marillenhof itself is a separate sole-trader UID ATU63513488 (VIES valid, same address) per hackls-marille.at Impressum; no GLEIF record)",
      sources=["https://www.hackls-marille.at/impressum/", "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/550716b"]),
 base(slug="venatio-wildspezialitaeten", name="Venatio. Wildspezialitäten aus Jägerhand", legal_name=None, fn=None, register_id=None, register_authority=None,
      address="Laaer Straße 41a, 2054 Haugsdorf, AT (Unternehmenssitz lt. Impressum; Produktion/Versand Konrad Frank-Weg 14, 2191 Pellendorf)",
      entity_status="Einzelunternehmen lt. Impressum (nicht im Firmenbuch)", founded=None,
      owners="Einzelunternehmen (1 natürliche Person lt. Impressum)", website="https://venatio.at", brands=["Venatio"], product_count=7, median_price_eur=9.9,
      nace="Einzelhandel mit Lebensmitteln; Nahrungs- und Genussmittelgewerbe (Unternehmensgegenstand lt. Impressum)", share_capital=None,
      register_status=None, register_entry_date=None, register_court=None, imprint_url="https://venatio.at/wp/",
      uid=None, uid_vies_name=None, uid_vies_address=None, uid_checked_at=None,
      registry_status="sole_trader_impressum (Einzelunternehmen, WKO member lt. Impressum; no FN and no UID published → not VIES/Firmenbuch-verifiable)",
      sources=["https://venatio.at/wp/", "https://venatio.at/wp/?page_id=24838"]),
]
P = f"{R}/data/companies.json"; d = json.load(open(P))
slugs = {r["slug"] for r in rows}
d = [r for r in d if r["slug"] not in slugs]
for r in d:
    if r["slug"] == "roman-fenz-eu":
        if "Bauernladen.at" not in r["chains"]: r["chains"].append("Bauernladen.at")
        r["product_count"] = 7; r["chain_product_count"] = None
        r["uid_vies_name"] = V["57151209"]["name"]; r["uid_vies_address"] = vaddr("57151209"); r["uid_checked_at"] = V["57151209"]["requestDate"]
        r["register_status"] = "Eingetragen"; r["register_entry_date"] = "2011-09-15"
        r["imprint_url"] = "https://dankebauer.com/impressum/"
        fenz = r
d += rows
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
C = f"{R}/data/companies.csv"
cur = list(csv.DictReader(open(C, encoding="utf-8"))); cols = list(cur[0].keys())
cur = [r for r in cur if r["slug"] not in slugs and r["slug"] != "roman-fenz-eu"]
def flat(row):
    o = {c: row.get(c) for c in cols}
    o["brands"] = "|".join(row["brands"]); o["chains"] = "|".join(row["chains"]); o["plants_count"] = 0
    if "sources" in cols: o["sources"] = "|".join(row.get("sources") or [])
    return {k: ("" if v is None else v) for k, v in o.items()}
with open(C, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
    for row in [fenz] + rows: w.writerow(flat(row))
ev = {"run": "2026-10-18T0506 Daten-Squad", "rows": rows, "updated": "roman-fenz-eu (+chain Bauernladen.at, product_count 4→7)",
      "vies": V, "evi": E, "evi_parent": EP,
      "gleif_fulltext_AT": {"fairkocht": 0, "Christöphl": 0, "MACH Genussprodukte": 0, "GENUSSS-MANUFAKTUR": 0, "Hackls Happy Turkey": 0, "Roman Fenz": "529900H4WE9MUT4KAE53 (existing)"},
      "no_row": {"vom Sandriegel": "no website/Impressum found; Bauernladen producer page lists only 'Sandriegel, 8385 Neuhaus am Klausenbach' + phone; no FN/UID published"},
      "note": "natural persons in evi sections counted, not named; Venatio owner named in its Impressum but not stored (legal_name null)"}
json.dump(ev, open(f"{R}/raw/companies_bauernladen_2026-10-18T0506.json", "w"), ensure_ascii=False, indent=1, default=str)
print("companies", len(d))
