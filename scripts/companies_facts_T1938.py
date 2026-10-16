"""Daten-Squad 2026-10-16T1938: company employees / revenue / founding from VERIFIED public statements.
Probe passes (scripts/facts_T1938/): crawl.py (company-owned about/history/facts/careers/press pages on the row's verified
website; robots.txt respected, no cookies/JS/login, <=1 req/s per host, 4 hosts in parallel), wikidata.py (items matched by
LEI P1278 or official website P856 == row website only), wikipedia.py (de/en/it infobox of those items).
This script re-fetches every accepted source, requires every listed phrase to be present verbatim on that page (whitespace
normalised) and only then writes the value into an EMPTY field (never overwrites). Evidence: raw/companies_facts_2026-10-16T1938.json.
Scope rules: entity vs group is spelled out in the value ('Gruppe', 'weltweit', 'dm Österreich'); founding statements are
labelled as company/brand statements ('Unternehmensangabe', 'Marke', 'Gruppe') — they are not legal-entity dates.
Third-party figures only with outlet named (Die Presse paid advertorial = company-supplied, labelled 'Anzeige')."""
import csv, html, io, json, re, subprocess, tempfile, os, time, urllib.parse, urllib.request, urllib.robotparser, urllib.error
UA = "food-connectors/0.1 (+https://github.com/servas-ai/fertiggerichte-daten)"
NOW = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
W = "web"; WP = "wikipedia"; WD = "wikidata"; PDF = "pdf"
UO = "Unternehmensangabe"
# (slug, field, value, kind, url(s), must-phrases (prefix 're:' = regex), scope, quote-hint)
D = [
 ("alnatura-gmbh", "employees", "3.730 (Unternehmensangabe GJ 2024/25, Alnatura gesamt; davon 200 Lehrlinge/Studierende)", W, "https://www.alnatura.de/presse/daten-und-fakten", ["Mitarbeiter/ -innen", "3.730", "davon 200 Lehrlinge und Studierende"], "company (Alnatura, operating entity = Alnatura Produktions- und Handels GmbH per legal notice)"),
 ("alnatura-gmbh", "revenue", "1,274 Mrd. € netto (GJ 2024/25, Unternehmensangabe)", W, "https://www.alnatura.de/presse/daten-und-fakten", ["Umsatz GJ 2024/25: 1,274 Mrd. Euro netto"], "company"),
 ("alnatura-gmbh", "founded", "1984 (Unternehmensangabe: Gründungsjahr Alnatura; Rechtsträger GmbH lt. GLEIF 1987)", W, "https://www.alnatura.de/presse/daten-und-fakten", ["Gründungsjahr", "re:Gründungsjahr\\W{0,5}1984"], "company founding (not legal-entity date)"),
 ("alnatura-produktions-und-handels-gmbh", "employees", "3.730 (Unternehmensangabe GJ 2024/25, Alnatura gesamt; davon 200 Lehrlinge/Studierende)", W, "https://www.alnatura.de/presse/daten-und-fakten", ["3.730", "davon 200 Lehrlinge und Studierende"], "company"),
 ("alnatura-produktions-und-handels-gmbh", "revenue", "1,274 Mrd. € netto (GJ 2024/25, Unternehmensangabe)", W, "https://www.alnatura.de/presse/daten-und-fakten", ["Umsatz GJ 2024/25: 1,274 Mrd. Euro netto"], "company"),
 ("biovegan-gmbh", "employees", "über 120 (Unternehmensangabe 2026)", W, "https://www.biovegan.de/", ["mit über 120 Mitarbeitenden"], "company"),
 ("biovegan-gmbh", "founded", "seit 1986 (Unternehmensangabe: „Bio & vegan seit 1986“)", W, "https://www.biovegan.de/pages/ueber-uns", ["Seit 1986 stehen wir für Bio-Qualität"], "company statement"),
 ("deflorian-srl", "founded", "1991 (Unternehmensangabe: Gründung als Einzelunternehmen in Gnadenwald; heute Deflorian Tiefkühlspezialitäten GmbH)", W, "https://deflorian.tirol/pages/uber-uns", ["Gründung Deflorian Tiefkühlspezialitäten als Einzelunternehmen", "1991 Gründung"], "company founding (sole proprietorship), not the GmbH"),
 ("deflorian-srl", "employees", "17 (Unternehmensangabe, Stand 2016)", W, "https://deflorian.tirol/pages/uber-uns", ["2016 25 Jahre Gnadenwald", "17 Mitarbeiter"], "company, 2016 timeline entry"),
 ("followfood-gmbh", "employees", "76 (Unternehmensangabe, Steckbrief)", W, "https://followfood.de/bewegung", ["followfood Steckbrief", "Mitarbeiter:innen 76"], "company"),
 ("mpreis-warenvertriebs-gmbh", "employees", "über 6.000 (Unternehmensangabe, MPREIS gesamt)", W, "https://www.mpreis.at/mpreis/werte", ["über 6.000 Mitarbeitenden"], "company (MPREIS)"),
 ("planted-foods-ag", "founded", "2019 (Unternehmensangabe: Firmengründung August 2019)", W, "https://planted-foods-de.myshopify.com/pages/about", ["Planted wurde 2019 gegründet", "2019 August Firmengründung"], "company founding (Planted, Kemptthal)"),
 ("planted-foods-ag", "employees", "über 170 (Unternehmensangabe Juli 2022, Planted gesamt in 6 Ländern)", W, "https://planted-foods-de.myshopify.com/pages/about", ["in 6 Ländern mit über 170 Mitarbeitenden"], "group (all countries), 2022"),
 ("planted-foods-gmbh", "founded", "Gruppe 2019 (Unternehmensangabe: Firmengründung Planted August 2019, Planted Foods AG)", W, "https://planted-foods-de.myshopify.com/pages/about", ["Planted wurde 2019 gegründet", "2019 August Firmengründung"], "group founding, not the DE GmbH"),
 ("planted-foods-gmbh", "employees", "Gruppe über 170 (Unternehmensangabe Juli 2022, Planted gesamt)", W, "https://planted-foods-de.myshopify.com/pages/about", ["in 6 Ländern mit über 170 Mitarbeitenden"], "group, 2022"),
 ("revo-foods", "employees", "21 Team Members (Unternehmensangabe)", W, "https://revo-foods.com/team/", ["Team Members 21"], "company"),
 ("rewe-international-ag", "employees", "rund 47.000 (REWE Group Österreich, Jahresende 2025, Unternehmensangabe)", W, "https://rewe-group.at/de/ueber-uns/zahlen-fakten/", ["Das Jahr 2025", "beschäftigte zum Jahresende landesweit rund 47.000 Mitarbeiter:innen"], "group (REWE Group Österreich)"),
 ("rewe-international-ag", "revenue", "11,36 Mrd. € brutto (2025, REWE Group Österreich, Unternehmensangabe)", W, "https://rewe-group.at/de/ueber-uns/zahlen-fakten/", ["Das Jahr 2025", "Bruttoumsatz um + 2,2 Prozent auf 11,36 Milliarden Euro"], "group (REWE Group Österreich)"),
 ("penny-gmbh", "employees", "mehr als 2.900 (Unternehmensangabe, PENNY Österreich)", W, "https://www.penny.at/ueber-uns", ["Zahlen & Fakten", "Mehr als 2.900 MitarbeiterInnen"], "company (PENNY Österreich)"),
 ("dr-schaer-spa", "employees", "über 1.400 weltweit (Dr. Schär Gruppe, Unternehmensangabe)", W, "https://www.schaer.com/en-us/company-dr-schar", ["more than 1,400 employees worldwide"], "group (worldwide)"),
 ("spar-oesterreichische-warenhandels-aktiengesellschaft", "employees", "über 93.000 (SPAR Österreich-Gruppe, davon 51.000 in Österreich; Unternehmensangabe)", W, "https://www.spar.at/unternehmen", ["Die SPAR Österreich-Gruppe beschäftigt in Summe über 93.000 Mitarbeiter:innen, 51.000 davon in Österreich"], "group"),
 ("spar-oesterreichische-warenhandels-aktiengesellschaft", "revenue", "10,82 Mrd. € Brutto-Verkaufsumsatz SPAR Österreich (2025); Gruppe 22,3 Mrd. €", W, "https://www.spar.at/unternehmen", ["2025 in Österreich auf 10,82 Mrd. Euro", "wuchs 2025 um insgesamt +4 % auf 22,3 Milliarden Euro"], "Austria + group, gross sales"),
 ("tress-lebensmittel-gmbh-co-kg", "employees", "100+ (Unternehmensangabe, TressBrüder gesamt)", W, "https://tressbrueder.de/ueber-uns", ["100+ Menschen im Team"], "family business overall (TressBrüder)"),
 ("weinbergmaier-gmbh", "employees", "250 (Unternehmensangabe)", W, "https://www.weinbergmaier.at/ueber-uns/das-sind-wir", ["250 Mitarbeiter"], "company"),
 ("weinbergmaier-gmbh", "revenue", "75,2 Mio. € (2024, Unternehmensangabe)", W, "https://www.weinbergmaier.at/ueber-uns/presse", ["Geschäftsjahr 2024", "auf 75,2 Millionen Euro steigern"], "company"),
 ("ager-gesmbh", "employees", "rund 100 (Unternehmensangabe)", W, "https://www.ager.cc/unternehmen/ueber-uns", ["mit rund 100 Mitarbeitern geführt"], "company"),
 ("bauck-gmbh", "employees", "rund 280 in Rosche (Unternehmensangabe)", W, "https://www.bauck.de/ueber-uns/fakten-und-zahlen/", ["Bei uns in Rosche arbeiten inzwischen rund 280 Kolleginnen und Kollegen"], "company (Rosche site = HQ)"),
 ("bauck-gmbh", "revenue", "rund 73 Mio. € pro Geschäftsjahr (Unternehmensangabe, „73400000 € Jahresumsatz“; Jahr nicht genannt)", W, "https://www.bauck.de/ueber-uns/fakten-und-zahlen/", ["73400000 € Jahresumsatz", "rund 73 Millionen Euro pro Geschäftsjahr"], "company, year not stated"),
 ("a-darbo-ag", "founded", "seit 1879 (Unternehmensangabe: Familie Darbo)", W, "https://darbo.com/at/", ["Seit 1879 kreiert die Familie Darbo"], "company/family statement"),
 ("a-darbo-ag", "employees", "über 400 (Unternehmensangabe, 4 Tiroler Standorte)", W, "https://darbo.com/at/karriere/", ["Mit über 400 Mitarbeiterinnen und Mitarbeitern veredelt Darbo"], "company"),
 ("ehrmann-gmbh", "employees", "Gruppe: über 3.450 (Ehrmann SE, 2024, Unternehmensangabe)", W, "https://www.ehrmann.de/unternehmen/ehrmann-die-familien-molkerei-aus-dem-allgaeu/", ["Mit über 3450 Mitarbeitern hat die Ehrmann SE im Jahr 2024"], "group (Ehrmann SE), row website = group site"),
 ("ehrmann-gmbh", "revenue", "Gruppe: ca. 1,1 Mrd. € (Ehrmann SE, 2024, Unternehmensangabe)", W, "https://www.ehrmann.de/unternehmen/ehrmann-die-familien-molkerei-aus-dem-allgaeu/", ["hat die Ehrmann SE im Jahr 2024 circa 1.1 Milliarden Euro"], "group (Ehrmann SE)"),
 ("frosta-ag", "employees", "1.849 Ø (2025, Kennzahlen der FRoSTA AG)", W, "https://www.frosta-ag.com/investor-relations/kennzahlen/", ["Kennzahlen der AG", "re:Mitarbeiter \\(Durchschnitt\\)\\s*Anzahl\\s*1\\.760\\s*1\\.849"], "company (investor-relations key figures)"),
 ("frosta-ag", "revenue", "682 Mio. € (2025, Kennzahlen der FRoSTA AG)", W, "https://www.frosta-ag.com/investor-relations/kennzahlen/", ["Kennzahlen der AG", "re:Umsatz \\(mEUR\\)\\s*638\\s*682"], "company"),
 ("frosta-ag", "founded", "1961 (Unternehmensangabe: Gründung von FRoSTA)", W, "https://www.frosta-ag.com/unternehmen/firmengeschichte/", ["1961 Gründung von FRoSTA"], "company founding"),
 ("hammermuehle-gmbh", "founded", "seit 1967 (Unternehmensangabe: „Bereits seit 1967 stehen wir für handwerkliche deutsche Backkunst“)", W, "https://www.hammermuehle-shop.de/ueber-uns/", ["Bereits seit 1967 stehen wir für handwerkliche deutsche Backkunst"], "company statement"),
 ("ja-natuerlich-naturprodukte-gesellschaft-mbh", "founded", "Marke 1994 (Unternehmensangabe: erste österreichische Bio-Marke gegründet)", W, "https://www.janatuerlich.at/wir-sind-bio/wofuer-wir-stehen/unsere-meilensteine/", ["als erste österreichische Bio-Marke im Jahr 1994 gegründet"], "brand founding"),
 ("kikkoman-trading-europe-gmbh", "employees", "Gruppe: ca. 7.000 weltweit (Kikkoman, Unternehmensangabe)", W, "https://www.kikkoman.de/ueber-kikkoman/unternehmen/kikkoman-gruppe", ["Kikkoman in Zahlen", "Ca. 7.000 Mitarbeiter weltweit"], "group (worldwide)"),
 ("kikkoman-trading-europe-gmbh", "founded", "Gruppe 1917 (Noda Shoyu Co., heute Kikkoman Corporation; Unternehmensangabe)", W, "https://www.kikkoman.de/ueber-kikkoman/unternehmen/kikkoman-geschichte", ["Im Jahr 1917 gründeten die japanischen Familien Mogi und Takanashi die Noda Shoyu"], "group founding, not the European trading GmbH"),
 ("lidl-oesterreich-gmbh", "employees", "> 5.800 in Österreich (Unternehmensangabe)", W, "https://corporate.lidl.at", ["Lidl Österreich in Zahlen", "5.800 Mitarbeiter:innen in Österreich"], "company (Lidl Österreich)"),
 ("lidl-oesterreich-gmbh", "revenue", "> 2 Mrd. € (GJ 2025, Unternehmensangabe)", W, "https://corporate.lidl.at", ["2 Mrd. Euro Umsatz im Geschäftsjahr 2025"], "company"),
 ("lidl-oesterreich-gmbh", "founded", "1998 (Wikidata Q57018091 P571 / de.wikipedia Gründungsdatum; Lidl Österreich)", WP, ("de", "Lidl Österreich"), ["re:Gründungsdatum\\s*=\\s*1998"], "company (Wikidata item matched by P856 = lidl.at); legal entity FN 131556s may be older"),
 ("meica-gmbh", "founded", "seit 1908 (Unternehmensangabe; 2008 100-jähriges Jubiläum)", W, "https://www.meica.de/ueber-uns", ["Meica feiert sein 100jähriges Jubiläum", "Seit 1908 steht Meica"], "company statement"),
 ("noem-ag", "employees", "über 1.000 (Unternehmensangabe, Karriereseite)", W, "https://www.noem.at/karriere", ["+1.000 Mitarbeiter"], "company (scope not stated: AG or group)"),
 ("noem-ag", "revenue", "645 Mio. € (2023, Unternehmensangabe); NÖM AG Jahresabschluss 2023: 534 Mio. € (lt. de.wikipedia)", W, "https://www.noem.at/karriere", ["645 Mio Umsatz im Jahr 2023"], "company statement + differing annual-accounts figure (both recorded)"),
 ("recheis-teigwaren-gmbh", "founded", "1889 (Unternehmensangabe: Gründung der ersten Teigwarenmanufaktur Österreichs)", W, "https://www.recheis.com/ueber-uns/geschichte/", ["re:1889\\s*\\W\\s*Gründung der ersten Teigwarenmanufaktur Österreichs"], "company founding"),
 ("recheis-teigwaren-gmbh", "employees", "rund 100 in Hall in Tirol; Recheis Gruppe fast 200 (Unternehmensangabe)", W, "https://www.recheis.com/ueber-uns/geschichte/", ["An unserem modernen Firmenstandort in Hall in Tirol sind rund 100"], "company site; group figure from press page"),
 ("rila-die-genussentdecker", "founded", "seit 1969 (Unternehmensangabe: „Seit 1969 der Partner für den LEH“)", W, "https://rila.de/ueber-uns/", ["Seit 1969 der Partner für den LEH"], "company statement"),
 ("ruegenwalder-muehle-carl-mueller-gmbh-co-kg", "employees", "892 (2023, Konzern; lt. de.wikipedia, Quelle Konzernabschluss 2023)", WP, ("de", "Rügenwalder Mühle"), ["re:Mitarbeiterzahl\\s*=\\s*892 \\(2023\\)", "Konzernabschluss zum Geschäftsjahr vom 01.01.2023"], "group accounts via Wikipedia (item matched by LEI)"),
 ("ruegenwalder-muehle-carl-mueller-gmbh-co-kg", "revenue", "266,5 Mio. € (2023, Konzern; lt. de.wikipedia, Quelle Konzernabschluss/Unternehmensregister)", WP, ("de", "Rügenwalder Mühle"), ["re:Umsatz\\s*=\\s*266,5 Mio\\. Euro \\(2023\\)", "Konzernabschluss zum Geschäftsjahr vom 01.01.2023"], "group accounts via Wikipedia"),
 ("zum-dorfkrug-produktions-und-handelsgesellschaft-mbh-co-kg", "employees", "rund 200 (Unternehmensangabe, Jobseite)", W, "https://www.zum-dorfkrug.de/jobs", ["Rund 200 Mitarbeitende bilden"], "company"),
 ("aia-spa", "founded", "1968 (Wikidata Q3606861 P571, Agricola Italiana Alimentare)", WD, "Q3606861", ["P571:1968", "P856:aiafood.com"], "company (item matched by P856 = aiafood.com)"),
 ("hamker-vertriebsgesellschaft-mbh", "founded", "Stammhaus 1907 (Heinrich Hamker Lebensmittelwerke; Wikidata Q1510152 / de.wikipedia)", WD, "Q1510152", ["P571:1907", "P856:hamker.de"], "parent/brand company, not the Vertriebsgesellschaft"),
 ("maresi-austria-gmbh", "employees", "71 (2019, lt. de.wikipedia)", WP, ("de", "Maresi (Unternehmen)"), ["re:Mitarbeiterzahl\\s*=\\s*71 \\(2019\\)"], "company (item matched by P856 = maresi.at)"),
 ("maresi-austria-gmbh", "revenue", "79 Mio. € (2020, lt. regal.at via de.wikipedia)", WP, ("de", "Maresi (Unternehmen)"), ["re:Umsatz\\s*=\\s*79 Mio\\. Euro \\(2020\\)", "regal.at"], "company; third-party trade press (REGAL)"),
 ("hofer-kg", "employees", "mehr als 12.000 (Unternehmensangabe, Presseaussendung 20.08.2025)", W, "https://www.hofer.at/ueber-hofer/presse/alle-presseaussendungen/presseaussendungen-unternehmen/2025/service-value-studie", ["(Sattledt, 20.08.2025; HOFER)", "mehr als 12.000 engagierten Mitarbeiter:innen"], "company"),
 ("hofer-kg", "revenue", "5,4 Mrd. € (2025; Unternehmensangabe in bezahlter Anzeige, Die Presse 2026)", W, "https://www.diepresse.com/26002500/das-erlebnis-einkauf-weiter-erfolgreich-umsetzen", ["Anzeige", "2025 ein Rekordjahr hingelegt", "Mit 5,4 Mrd. Euro Umsatz bei 540 Filialen"], "company-supplied advertorial in third-party outlet (labelled)"),
 ("dm-drogerie-markt-gmbh", "employees", "6.844 (dm Österreich, GJ 2024/25, Unternehmensangabe); Ländergruppe dm Österreich + Verbundene Länder 29.120", W, ["https://pr.dm.at/news-dm-weiterhin-lieblingsdrogerie-der-oesterreicher?id=225897&l=deutsch&menueid=5306", "https://www.dm.at/unternehmen/zahlen-und-fakten/unternehmenszahlen"], ["6.844 Mitarbeiter", "29.120"], "company (AT) + group"),
 ("dm-drogerie-markt-gmbh", "revenue", "1,374 Mrd. € (dm Österreich, GJ 2024/25); Ländergruppe 5,851 Mrd. €", W, ["https://pr.dm.at/news-dm-weiterhin-lieblingsdrogerie-der-oesterreicher?id=225897&l=deutsch&menueid=5306"], ["ein Umsatz von 1,374 Mrd. Euro erzielt", "5,851 Milliarden Euro"], "company (AT) + group"),
 ("dm-drogerie-markt-gmbh", "founded", "1976 (Unternehmensangabe: erste dm Filiale in Österreich)", W, ["https://pr.dm.at/news-dm-weiterhin-lieblingsdrogerie-der-oesterreicher?id=225897&l=deutsch&menueid=5306", "https://www.dm.at/unternehmen/zahlen-und-fakten/unternehmenszahlen"], ["eröffnete im Jahr 1976 die erste Filiale in Österreich"], "start of Austrian business (first store), not legal-entity date"),
 ("heiploeg-international-bv", "founded", "Ursprung vor 1900 (Familienbetriebe Heidema und Van der Ploeg, Zoutkamp); Name Heiploeg seit Anfang der 1970er (Unternehmensangabe)", W, "https://heiploeg.com/en-us/company", ["goes back to before 1900", "Heiploeg became the name of the company in the early 70s"], "company history statement"),
 ("iglo-austria-gmbh", "employees", "ca. 80 in Österreich (Unternehmensangabe); Nomad Foods Gruppe ca. 4.300", W, "https://www.iglo.at/wir-sind-iglo/jobs-und-karriere", ["ca. 80 Mitarbeitern in Österreich", "4.300 in der Nomad Foods Gruppe"], "company + group"),
 ("iglo-austria-gmbh", "revenue", "knapp 120 Mio. € (2020, Unternehmensangabe, Presseaussendung 04.08.2021)", PDF, "https://www.iglo.at/_/media/project/bluesteel/iglo-at/ueberuns/presse/files/210804_pa_jahresrckblick.pdf", ["Umsatz um 20 Prozent auf knapp 120 Mio. Euro", "Iglo Austria GmbH"], "company"),
]
# extra evidence that must hold for a decision (second source) — checked, recorded, not required for apply
EXTRA = {("recheis-teigwaren-gmbh", "employees"): (W, "https://www.recheis.com/presse-oeffentlichkeit/", ["Die gesamte Recheis Gruppe beschäftigt derzeit fast 200 Mitarbeitende"]),
         ("noem-ag", "revenue"): (WP, ("de", "NÖM"), ["534 Millionen", "Jahresabschluss 2023"])}
