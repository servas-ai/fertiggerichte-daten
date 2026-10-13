import json, datetime
T = datetime.date.today().isoformat()
def F(v, src, conf): return {"value": v, "sources": src if isinstance(src, list) else [src], "confidence": conf}
NF = lambda: F(None, [], "none")
P = [
 dict(slug="gms-gourmet", name="GMS GOURMET GmbH", plant="St. Pölten, Zdarskystraße 3 (AT 30733 EG)",
  technology=F(["Heißabfüllung + Pasteurisation (gekühlte Fertiggerichte)", "MAP-Schalenversiegelung (CPET/PP Ein-/Mehrkammerschalen)", "Sterilisation von Fertiggerichten in Kunststoffverbundschalen (Retort/Autoklav)", "Tiefkühlung (TK-Fertiggerichte, PP-Beutel)"],
     ["https://www.gourmet.at/fileadmin/public/dachmarke/Home_und_Unser_Angebot/Zertifikate/IFS-St._P%C3%B6lten-g%C3%BCltig_bis_07022027.pdf", "https://www.gourmet.at/fileadmin/public/dachmarke/Home_und_Unser_Angebot/Zertifikate/IFS_St._Poelten_gueltig_bis_07.02.2021.pdf"], "high"),
  machines=F(None, [], "none"),
  ifs=F({"standard": "IFS Food", "level": "unbekannt (2019: 89,34 % = Foundation Level)", "valid_until": "2027-02-07"}, "https://www.gourmet.at/fileadmin/public/dachmarke/Home_und_Unser_Angebot/Zertifikate/IFS-St._P%C3%B6lten-g%C3%BCltig_bis_07022027.pdf", "high"),
  brc=NF(), other_certs=F(["Bio (seit 1997)", "MSC", "ASC", "Fairtrade", "ISO 9001", "ISO 14001", "ISO 22000", "ISO 50001", "FSSC 22000"], "https://www.wlw.de/de/firma/gms-gourmet-gmbh-117012", "medium"),
  sourcing=NF(), recalls=F([], ["https://www.ages.at/mensch/produktwarnungen-produktrueckrufe"], "low"),
  notes="Teile ausgelagert, Brokeraktivitäten nicht GFSI-zertifiziert (lt. IFS-Zertifikat)."),
 dict(slug="rewe-austria-fleischwaren", name="Rewe Austria Fleischwaren GmbH", plant="Eberstalzell (AT 42152 EG)",
  technology=F(["Zerlegung Schwein/Rind", "Wurst- und Convenience-Rohstoff-Produktion"], "https://rewe-group.at/de/newsroom/2023/01/staerkung-des-standorts-eberstalzell-fleischproduktion-von-st-veit-wird-gebuendelt", "medium"),
  machines=NF(), ifs=F({"standard": "IFS Food", "level": "unbekannt"}, ["https://jobborse.co.at/leiter-qualitatssicherung_oberosterreich-c14845561/2026-10-rewe-fleischwaren_i4237726191"], "medium"),
  brc=NF(), other_certs=F(["Bio", "AMA-Gütesiegel", "Ohne Gentechnik (OGT)"], "https://jobborse.co.at/teamleiterin_oberosterreich-c14845561/2026-10-rewe-fleischwaren_i4237725612", "medium"),
  sourcing=F("Konventionelles Schwein- und Rindfleisch; AMA-Programm nahe AT-Herkunft, Anteil nicht veröffentlicht", "https://rewe-group.at/de/newsroom/2023/01/staerkung-des-standorts-eberstalzell-fleischproduktion-von-st-veit-wird-gebuendelt", "low"),
  recalls=F([], [], "low")),
 dict(slug="rewe-genusskueche", name="Rewe Austria Genussküche GmbH", plant="Traiskirchen",
  technology=F(["2 Produktionslinien: Heißluft", "pasteurisierender Mikrowellen-Tunnel", "ca. 1,3 Mio. Portionen/Monat, ~4.000 m², ~120 MA (seit 2017)"], "https://rewe-group.jobs/de/wir-als-arbeitgeber/fachbereiche/fleischwaren/genusskueche", "high"),
  machines=NF(), ifs=NF(), brc=NF(), other_certs=NF(), sourcing=F("Fleisch-Rohstoff aus REWE Fleischwaren (Eberstalzell/Traiskirchen) – konzernintern", "https://rewe-group.jobs/de/wir-als-arbeitgeber/fachbereiche/fleischwaren/genusskueche", "low"), recalls=F([], [], "low")),
 dict(slug="wiesbauer-gourmet", name="Wiesbauer Gourmet Gastro GmbH", plant="Sitzenberg-Reidling",
  technology=F(["Sous-vide: vakuumversiegeltes Fleisch, 50–70 °C, viele Stunden im Wasserbad", "große Wasserkochanlage („europaweit einzigartig“ lt. Firma)"], ["https://cdn.wiesbauer.at/user_upload/wiesbauer/Presse/Firmen_Folder_Issuu.pdf", "https://www.wiesbauer-sousvide.at/", "https://medianet.at/news/retail/wiesbauer-begeistert-mit-sous-vide-gegartem-schinken-braten-59940.html"], "high"),
  machines=NF(), ifs=F({"standard": "IFS Food", "level": "unbekannt", "since": "> 10 Jahre"}, "https://cdn.wiesbauer.at/user_upload/wiesbauer/Presse/Firmen_Folder_Issuu.pdf", "medium"),
  brc=NF(), other_certs=NF(), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="wiesbauer", name="Wiesbauer österreichische Wurstspezialitäten GmbH", plant="Wien-Liesing, Laxenburger Straße 256",
  technology=F(["Wurst- und Fleischwarenproduktion"], "https://liesing.spoe.wien/artikel/betriebsbesuch-bei-wiesbauer-tradition-qualitaet-und-innovation-in-wien-liesing", "medium"),
  machines=NF(), ifs=F({"standard": "IFS Food", "level": "unbekannt"}, "https://liesing.spoe.wien/artikel/betriebsbesuch-bei-wiesbauer-tradition-qualitaet-und-innovation-in-wien-liesing", "medium"),
  brc=NF(), other_certs=NF(), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="blasko", name="Wilhelm Blasko CONVENIENCE-Fertiggerichte GmbH", plant="Bruck an der Mur (+ Oberwaltersdorf, Villach)",
  technology=F(["Manufaktur-Küche, täglich frisch gekocht", "Panieren + Backen in Pflanzenöl", "Frisch, Heiße Theke, TK und SB-Convenience"], ["https://www.blasko.at/produktion/qualitaet", "https://www.brandensteincom.at/blasko-convenience-traditionelle-hausmannskost-zu-100-prozent-aus-oesterreich-fuer-die-gastronomie-hotellerie/"], "high"),
  machines=NF(), ifs=F({"standard": "IFS Food v8", "level": "höchstes Niveau (Higher Level) lt. Firma", "year": 2026}, "https://www.blasko.at/produktion/zertifizierungen", "high"),
  brc=NF(), other_certs=F(["FSC-Kartons", "100 % CO2-neutraler Strom"], "https://www.blasko.at/produktion/zertifizierungen", "high"),
  sourcing=F("100 % österreichisches Rind- und Schweinefleisch, Frischfleisch vom Mutterbetrieb Marcher Fleischwerke; Eier aus Bodenhaltung", ["https://www.brandensteincom.at/blasko-convenience-traditionelle-hausmannskost-zu-100-prozent-aus-oesterreich-fuer-die-gastronomie-hotellerie/", "https://www.blasko.at/produktion/qualitaet"], "high"),
  sourcing_at=True, recalls=F([], [], "low")),
 dict(slug="karnerta", name="KARNERTA GmbH", plant="Klagenfurt, Südring 334",
  technology=F(["Frischteigwaren-Produktionsstraße (vorgegart, frisch, TK)", "eigene Fleischzerlegung (Rinder-/Schweinehälften)"], ["https://www.karnerta.at/produkte/teigwaren/", "https://www.karnerta.at/unternehmen/"], "high"),
  machines=NF(), ifs=F({"standard": "IFS Food", "level": "Higher Level (2025, Teigwaren)", "since": 2003}, "https://frischteigwaren.at/", "high"),
  brc=NF(), other_certs=F(["Bio", "Cibus (Herkunft)", "V-Label vegetarisch/vegan"], "https://frischteigwaren.at/", "high"),
  sourcing=F("Kärntner Fleisch, rückverfolgbar bis zum Hof; vorwiegend regionale Lieferanten, wenn möglich AT", "https://www.karnerta.at/unternehmen/", "high"),
  sourcing_at=True, recalls=F([], [], "low")),
 dict(slug="landena", name="Landgenossenschaft Ennstal LANDENA KG", plant="Stainach-Pürgg (+ Landena Wels Trocken)",
  technology=F(["Konserven (Dose 24 g–3 kg, Glas) – Sterilisation in Autoklaven (neue Autoklaven: −35 % Wasser, −25 % Energie)", "Tiefkühl-Fertiggerichte", "Schalen- und Beutelverpackung", "Wurst-Snacks", "~30.000 t Fertiggerichte/Jahr, ~500 MA"], ["https://www.landena.at/de/produkte/", "https://www.landena.at/de/produkte/produkte-in-der-dose/", "https://www.landena.at/de/unternehmen/nachhaltigkeit/"], "high"),
  machines=F("Autoklaven (Hersteller nicht genannt)", "https://www.landena.at/de/unternehmen/nachhaltigkeit/", "medium"),
  ifs=F({"standard": "IFS", "level": "unbekannt"}, "https://www.landena.at/de/produkte/trockensortiment/", "medium"),
  brc=NF(), other_certs=F(["Bio", "HACCP", "Halal auf Wunsch (Suppen, Wels)"], "https://www.landena.at/de/produkte/trockensortiment/", "medium"),
  sourcing=F("Enge Zusammenarbeit mit Bauern aus der Region und lokalen Lieferanten; Anteil nicht veröffentlicht", "https://www.landena.at/de/", "medium"), recalls=F([], [], "low")),
 dict(slug="hink", name="Hink GmbH", plant="Wien-Floridsdorf, Otto-Beyschlag-Gasse 3",
  technology=F(["Handarbeit, Kleinmengen (Pasteten, Terrinen)"], "https://hink.wien/pages/manufaktur", "high"),
  machines=NF(), ifs=F(None, [], "none"), brc=NF(), other_certs=NF(), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="greisinger", name="Greisinger GmbH", plant="Münzbach, Klamer Straße 10 (59.000 m², seit 1995)",
  technology=F(["Fleisch-, Wurst- und Selchwaren"], "https://www.greisinger.com/fuer-unsere-partner/betriebsdaten/", "medium"),
  machines=NF(), ifs=F({"standard": "IFS Food", "level": "höheres Niveau (Higher Level) lt. Firma"}, "https://www.greisinger.com/qualitaet-nachhaltigkeit/auszeichnungen-zertifikate/", "medium"),
  brc=F({"standard": "BRC", "grade": "unbekannt"}, "https://www.greisinger.com/qualitaet-nachhaltigkeit/auszeichnungen-zertifikate/", "medium"),
  other_certs=NF(), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="hochreiter", name="Hochreiter Quality Meat Factory GmbH", plant="Reichenthal (Zerlegung) / Bad Leonfelden (Fleischwaren)",
  technology=F(["zentrales Fleisch-Einkaufs- und Zerlegezentrum (QMF)", "Slicen + Verpacken in Folie/MAP, IQF-Fleischerzeugnisse (Hochreiter Fleischwaren)"], ["https://www.hochreiter.cc/wp-content/uploads/2023/04/59503msIFSFood_V7_de-1.pdf", "https://www.hochreiter-gruppe.at/"], "high"),
  machines=NF(), ifs=F({"standard": "IFS Food v7", "level": "Higher Level, 95,83 % (Schwesterbetrieb Hochreiter Fleischwaren)", "year": 2023}, "https://www.hochreiter.cc/wp-content/uploads/2023/04/59503msIFSFood_V7_de-1.pdf", "medium"),
  brc=NF(), other_certs=F(["QS (QMF, 2022)"], "https://www.hochreiter.cc/wp-content/uploads/2022/02/QS-QMF-bis-29.12.2022_2022.pdf", "medium"), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="hubers-landhendl", name="Hubers Landhendl GmbH", plant="Pfaffstätt (OÖ)",
  technology=F(["integriert: Schlachtung, Zerlegung, Verarbeitung Geflügel"], "https://huberslandhendl.at/uber-uns/downloads/", "high"),
  machines=NF(), ifs=F({"standard": "IFS Food", "level": "unbekannt", "note": "online gelistetes Zertifikat 2019–2020, aktuelles nicht geprüft"}, "https://huberslandhendl.at/uber-uns/downloads/", "medium"),
  brc=NF(), other_certs=F(["AMA-Gütesiegel Hühnerfleisch", "AMA-Gütesiegel Kochpökelware", "GVO-frei"], "https://huberslandhendl.at/uber-uns/downloads/", "high"),
  sourcing=F("AMA-Geflügel: in AT geschlüpft, aufgezogen, geschlachtet, verarbeitet", "https://huberslandhendl.at/", "high"), sourcing_at=True,
  recalls=F([{"date": "2026-06-03", "product": "FairHOF Chicken Wings 500 g / Gewürzte Hühner Unterkeulen 400 g (Hofer)", "reason": "mögliche Salmonellen", "lot": "6152007"}], ["https://www.nachrichten.at/oberoesterreich/hofer-ruft-hubers-landhendl-wegen-salmonellengefahr-zurueck;art4,4177843", "https://www.ages.at/mensch/produktwarnungen-produktrueckrufe/produkt/fairhof-chicken-wings-500-g-fairhof-gewuerzte-huehner-unterkeulen-400-g"], "high")),
 dict(slug="graninger", name="Graninger Holding GmbH", plant="Frastanz/Feldkirch (Vbg.)",
  technology=F(["Tiefkühl-Fertiggerichte/Komponenten (z. B. Kalbsrahmspätzle, Brätknödel)"], ["https://shop.transgourmet.at/catalog2/products/196566/tiefkuhlprodukte/tk-fertiggerichte/tk-fertiggerichte/graninger-kalbsrahmspatzle-vorgekocht-tiefgekuhlt-1-kg"], "medium"),
  machines=NF(), ifs=F(None, [], "none"), brc=NF(), other_certs=NF(), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="radatz", name="Radatz - Feine Wiener Fleischwaren GmbH", plant="Wien",
  technology=F(["Fleisch- und Wurstwaren"], "https://www.radatz.at/b2b", "medium"), machines=NF(),
  ifs=F({"standard": "IFS Food", "level": "unbekannt", "since": 2003}, "https://www.radatz.at/ueber-uns/qualitaet-nachhaltigkeit", "high"),
  brc=NF(), other_certs=F(["AMA-Gütesiegel (teilweise)"], "https://www.radatz.at/ueber-uns/qualitaet-nachhaltigkeit", "high"), sourcing=NF(), recalls=F([], [], "low")),
 dict(slug="wech", name="Wech-Geflügel GmbH", plant="Kärnten (KTH + WGG)",
  technology=F(["Geflügelschlachtung und -verarbeitung"], "https://www.wech.at/wissen/ifs-food", "medium"), machines=NF(),
  ifs=F({"standard": "IFS Food", "level": "unbekannt", "sites": ["KTH", "WGG"]}, "https://www.wech.at/wissen/ifs-food", "high"),
  brc=NF(), other_certs=F(["AMA-Gütesiegel Geflügelfleisch + Fleischerzeugnisse"], "https://www.wech.at/wissen/ama-guetesiegel", "high"),
  sourcing=F("AMA-Geflügel = österreichische Herkunft", "https://www.wech.at/wissen/ama-guetesiegel", "high"), sourcing_at=True, recalls=F([], [], "low")),
 dict(slug="heiploeg", name="Heiploeg International B.V.", plant="Zoutkamp (NL), Panserweg 14",
  technology=F(["Garnelen-Verarbeitung, Verpackung, Konservierung"], "https://heiploeg.com/en-us/quality/certification", "medium"), machines=NF(),
  ifs=NF(), brc=F({"standard": "BRCGS Food Issue 9", "grade": "A+", "valid_until": "2027-06-29"}, "https://heiploeg.com/Portals/10/PDF_files/2026/PDF%202026%20RC%2072856-2010-ABRC-NLD-ACCREDIA_BRC%20Food-20260506.pdf", "high"),
  other_certs=F(["MSC CoC (MSC-C-51664, bis 2028-08-24)", "ASC CoC (ASC-C-00489, bis 2028-08-24)"], ["https://heiploeg.com/Portals/10/PDF_files/2025/MSC-C-51664%20Heiploeg%20valid%20till%202028-08-24.pdf", "https://heiploeg.com/Portals/10/PDF_files/2025/ASC-C-00489%20Heiploeg%20till%202028-08-24.pdf"], "high"),
  sourcing=F("Wildfang/Aquakultur mit MSC/ASC-Rückverfolgbarkeit (Import)", "https://heiploeg.com/en-us/quality/certification", "medium"), recalls=F([], [], "low")),
]
CRIT = {"zertifizierung": "max 35: IFS Higher Level / BRCGS A/A+ = 35, IFS/BRC (Stufe unbekannt) = 25, kein Nachweis gefunden = 0",
        "zusatz_siegel": "max 10: je 3 Punkte für AMA-Gütesiegel, Bio, MSC/ASC, weitere (max 10)",
        "herkunft": "max 25: dokumentiert 100 % AT/regional rückverfolgbar = 25, 'vorwiegend regional' = 15, Import mit Zertifizierung = 12, unbekannt = 5",
        "technologie_transparenz": "max 15: konkrete Verfahren öffentlich (≥2 belegt) = 15, eines = 8, keines = 0",
        "rueckrufe": "max 15: kein Rückruf in AGES/Presse gefunden (letzte 24 Monate) = 15, ein Rückruf = 5",
        "potenzial": "Score, wenn alle 'unbekannt'-Felder auf den bestmöglichen Wert fallen (Obergrenze bei aktueller Datenlage); Differenz = Recherche-/Transparenzlücke"}
