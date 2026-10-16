"""Daten-Squad 2026-10-16T1805: close remaining legal-entity gaps (13 rows without LEI/UID after T1706).
Sources (all public, no login, robots respected, <=1 req/s/host): GLEIF API lei-records, EU VIES REST (incl. approximate
trader-name match for ES), brand-site Impressum/legal notices, evi.gv.at (official Firmenbuch publication platform, /f/<FN>
pages are robots-allowed), CZ ARES REST, SK RPO API (api.statistics.sk), Swiss UID public web service (uid-wse.admin.ch,
GetByUID), UK Companies House public company page, openregister.de (Handelsregister data).
Only facts printed on those pages / returned by those registries are written; nothing inferred.
Metric: 'legal entity identified' = LEI or VIES-verified EU UID. Non-EU register IDs (CH UID CHE-..., UK company number)
are written to register_id with registry_status 'verified_non_eu_register_*' and counted separately.
FN-/HRB-only rows (register number from an official/public register, but no LEI and no VIES-valid UID) stay outside the metric."""
import csv, json, io
EVI = "https://www.evi.gv.at/f/"
VIES = "https://ec.europa.eu/taxation_customs/vies/"
U = {
 "mochi-production-gmbh": dict(legal_name="Mochi Production GmbH", fn="FN 554188h", register_id="554188h",
    register_authority="Handelsgericht Wien", register_court="Handelsgericht Wien", country="AT",
    address="Ferdinandstraße 13/1, 1020 Wien, AT", entity_status="ACTIVE (Firmenbuch: eingetragen seit 2021-04-10)",
    founded="2021-04-10", owners="Mochi Holding GmbH (Gesellschafterin lt. evi.gv.at)",
    management="Gerhard Summer (Geschäftsführer lt. Impressum/Firmenbuch)", website="https://shoppu.mochi.at",
    imprint_url="https://shoppu.mochi.at/impressum", uid="ATU76763147", uid_vies_name="Mochi Production GmbH",
    uid_vies_address="Ferdinandstraße 13/1, AT-1020 Wien", uid_checked_at="2026-10-16T18:11:15Z",
    nace="Entwicklung und Produktion von Speisen für den Lebensmittelhandel (Geschäftszweig lt. Firmenbuch)",
    registry_status="verified_vies_impressum", fetched_at="2026-10-16T18:11:15Z",
    sources=["https://shoppu.mochi.at/impressum", VIES, EVI + "554188h"]),
 "hildegard-gruenkraft-naturprodukte": dict(legal_name="St. Hildegard-Posch GmbH", fn="FN 266429h", register_id="266429h",
    register_authority="Landesgericht Wels", register_court="Landesgericht Wels", country="AT",
    address="Thern 40, 4880 St. Georgen im Attergau, AT", entity_status="ACTIVE (Firmenbuch: eingetragen seit 2005-09-06)",
    founded="2005-09-06", management="Nikolaj Posch, Mag. pharm. Patrick Posch (Geschäftsführer lt. Impressum)",
    website="http://www.hildegard-grünkraft.at", imprint_url="http://www.xn--hildegard-grnkraft-x6b.at/impressum.html",
    uid="ATU61930557", uid_vies_name="St. Hildegard-Posch GmbH", uid_vies_address="Thern 40, AT-4880 St.Georgen/Attergau",
    uid_checked_at="2026-10-16T18:12:03Z", nace="Vertrieb von Naturprodukten (Geschäftszweig lt. Firmenbuch)",
    registry_status="verified_vies_impressum (brand-site Impressum names St. Hildegard-Posch GmbH, FN 266429h, ATU61930557; VIES + Firmenbuch address Thern 40, Impressum address Am Weinberg 23 — same town 4880 St. Georgen im Attergau)",
    fetched_at="2026-10-16T18:12:03Z",
    sources=["http://www.xn--hildegard-grnkraft-x6b.at/impressum.html", VIES, EVI + "266429h"]),
 "franu-espana-sl": dict(legal_name="FRA NUI ESPAÑA SOCIEDAD LIMITADA", lei="959800UR1864J6SPSH33", register_id="1000172035445",
    register_authority="RA000533", legal_form_code="DP3Q", country="ES", address="Dels Gremis 8, 46290 Alcàsser, ES",
    entity_status="ACTIVE (GLEIF entity; LEI ISSUED, next renewal 2027-04-10)", gleif_ultimate_parent_exception="NON_CONSOLIDATING",
    gleif_match_score=1.0, gleif_match_basis="GLEIF legal name FRA NUI ESPAÑA S.L. = label 'Franuí Espana SL.' (brand Franuí), country ES; VIES ES approximate match traderName FRANUI ESPANA SL / 46290 / ALCASSER = VALID",
    uid="ESB40502403", uid_vies_name="--- (ES returns no name; approximate match traderName 'FRANUI ESPANA SL' = VALID)",
    uid_vies_address="--- (ES; traderPostalCode 46290 = VALID, traderCity ALCASSER = VALID)", uid_checked_at="2026-10-16T18:13:55Z",
    registry_status="verified_gleif+vies", fetched_at="2026-10-16T18:16:30Z",
    sources=["https://api.gleif.org/api/v1/lei-records/959800UR1864J6SPSH33", VIES]),
 "gastrotech": dict(legal_name="GASTROTECH, s.r.o.", register_id="06661645", register_authority="Městský soud v Praze, C 286534",
    register_court="Městský soud v Praze", country="CZ", address="Zděbradská 74, Jažlovice, 251 01 Říčany, CZ",
    entity_status="ACTIVE (ARES: AKTIVNI; seat until 2026-04-30 Štúrova 1701/55, 142 00 Praha 4)", founded="2017-12-06",
    uid="CZ06661645", uid_vies_name="GASTROTECH, s.r.o.", uid_vies_address="Zděbradská 74, JAŽLOVICE, 251 01 ŘÍČANY",
    uid_checked_at="2026-10-16T18:14:00Z",
    registry_status="verified_vies_public_register (label 'Gastrotech, s.r.o.' = the only active exact-name entity in CZ ARES and SK RPO (SK 'Gastrotech, s.r.o.' 45394903 terminated 2022); VIES valid; brand Sushitime (sushitime.cz, Optiform s.r.o.) is operated at the same seat Zděbradská 74, Říčany)",
    fetched_at="2026-10-16T18:14:00Z",
    sources=["https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/06661645", VIES, "https://www.sushitime.cz/cz/kontakt/"]),
 "planted-foods-ag": dict(legal_name="Planted Foods AG", register_id="CHE-398.606.506",
    register_authority="Swiss UID register (BFS) — non-EU register ID; Handelsregister Kanton Zürich CH-020.3.047.536-5",
    legal_form_code="0106 (eCH-0097: Aktiengesellschaft)", country="CH", address="Kemptpark 32, 8310 Kemptthal, CH",
    entity_status="ACTIVE (UID register; Sitz Lindau ZH)",
    registry_status="verified_non_eu_register_ch_uid (Swiss UID public web service GetByUID CHE-398.606.506: Planted Foods AG, legal form AG, Kemptpark 32, 8310 Kemptthal; label 'Planted Foods AG' + CH; no LEI, CH outside VIES)",
    fetched_at="2026-10-16T18:10:30Z", sources=["https://www.uid-wse.admin.ch/V5.0/PublicServices.svc (GetByUID CHE398606506)", "https://www.uid.admin.ch/Detail.aspx?uid_id=CHE398606506"]),
 "gue-puds": dict(legal_name="GU INDULGENT FOODS LIMITED", register_id="07104090",
    register_authority="Companies House (UK) — non-EU register ID", legal_form_code="Private limited Company", country="GB",
    address="Head Office, Dunmow Road, Bishop's Stortford, Hertfordshire, CM23 5PA, GB", entity_status="ACTIVE (Companies House)",
    founded="2009-12-14", website="https://gudesserts.com", imprint_url="https://gudesserts.com/pages/privacy-policy",
    nace="SIC 10890 Manufacture of other food products n.e.c. (Companies House)",
    registry_status="verified_non_eu_register_uk_companies_house (brand site gupuds.com → gudesserts.com: '© 2026 Gü Indulgent Foods Limited', privacy policy 'Gü Indulgent Foods Ltd, Dunmow Road, Bishops Stortford CM23 5PA' = Companies House 07104090 registered office; previous name NOBLE DESSERTS HOLDINGS LIMITED until 2021-06-25; no LEI, UK outside VIES)",
    fetched_at="2026-10-16T18:13:00Z",
    sources=["https://find-and-update.company-information.service.gov.uk/company/07104090", "https://gudesserts.com/pages/privacy-policy"]),
 "knoedelwerkstatt-gmbh": dict(legal_name="Knödelwerkstatt GmbH", fn="FN 508483w", register_id="508483w", country="AT",
    address="Hauptstraße 12, 4581 Rosenau am Hengstpaß, AT", entity_status="ACTIVE (Firmenbuch: eingetragen seit 2019-03-08)",
    founded="2019-03-08", owners="Werner Dilly, Pernsteiner Entwicklungs GmbH (Gesellschafter lt. evi.gv.at)",
    management="Werner Dilly (Geschäftsführer lt. Firmenbuch)", website="https://www.knoedelwerkstatt.at",
    imprint_url="https://www.knoedelwerkstatt.at/impressum/", nace="Lebensmittelproduktion (Geschäftszweig lt. Firmenbuch)",
    registry_status="fn_public_register (evi.gv.at FN 508483w name+address = pack label 'Knödelwerkstatt G.m.b.H, Hauptstraße 12, 4581 Rosenau am Hengstpass'; Impressum UID truncated 'ATU', directory UID ATU56237548 VIES-invalid 2026-10-16T18:09Z — no LEI/verified UID, not counted as legal entity identified)",
    fetched_at="2026-10-16T18:09:40Z", sources=[EVI + "508483w", "https://www.knoedelwerkstatt.at/impressum/", VIES]),
 "kasnudl-gmbh": dict(legal_name="Invaro GmbH (Firmenwortlaut 2019-03-20–2026-06-03: Kasnudl GmbH)", fn="FN 425910p", register_id="425910p",
    register_authority="Handelsgericht Wien", register_court="Handelsgericht Wien", country="AT", address="Schumanngasse 16/16, 1180 Wien, AT",
    entity_status="ACTIVE (Firmenbuch: eingetragen; Insolvenz-Mitteilungen 11/2024 + 02/2025, Namensänderung 06/2026)", founded="2014-12-04",
    owners="Andreas Schrittesser, Schmidbauer Food Innovation GmbH (Gesellschafter lt. evi.gv.at)", management="Andreas Schrittesser (Geschäftsführer lt. Firmenbuch)",
    registry_status="fn_public_register (pack label 'Stadtküche (Kasnudl GmbH)' = FN 425910p, renamed Invaro GmbH 2026-06-03 (name history firmenatlas.com, Justiz data; evi.gv.at: FN, address, Namensänderung 06/2026); Stadtküche brand now run by Knödelhütte GmbH (row stadtkueche); firmenatlas shows UID ATU83103945, but VIES returns that UID for Knödelhütte GmbH — not used; no LEI/verified UID, not counted)",
    fetched_at="2026-10-16T18:20:00Z", sources=[EVI + "425910p", "https://www.firmenatlas.com/firma/425910p"]),
 "alimentastic-food-innovation-gmbh": dict(legal_name="Schmidbauer Food Innovation GmbH (Firmenwortlaut 2023-12-12–2026-02-11: Alimentastic Food Innovation GmbH)",
    fn="FN 615538d", register_id="615538d", register_authority="Landesgericht Salzburg", register_court="Landesgericht Salzburg",
    country="AT", address="Strubergasse 24, 5020 Salzburg, AT", founded="2023-12-12", management="Mag. (FH) Laurenz Hoffmann (Geschäftsführer lt. Firmenbuch)",
    entity_status="ACTIVE (Firmenbuch: eingetragen seit 2023-12-12)",
    registry_status="fn_public_register (label entity 'Alimentastic Food Innovation GmbH' = FN 615538d per evi.gv.at + wirtschaft.at name history, renamed Schmidbauer Food Innovation GmbH 2026-02-11; T1706 had mapped the brand successor Alimentastic GmbH FN 673845z (founded 2026-02-27, ATU83105925 VIES-valid per biogenamoments.com Impressum) — corrected to the label entity; no LEI/verified UID for FN 615538d, not counted)",
    fetched_at="2026-10-16T18:19:00Z", sources=[EVI + "615538d", "https://www.wirtschaft.at/u/615538d", EVI + "673845z", "https://www.biogenamoments.com/policies/legal-notice"]),
 "bauck-gmbh": dict(legal_name="Bauck GmbH", hrb="HRB 205474", register_id="HRB 205474", register_authority="Amtsgericht Lüneburg",
    register_court="Amtsgericht Lüneburg", country="DE", address="Duhenweitz 4, 29571 Rosche, DE", entity_status="ACTIVE (openregister.de)",
    management="Jan-Peter Bauck, Friedemann Wecker (Geschäftsführer lt. openregister.de)", website="https://www.bauck.de",
    registry_status="hrb_public_register (exact name 'Bauck GmbH' (label), HRB 205474 AG Lüneburg, Duhenweitz 4 = address of the Bauck Mühle brand site; no public UID — bauck.de Impressum UID DE313040669 belongs to BauckOnline GmbH HRB 206937; no LEI — not counted)",
    fetched_at="2026-10-16T18:22:00Z", sources=["https://openregister.de/company/DE-HRB-P2507-205474", "https://www.bauck.de/impressum/"]),
 "delikatessa-gmbh": dict(
    registry_status="not_mapped (candidate: '\"Delikatessa\" Lebensmittel-Handels- und Erzeugungs-Gesellschaft m.b.H.' FN 125012t, Wiener Neudorf, gelöscht 2020-08-14 durch Verschmelzung lt. evi.gv.at; label short form 'Delikatessa GmbH' not an exact name, absorbing entity not shown — not mapped; a different delikatessa gmbh Heidelberg HRB 337486 exists)",
    fetched_at="2026-10-16T18:21:00Z", sources=[EVI + "125012t"]),
 "vegetarische-feinkost-produktion-peter-hiel": dict(country="AT", address="Marchfeldstraße 4, 1200 Wien, AT (pack label)",
    registry_status="sole_trader_unverified (label 'Vegetarische Feinkost Produktion Peter Hiel' = Einzelunternehmen, no FN/UID published; business continued since 01/2024 by Hiel & Co GmbH FN 626704z ATU80621089 (VIES valid, Industriestraße 1, 2100 Korneuburg; hiel.at Impressum) — different legal entity, not mapped)",
    fetched_at="2026-10-16T18:18:13Z", sources=["https://www.hiel.at/impressum", VIES]),
 "verband-der-mpreis-partner-jeden-tag": dict(
    registry_status="label_distributor_unverified ('Verband der MPREIS-Partner' — no registered entity found; 'Jeden Tag' brand-site Impressum (jeden-tag.at) = Zentrale Handelsgesellschaft - ZHG - mbH FN 105041y, Radingerstraße 2a, 1020 Wien (brand owner, not the label producer); no LEI/UID — not mapped)",
    fetched_at="2026-10-16T18:24:00Z", sources=["https://www.jeden-tag.at/de/impressum", EVI + "105041y"]),
}
CLEAR = {"alimentastic-food-innovation-gmbh": ["uid_checked_at"]}  # T1706 VIES check was for the successor's old UID
p = "data/companies.json"; d = json.load(open(p, encoding="utf-8"))
for r in d:
    if r["slug"] in U:
        for k, v in U[r["slug"]].items():
            if k == "sources": r[k] = list(dict.fromkeys((r.get(k) or []) + v))
            else: r[k] = v
        for k in CLEAR.get(r["slug"], []): r.pop(k, None)
end = "\n" if open(p, encoding="utf-8").read().endswith("\n") else ""
open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + end)
p = "data/companies.csv"; raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys())
for r in rows:
    if r["slug"] in U:
        for k, v in U[r["slug"]].items():
            if k in fields and k != "sources": r[k] = "" if v is None else str(v)
        for k in CLEAR.get(r["slug"], []):
            if k in fields: r[k] = ""
out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
print("updated", len(U), list(U))