REJECT = {
 "andros-deutschland-gmbh": "andros.de/ueber-uns gives only per-site headcounts (Breuberg ~300, others ~250/~200), no company total → not summed",
 "landtmann-s-feine-patisserie": "'Die Familie Querfeld: 400 Mitarbeiter:innen. 7 Café-Restaurants' = Querfeld family business (cafés), not the patisserie entity",
 "lpp-lotao-gmbh": "lotao.com redirects to biozentrale.de ('Seit 1976') = Bio-Zentrale Naturprodukte GmbH, a different entity (see T1835)",
 "morgentau-biogemuese-gmbh": "'Echt BIO – seit 1986' = organic since 1986, not a founding statement",
 "tress-lebensmittel-gmbh-co-kg#founded": "'BIO ist bei uns Familiensache. Seit 1950' = organic since 1950, not a founding statement",
 "followfood-gmbh#founded": "Steckbrief 'Gründung 2007' conflicts with filled legal-entity date 2001-06-06 (GLEIF) → kept, conflict recorded",
 "revo-foods#founded": "team page 'Year Founded 2020' vs Firmenbuch entry 2021-02-24 (filled) → kept, conflict recorded",
 "efko-frischfrucht-und-delikatessen-gmbh#founded": "efko.at/geschichte '1976 Gründung der efko Frischfrucht und Delikatessen GmbH' vs filled GLEIF creationDate 1973-07-02 → conflict recorded, not changed",
 "iss-mich-gmbh#founded": "'Manufaktur seit 2014' vs filled Firmenbuch 2017-05-23 (GmbH) → kept",
 "frosta-ag#founded-wikidata": "Wikidata Q1470518 P571 1905 = Nordstern AG (bought 1984, per frosta-ag.com history) → company's own 1961 used instead",
 "billa-aktiengesellschaft#revenue": "rewe-group.at gives only BILLA growth % (+1,4 % 2025), no absolute revenue; billa.at now says 'über 30.000 Mitarbeiter' vs filled 'ca. 20.000 (2021, Wikidata)' → existing value not overwritten (newer figure recorded here)",
 "mpreis-warenvertriebs-gmbh#revenue": "only de.wikipedia '1 Mrd. Euro (2022)' citing a Jan-2022 wirtschaftszeit.at article → year ambiguous, not taken",
 "a-darbo-ag#revenue": "only de.wikipedia 'ca. 197 Mio. Euro' (top.tirol, no year) → not taken",
 "bonne-maman": "row = Andros (LEI): de.wikipedia 'etwa 7.400 / etwa 2 Mrd.' (no year) vs en.wikipedia '10,000 (2021) / €2.4bn (2020)' → conflicting, group, not taken",
 "aia-spa#employees/revenue": "it.wikipedia 'dipendenti 724' / '3,77 miliardi' (registroaziende.it, year unclear, implausible pair) → not taken",
 "hamker-vertriebsgesellschaft-mbh#employees": "de.wikipedia 'ca. 900 (2007)' = Heinrich Hamker Lebensmittelwerke 2007 → stale, other entity, not taken",
 "inzersdorfer-nahrungsmittelwerke#employees": "Wikidata P1128 140 without point in time → not taken",
 "greenforce-future-food-ag": "own site has no figures; only aggregators (handelsregister.ai/northdata = register scrapes) and PR boilerplate ('rund 100 Mitarbeitende', fabino.de, undated) → not taken",
 "iglo-austria-gmbh#employees": "iglo.at/wir-sind-iglo/jobs-und-karriere ('ca. 80 Mitarbeitern in Österreich', search-index copy) now redirects to the home page → not re-verifiable, not taken",
 "iglo-austria-gmbh#revenue-2025": "firmenakte.at shows Umsatzerlöse 2025 ~129 Mio. € (aggregator of filed accounts) → not taken; own 2020 press figure used",
 "frosta-tiefkuehlkost-gmbh": "FRoSTA AG key figures not transferred to the subsidiary GmbH",
 "spar.at/unternehmen/daten-fakten": "HTTP 403 → not bypassed (used spar.at/unternehmen, 200)",
 "unilever-austria-gmbh": "robots.txt disallows the site for our UA → not crawled",
 "strauss-gmbh": "straussjosef.it TLS error (unexpected EOF) → no data",
 "hildegard-gruenkraft-naturprodukte": "site timed out",
 "js-only/no-figures": "amlachernudel.com, andros-fruit.eu, bio-gourmet.com, every-foods.com, feel-food.com, gudesserts.com, harvestmoon.de, kasnudl.at, kernbeisser.at, maresi.at, shoppu.mochi.at, stanglnudeln.at, delidip.com, ehrenwort.at, fratelli-barbaro.at, hamker.de, knoedelwerkstatt.at, lamercantile.com, pastacecchin.it, reis-fit.de, youcook-food.com, xn--brtchen-boutique-nwb.at: no employee/revenue/founding statement in server-rendered HTML",
}
_last = {}; _rob = {}; _cache = {}
def _wait(host):
    w = 1.1 - (time.time() - _last.get(host, 0))
    if w > 0: time.sleep(w)
    _last[host] = time.time()
