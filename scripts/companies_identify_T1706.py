"""Daten-Squad 2026-10-16T1706: close legal-entity gaps for producer/retailer rows that had neither LEI nor VIES/Impressum id.
Sources (all public, robots respected, no login): brand-site Impressum pages + EU VIES (food-connectors `food company --impressum`),
GLEIF API lei-records. Only facts printed on those pages / returned by those registries are written; nothing inferred."""
import csv, json, io
U = {
 "stadtkueche": dict(legal_name="Knödelhütte GmbH", fn="FN 675365i", register_id="FN 675365i", register_authority="Handelsgericht Wien",
    register_court="Handelsgericht Wien", country="AT", address="Barbara-Prammer-Allee 15/1/1A, 1220 Wien, AT",
    management="Daniel Pichler (Geschäftsführer lt. Impressum)", website="https://kasnudl.at", imprint_url="https://kasnudl.at/impressum",
    uid="ATU83103945", uid_vies_name="Knödelhütte GmbH", uid_vies_address="Barbara-Prammer-Allee 15/1/1A, AT-1220 Wien",
    uid_checked_at="2026-10-16T17:10:34Z", registry_status="verified_vies_impressum", fetched_at="2026-10-16T17:10:34Z",
    nace="Lebensmittelproduktion (Unternehmensgegenstand lt. Impressum)",
    sources=["https://kasnudl.at/impressum", "https://ec.europa.eu/taxation_customs/vies/"]),
 "kasnudl-gmbh": dict(country="AT", website="https://kasnudl.at",
    registry_status="label_entity_unverified (pack label 'Stadtküche (Kasnudl GmbH)'; brand site kasnudl.at Impressum names Knödelhütte GmbH FN 675365i — see row stadtkueche; no register/VIES record for 'Kasnudl GmbH' found)",
    fetched_at="2026-10-16T17:10:34Z", sources=["https://kasnudl.at/impressum"]),
 "unimarkt-gmbh": dict(legal_name="UNIMARKT Handelsgesellschaft m.b.H. & Co. Kommanditgesellschaft", lei="529900X5GBP4KNVUYQ35",
    fn="FN 25076b", register_id="25076b", country="AT", address="Egger-Lienz-Straße 14, 4050 Traun, AT",
    entity_status="ACTIVE (GLEIF entity; LEI registration LAPSED since 2017-02-25)", legal_form_code="8888",
    registry_status="verified_gleif", gleif_match_score=1.0, fetched_at="2026-10-16T17:20:00Z",
    sources=["https://api.gleif.org/api/v1/lei-records/529900X5GBP4KNVUYQ35"]),
 "alimentastic-food-innovation-gmbh": dict(legal_name="Alimentastic GmbH", country="AT", address="Strubergasse 24, 5020 Salzburg, AT",
    register_authority="Landesgericht Salzburg", register_court="Landesgericht Salzburg", website="https://alimentastic.com",
    imprint_url="https://alimentastic.com/impressum", uid_checked_at="2026-10-16T17:10:39Z",
    registry_status="fn_from_imprint (Impressum UID ATU70319525 returned 'invalid' by VIES 2026-10-16T17:10Z — not written as verified UID)",
    fetched_at="2026-10-16T17:10:39Z", sources=["https://alimentastic.com/impressum", "https://ec.europa.eu/taxation_customs/vies/"]),
}
# companies.json
p = "data/companies.json"; d = json.load(open(p, encoding="utf-8"))
for r in d:
    if r["slug"] in U:
        for k, v in U[r["slug"]].items():
            if k == "sources": r[k] = list(dict.fromkeys((r.get(k) or []) + v))
            else: r[k] = v
end = "\n" if open(p, encoding="utf-8").read().endswith("\n") else ""
open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + end)
# companies.csv (keep header + line terminator)
p = "data/companies.csv"; raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys())
for r in rows:
    if r["slug"] in U:
        for k, v in U[r["slug"]].items():
            if k in fields and k != "sources": r[k] = "" if v is None else str(v)
out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
print("updated", list(U))