def score(p):
    i, b = p["ifs"]["value"] or {}, p["brc"]["value"] or {}
    lv = (str(i.get("level", "")) + str(b.get("grade", ""))).lower()
    c = 35 if ("higher" in lv or "höch" in lv or "a+" in lv or lv.endswith("a")) else 25 if (i or b) else 0
    oc = p["other_certs"]["value"] or []
    s = " ".join(oc).lower()
    z = min(10, 3 * sum(k in s for k in ("ama", "bio", "msc")) + (1 if len(oc) > 3 else 0))
    sv = (p["sourcing"]["value"] or "").lower()
    h = 25 if p.get("sourcing_at") else 15 if "region" in sv else 12 if ("msc" in sv or "asc" in sv) else 5
    tv = p["technology"]["value"] or []
    t = 15 if len(tv) >= 2 else 8 if tv else 0
    r = 5 if p["recalls"]["value"] else 15
    sc = c + z + h + t + r
    pot = (35 if c < 35 else c) + (10 if not oc else z) + (25 if not p["sourcing"]["value"] else h) + (15 if t < 15 else t) + r
    return sc, pot, {"zertifizierung": c, "zusatz_siegel": z, "herkunft": h, "technologie_transparenz": t, "rueckrufe": r}
for p in P:
    p["quality_score"], p["potential_score"], p["score_breakdown"] = score(p)
    p.pop("sourcing_at", None)