def fetch(url, binary=False, retry=True):
    try: return _fetch(url, binary)
    except urllib.error.HTTPError as e:  # one polite retry (same UA, after 6 s) on transient 403/429/5xx — no header/UA tricks
        if retry and e.code in (403, 429, 500, 502, 503, 504): time.sleep(6); return _fetch(url, binary)
        raise
def _fetch(url, binary=False):
    host = urllib.parse.urlparse(url).netloc; _wait(host)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-AT,de;q=0.9,en;q=0.6"})
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read(8_000_000); return (b if binary else b.decode(r.headers.get_content_charset() or "utf-8", "replace")), r.geturl()
def robots_ok(url):
    p = urllib.parse.urlparse(url); base = f"{p.scheme}://{p.netloc}"
    if base not in _rob:
        rp = urllib.robotparser.RobotFileParser()
        try: rp.parse(fetch(base + "/robots.txt")[0].splitlines())
        except urllib.error.HTTPError as e:  # RFC 9309: 4xx = no restriction (401/403 treated as disallow, conservative)
            if e.code in (401, 403): rp.disallow_all = True
            else: rp.allow_all = True
        except Exception: rp.allow_all = True
        _rob[base] = rp
    return _rob[base].can_fetch(UA, url)
def label(e_kind, src):
    if "diepresse.com" in str(src): return "third-party outlet (Die Presse, paid advertorial)"
    return {"web": "own site", "pdf": "own site (PDF)", "wikipedia": "Wikipedia", "wikidata": "Wikidata"}[e_kind]
