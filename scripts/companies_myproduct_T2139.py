"""Daten-Squad 2026-10-16T2139: add the producer companies behind the 64 myProduct.at ready meals (T2111) that were not
yet in companies, plus the store operator myProduct GmbH (retailer).
Sources (public, no login, robots respected, <=1 req/s/host): pack-label producer string on myproduct.at product pages
(raw/myproduct_2026-10-16T2111.json), GLEIF lei-records (name + country search, accepted only when the register number
also appears on the company's own legal notice or name+address match the label), the company's own legal notice
(food-connectors impressum.find_imprint), EU VIES, evi.gv.at /f/<FN> (official Firmenbuch publication platform).
Founded: AT = GLEIF creationDate (local day) when not later than the Firmenbuch entry, else Firmenbuch Eintragungsdatum;
DE = GLEIF creationDate. Owners: legal entities named, natural persons counted only. Nothing inferred.
DE VIES returned MS_UNAVAILABLE at check time (2026-10-16T21:44Z) → DE UIDs printed on the legal notice are recorded in
`uid` with uid_vies_name 'not checked (DE VIES MS_UNAVAILABLE)' and do NOT count as VIES-verified."""
import csv, io, json, statistics as st
R = json.load(open("raw/myproduct_2026-10-16T2111.json", encoding="utf-8"))
P = json.load(open("scripts/cm_T2139/probe_T2139.json", encoding="utf-8"))
E = json.load(open("scripts/cm_T2139/evi_T2139.json", encoding="utf-8"))
G = "https://api.gleif.org/api/v1/lei-records/"; EVI = "https://www.evi.gv.at/f/"; VIES = "https://ec.europa.eu/taxation_customs/vies/"
T = "2026-10-16T21:46:10Z"; DEU = "not checked (DE VIES MS_UNAVAILABLE 2026-10-16T21:44Z)"
# producer-string prefix on myproduct.at -> slug
MAP = {"Andreas Hartl (Hartl's Kulinarikum)": "hartls-kulinarikum", "Danke Bauer - Roman Fenz e.U": "roman-fenz-eu",
       "ARCHE NATURPRODUKTE GMBH": "arche-naturprodukte-gmbh", "BIOART AG": "bioart-ag", "ÖKOLAND GMBH NORD": "oekoland-gmbh-nord",
       "RAPUNZEL NATURKOST GMBH": "rapunzel-naturkost-gmbh-co-kg", "RAPUNZEL - ZWERGENWIESE": "rapunzel-naturkost-gmbh-co-kg",
       "SCHENKEL ERICH GMBH": "schenkel-erich-gmbh", "PETERSILCHEN GMBH": "petersilchen-gmbh", "EGESUN GMBH & Co.KG": "egesun-gmbh-co-kg"}