P.sort(key=lambda p: -p["quality_score"])
out = {"generated": T, "method_de": CRIT, "note_de": "Nur belegte Angaben; 'value: null' = nicht gefunden (nicht 'nicht vorhanden'). Maschinenhersteller (Multivac, Krones, JBT, Hiperbaric) wurden in keiner öffentlichen Referenz einem dieser Betriebe zugeordnet. Rückrufe: Suche AGES/VKI/Presse, RASFF nicht systematisch geprüft.", "producers": P}
json.dump(out, open("analysis/producer_quality.json", "w"), ensure_ascii=False, indent=1)
L = [f"# Hersteller-Qualitätsprofil ({T})", "", "Bewertung 0–100 nach transparenten Kriterien. Nur belegte Angaben, jede mit Quelle und Sicherheit in `producer_quality.json`.", "", "| # | Hersteller | Werk | Score | Potenzial | Zertifizierung | Herkunft | Rückrufe |", "|---|---|---|---|---|---|---|---|"]
for k, p in enumerate(P, 1):
    i = p["ifs"]["value"] or p["brc"]["value"] or {}
    cert = (i.get("standard", "") + " " + str(i.get("level", i.get("grade", "")))).strip() or "nicht gefunden"
    L.append(f"| {k} | {p['name']} | {p['plant']} | **{p['quality_score']}** | {p['potential_score']} | {cert} | {p['sourcing']['value'] or 'unbekannt'} | {'; '.join(r['date']+' '+r['reason'] for r in p['recalls']['value']) or 'keine gefunden'} |")
L += ["", "## Kriterien", ""] + [f"- **{k}**: {v}" for k, v in CRIT.items()] + ["", "## Hinweise", "", out["note_de"]]
open("analysis/producer_quality_de.md", "w").write("\n".join(L) + "\n")
for p in P: print(p["quality_score"], p["potential_score"], p["name"])