def norm(t): return re.sub(r"\s+", " ", t.replace("\xad", "").replace("\xa0", " ").replace("\u202f", " ").replace("\u2009", " "))
def htext(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</td>|</tr>|</section>", "\n", h)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", h)))
def get_text(kind, src):
    key = (kind, json.dumps(src))
    if key in _cache: return _cache[key]
    if kind == W:
        if not robots_ok(src): raise RuntimeError("robots.txt disallows")
        h, final = fetch(src); out = (htext(h), final)
    elif kind == PDF:
        if not robots_ok(src): raise RuntimeError("robots.txt disallows")
        b, final = fetch(src, binary=True)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(b); f.flush(); t = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
        out = (norm(t), final)
    elif kind == WP:
        lang, title = src
        d = json.loads(fetch(f"https://{lang}.wikipedia.org/w/api.php?action=parse&prop=wikitext|revid&section=0&format=json&page=" + urllib.parse.quote(title))[0])
        out = (norm(d["parse"]["wikitext"]["*"]), f"https://{lang}.wikipedia.org/w/index.php?oldid={d['parse'].get('revid')}")
    elif kind == WD:
        e = json.loads(fetch(f"https://www.wikidata.org/wiki/Special:EntityData/{src}.json")[0])["entities"][src]["claims"]
        parts = [f"P571:{c['mainsnak']['datavalue']['value']['time'][1:5]}" for c in e.get("P571", []) if c["mainsnak"].get("datavalue")]
        parts += [f"P856:{urllib.parse.urlparse(c['mainsnak']['datavalue']['value']).netloc.replace('www.', '')}" for c in e.get("P856", []) if c["mainsnak"].get("datavalue")]
        out = (" | ".join(parts), f"https://www.wikidata.org/wiki/{src}")
    _cache[key] = out; return out