U = {
 "hartls-kulinarikum": dict(name="Hartl's Kulinarikum", role="producer", legal_name="Hartl Andreas (Einzelunternehmer, Betreiber Hartl's Kulinarikum)",
    country="AT", address="Marktplatz 4 (Südbahnhofmarkt), 4020 Linz, AT", website="https://www.hartls-kulinarikum.at",
    imprint_url="https://www.hartls-kulinarikum.at/impressum", entity_status="ACTIVE (Medieninhaber lt. Impressum §5 ECG)",
    registry_status="label_and_impressum_only (natural-person sole trader; Impressum names 'Hartl Andreas, Martkplatz 4, 4020 Linz', no FN/UID/LEI published, no GLEIF record → legal entity not register-verified)",
    nace="Bio-Feinkost/Fertiggerichte, Marktstand Südbahnhofmarkt Linz; Bio-Zertifizierung Austria Bio Garantie seit Mai 2008 (Unternehmensangabe)",
    sources=["https://www.hartls-kulinarikum.at/impressum"]),
 "roman-fenz-eu": dict(name="Danke Bauer (Roman Fenz e.U.)", role="producer", legal_name="Roman Fenz e.U.", lei="529900H4WE9MUT4KAE53",
    fn="FN 368109m", register_id="368109m", register_authority="RA000017", register_court="Landesgericht Klagenfurt", legal_form_code="ECWU",
    country="AT", address="Bichlweg 6, 9500 Villach, AT", entity_status="ACTIVE (GLEIF; LEI ISSUED; Firmenbuch eingetragen)",
    founded="2011-09-15", founded_source="GLEIF legal entity creation date (LEI 529900H4WE9MUT4KAE53) = Firmenbuch Eintragungsdatum 15.09.2011 (evi.gv.at/f/368109m)",
    owners="Einzelunternehmer (1 natürliche Person)", website="https://dankebauer.com", imprint_url="https://dankebauer.com/at/impressum",
    uid="ATU57151209", uid_vies_name="Fenz Roman", uid_vies_address="Bichlweg 6, AT-9500 Villach", uid_checked_at="2026-10-16T21:42:29Z",
    nace="Handel mit Waren aller Art (Geschäftszweig lt. Firmenbuch)", gleif_match_score=1.0,
    registry_status="verified_gleif+vies+impressum (Impressum FN 368109m = GLEIF register id; VIES name = owner of the e.U., address match)",
    sources=[G + "529900H4WE9MUT4KAE53", "https://dankebauer.com/at/impressum", VIES, EVI + "368109m"]),
 "arche-naturprodukte-gmbh": dict(name="Arche Naturprodukte GmbH", role="producer", legal_name="ARCHE Naturprodukte GmbH", lei="529900BMCO2TYYBU4P09",
    register_id="HRB 85754", hrb="HRB 85754", register_authority="RA000234", legal_form_code="2HBR", country="DE",
    address="Liebigstraße 5a, 40721 Hilden, DE", entity_status="ACTIVE (GLEIF; LEI ISSUED)", founded="2018-12-05",
    founded_source="GLEIF legal entity creation date (LEI 529900BMCO2TYYBU4P09)", website="https://arche-naturkueche.de",
    imprint_url="https://arche-naturkueche.de/de/impressum.php", uid="DE322242442", uid_vies_name=DEU, gleif_match_score=1.0,
    registry_status="verified_gleif (legal notice HRB 85754 = GLEIF register id; label address = GLEIF address)",
    sources=[G + "529900BMCO2TYYBU4P09", "https://arche-naturkueche.de/de/impressum.php"]),
 "bioart-ag": dict(name="BioArt AG", role="producer", legal_name="BioArt AG", lei="5299004CIGK3WLRBB426", fn="FN 306867a", register_id="306867a",
    register_authority="RA000017", register_court="Landesgericht Salzburg", legal_form_code="EQOV", country="AT",
    address="Biodorfweg 4, 5164 Seeham, AT", entity_status="ACTIVE (GLEIF entity ACTIVE / LEI registration LAPSED; Firmenbuch eingetragen)",
    founded="2007-12-28", founded_source="GLEIF legal entity creation date (LEI 5299004CIGK3WLRBB426); Firmenbuch Eintragungsdatum 20.03.2008 (evi.gv.at/f/306867a)",
    share_capital="EUR 278 000 (lt. evi.gv.at)", website="https://bioart.at", imprint_url="https://bioart.at/impressum",
    uid="ATU64243713", uid_vies_name="BioArt AG", uid_vies_address="Biodorf-Weg 4, AT-5164 Seeham", uid_checked_at="2026-10-16T21:43:20Z",
    nace="Produktion, Handel und Vermittlung von Waren aller Art, insbesondere biologische Lebensmittel und fair gehandelte Produkte (Geschäftszweig lt. Firmenbuch)",
    gleif_match_score=1.0, registry_status="verified_gleif+vies (VIES name match 1.0 on the Impressum UID; GLEIF register id = FN)",
    sources=[G + "5299004CIGK3WLRBB426", "https://bioart.at/impressum", VIES, EVI + "306867a"]),
 "oekoland-gmbh-nord": dict(name="Ökoland GmbH Nord", role="producer", legal_name="Ökoland GmbH Nord Vertriebsgesellschaft für ökologische Erzeugnisse",
    lei="3912002MJDIL66IVKQ44", register_id="HRB 201209", hrb="HRB 201209", register_authority="RA000262", register_court="Amtsgericht Hannover",
    legal_form_code="2HBR", country="DE", address="Georgstr. 3, 31515 Wunstorf, DE", entity_status="ACTIVE (GLEIF; LEI ISSUED)",
    founded="1991-11-08", founded_source="GLEIF legal entity creation date (LEI 3912002MJDIL66IVKQ44)", website="https://oekoland.de",
    imprint_url="https://oekoland.de/impressum/", uid="DE116156996", uid_vies_name=DEU, gleif_match_score=1.0,
    registry_status="verified_gleif (legal notice HRB 201209, AG Hannover = GLEIF register id; label 'ÖKOLAND GMBH NORD, Georgstr. 3-5, Wunstorf')",
    sources=[G + "3912002MJDIL66IVKQ44", "https://oekoland.de/impressum/"]),
 "rapunzel-naturkost-gmbh-co-kg": dict(name="Rapunzel Naturkost", role="producer", legal_name="Rapunzel Naturkost GmbH & Co. KG",
    lei="529900Q11GX6NB4F4574", register_id="HRA 14236", hrb="HRA 14236", register_authority="RA000299", register_court="Amtsgericht Memmingen",
    legal_form_code="2HBR", country="DE", address="Rapunzelstraße 1, 87764 Legau, DE", entity_status="ACTIVE (GLEIF; LEI ISSUED)",
    founded="2011-08-02", founded_source="GLEIF legal entity creation date (LEI 529900Q11GX6NB4F4574)", website="https://rapunzel.de",
    imprint_url="https://rapunzel.de/impressum", uid="DE129088402", uid_vies_name=DEU, gleif_match_score=0.9,
    registry_status="verified_gleif (label 'RAPUNZEL NATURKOST GMBH' / 'RAPUNZEL - ZWERGENWIESE', Rapunzelstraße 1, Legau; legal notice lists HRA 14236 = GLEIF register id of the GmbH & Co. KG and HRB 21431 = general partner; Zwergenwiese is a Rapunzel brand at the same seat)",
    sources=[G + "529900Q11GX6NB4F4574", "https://rapunzel.de/impressum"]),
 "schenkel-erich-gmbh": dict(name="Schenkel Erich GmbH", role="producer", country="AT", address="3400 Klosterneuburg, AT (pack label on myproduct.at)",
    registry_status="unidentified (label only; no GLEIF record for 'Schenkel Erich/Erich Schenkel GmbH' in AT — only 'Erich Schenkel - Privatstiftung', Wien, not taken; no website/legal notice found; Firmenbuch name search needs FIRMENBUCH_API_KEY)",
    sources=["raw/myproduct_2026-10-16T2111.json"]),
 "petersilchen-gmbh": dict(name="Petersilchen GmbH", role="producer", legal_name="Petersilchen GmbH", register_id="HRB 11924", hrb="HRB 11924",
    register_authority="Amtsgericht Paderborn", register_court="Amtsgericht Paderborn", country="DE", address="Am Piepenbrink 2, 32839 Steinheim, DE",
    management="Christof Henne, Matthias Rebentisch (Geschäftsführer lt. Impressum)", website="https://petersilchen.de",
    imprint_url="https://petersilchen.de/impressum", uid="DE124612378", uid_vies_name=DEU,
    registry_status="register_no_from_impressum (HRB 11924 AG Paderborn + UID printed on the legal notice; no GLEIF record; DE VIES unavailable at check time → not counted as identified)",
    nace="Bio-Hersteller (EG-Kontroll-Nr. DE-ÖKO-013, IFS Progress Food lt. Website)", sources=["https://petersilchen.de/impressum"]),
 "egesun-gmbh-co-kg": dict(name="EgeSun GmbH & Co. KG", role="producer", legal_name="EgeSun GmbH & Co. KG", lei="529900D2TOUXZ7QYGX57",
    register_id="HRA 205719", hrb="HRA 205719", register_authority="RA000358", register_court="Amtsgericht Walsrode", legal_form_code="8Z6G",
    country="DE", address="Lübkemannstraße 7, 28876 Oyten, DE", entity_status="ACTIVE (GLEIF; LEI ISSUED)", founded="2025-06-27",
    founded_source="GLEIF legal entity creation date (LEI 529900D2TOUXZ7QYGX57)", website="https://egesun.de", imprint_url="https://egesun.de/impressum",
    uid="DE455151638", uid_vies_name=DEU, gleif_match_score=1.0,
    registry_status="verified_gleif (legal notice HRA 205719, AG Walsrode = GLEIF register id; label address = GLEIF address)",
    sources=[G + "529900D2TOUXZ7QYGX57", "https://egesun.de/impressum"]),
 "myproduct-gmbh": dict(name="myProduct GmbH", role="retailer", legal_name="myProduct GmbH", fn="FN 431059k", register_id="431059k",
    register_authority="Landesgericht Krems", register_court="Landesgericht Krems", country="AT", address="Karl Kastner-Straße 1, 3910 Zwettl, AT",
    entity_status="ACTIVE (Firmenbuch eingetragen)", founded="2015-03-28",
    founded_source="Firmenbuch Eintragungsdatum, evi.gv.at/f/431059k (myproduct.at schema.org foundingDate 2015-03-11 = Unternehmensangabe)",
    owners="Kastner Großhandelsgesellschaft m.b.H. (FN 44098a); 2 natürliche Personen (Gesellschafter lt. Firmenbuch/evi.gv.at)",
    management="Rainer Neuwirth M.A., KommR Christof Kastner, Mag. Herwig Gruber (Geschäftsführung lt. Impressum)", share_capital="EUR 36 000 (lt. evi.gv.at)",
    website="https://myproduct.at", imprint_url="https://myproduct.at/impressum", uid="ATU69436808", uid_vies_name="myProduct GmbH",
    uid_vies_address="Karl Kastner-Straße 1, AT-3910 Zwettl-NÖ", uid_checked_at="2026-10-16T21:44:42Z", nace="Onlinehandel (Geschäftszweig lt. Firmenbuch)",
    registry_status="verified_vies_impressum (no GLEIF record)", brands=[], chains=["myProduct"],
    sources=["https://myproduct.at/impressum", VIES, EVI + "431059k"]),
}
groups = {}
for x in R["products"]:
    s = MAP.get((x.get("producer") or "").split(",")[0])
    if s: groups.setdefault(s, []).append(x)