def check(kind, srcs, must):
    srcs = srcs if isinstance(srcs, list) else [srcs]; errs = []
    for s in srcs:
        try: t, final = get_text(kind, s)
        except Exception as e: errs.append(f"{s}: {str(e)[:100]}"); continue
        miss = [m for m in must if not (re.search(m[3:], t) if m.startswith("re:") else norm(m) in t)]
        quotes = []
        for m in must:
            x = re.search(m[3:], t) if m.startswith("re:") else re.search(re.escape(norm(m)), t)
            if x: quotes.append(t[max(0, x.start() - 120): x.end() + 120])
        if not miss: return True, final, quotes, None
        errs.append(f"{s}: phrases not found {miss}")
    return False, None, [], "; ".join(errs)
if __name__ == "__main__":
    d = json.load(open("data/companies.json", encoding="utf-8")); J = {r["slug"]: r for r in d}
    before = {k: sum(1 for r in d if (r.get(k) or "").strip()) for k in ("employees", "revenue", "founded")}
    ev = []; U = {}
    for slug, field, value, kind, src, must, scope in D:
        rec = {"slug": slug, "field": field, "value": value, "kind": kind, "source": src, "must": must, "scope": scope, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        if slug not in J: rec.update(decision="rejected", reason="slug not in dataset"); ev.append(rec); continue
        if (J[slug].get(field) or "").strip(): rec.update(decision="skipped", reason=f"field already filled: {J[slug][field]!r}"); ev.append(rec); continue
        ok, final, quotes, err = check(kind, src, must)
        rec.update(url=final, quote=quotes)
        if ok:
            x = EXTRA.get((slug, field))
            if x:
                ok2, f2, q2, e2 = check(*x); rec["extra_evidence"] = {"source": x[1], "url": f2, "quote": q2, "ok": ok2, "error": e2}
                if not ok2: value = value.split(";")[0].strip(); rec["value"] = value; rec["note"] = "second-source part dropped (not re-verified)"
            rec["decision"] = "accepted"; U.setdefault(slug, {})[field] = (value, final, scope, kind)
        else: rec.update(decision="rejected", reason=err)
        ev.append(rec); print(rec["decision"], slug, field, err or "")
    for slug, fields in U.items():
        r = J[slug]
        for field, (value, url, scope, kind) in fields.items():
            if (r.get(field) or "").strip(): continue
            r[field] = value; r[f"{field}_source"] = f"{url} ({label(kind, url)}; scope: {scope}; T1938)"
            srcs = [url] + ([EXTRA[(slug, field)][1]] if (slug, field) in EXTRA and isinstance(EXTRA[(slug, field)][1], str) else [])
            r["sources"] = list(dict.fromkeys((r.get("sources") or []) + srcs))
    open("data/companies.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    p = "data/companies.csv"; raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys())
    for r in rows:
        for k in ("employees", "revenue", "founded"):
            if r["slug"] in U and k in U[r["slug"]] and not r[k].strip(): r[k] = J[r["slug"]][k]
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
    after = {k: sum(1 for r in d if (r.get(k) or "").strip()) for k in ("employees", "revenue", "founded")}
    bysrc = {}
    for e in ev:
        if e["decision"] == "accepted":
            k = label(e["kind"], e["source"]); bysrc.setdefault(e["field"], {}); bysrc[e["field"]][k] = bysrc[e["field"]].get(k, 0) + 1
    json.dump({"run": "Daten-Squad T1938", "generated_at": NOW, "rules": __doc__, "before": before, "after": after, "by_source": bysrc,
               "evidence": ev, "rejects_and_dead_ends": REJECT,
               "probe_files": ["scripts/facts_T1938/crawl_out.json", "scripts/facts_T1938/wikidata_out.json", "scripts/facts_T1938/wikipedia_out.json"]},
              open("raw/companies_facts_2026-10-16T1938.json", "w"), ensure_ascii=False, indent=1)
    print("before", before, "after", after); print("by source", bysrc)