for s, xs in groups.items():
    U[s]["brands"] = sorted({x["brand"] for x in xs}); U[s]["chains"] = ["myProduct"]; U[s]["product_count"] = len(xs)
    pr = [x["price_eur"] for x in xs if x.get("price_eur")]; U[s]["median_price_eur"] = round(st.median(pr), 2) if pr else None
U["myproduct-gmbh"]["chain_product_count"] = len(R["products"])
for s, u in U.items(): u.setdefault("slug", s); u.setdefault("fetched_at", T)
p = "data/companies.json"; d = json.load(open(p, encoding="utf-8")); have = {r["slug"] for r in d}
keys = list(d[0].keys()); added = []
for s, u in U.items():
    if s in have: continue
    r = {k: None for k in keys}; r.update({"plants": [], "brands": [], "chains": [], "sources": []}); r.update(u); r["slug"] = s
    d.append(r); added.append(s)
end = "\n" if open(p, encoding="utf-8").read().endswith("\n") else ""
open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + end)
p = "data/companies.csv"; raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys()); hc = {r["slug"] for r in rows}
for s in added:
    if s in hc: continue
    u = U[s]; r = {k: "" for k in fields}
    for k, v in u.items():
        if k in fields: r[k] = "|".join(v) if isinstance(v, list) and k in ("brands", "chains") else ("" if v is None or isinstance(v, list) else str(v))
    r["slug"] = s; rows.append(r)
out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
json.dump({"run": "T2139", "added": added, "rows": {s: U[s] for s in added}, "probe": P, "evi": E,
           "not_taken": {"Erich Schenkel - Privatstiftung (GLEIF, Wien)": "different entity/seat than label 'SCHENKEL ERICH GMBH, 3400 Klosterneuburg'",
                         "DE UIDs": "DE VIES MS_UNAVAILABLE at 2026-10-16T21:44Z (retried once) → recorded, not counted as VIES-verified"},
           "already_present": ["allos-hof-manufaktur-gmbh", "followfood-gmbh", "golden-veggies-gmbh", "kreyenhop-kluge-gmbh-cokg", "biogourmet-gmbh"]},
          open("raw/companies_myproduct_2026-10-16T2139.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("added", len(added), added)
