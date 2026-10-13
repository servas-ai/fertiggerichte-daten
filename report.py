import json
d=json.load(open('scored.json')); S=json.load(open('packaging_stats.json'))
M=[x for x in d if x['is_meal']]
L=[]; w=L.append
w("# Fertiggerichte nach Verpackungsart – Gesundheits-KPI-Vergleich\n")
w(f"Stand 12.10.2026 · {len(d)} Produkte nach Dedupe (davon {len(M)} Gerichte, {len(d)-len(M)} Nicht-Gerichte wie Teigblätter oder Kräuter ausgeschlossen) · Quellen: billa.json, spar.json, spar_live.json, hofer_lidl.json, frozen_quick.json, other.json\n")
w("## Medianwerte je Verpackungsart\n")
w("| Typ | n | Protein g/100g | Protein g/100kcal | Salz g/100g | ges. Fett | Zucker | Ballaststoffe (n) | €/kg | € pro 10 g Protein | Health-Score |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
for t,s in sorted(S.items(),key=lambda kv:-(kv[1]['health_score'][0] or 0)):
    g=lambda f:'–' if s[f][0] is None else f"{s[f][0]}"
    w(f"| {t} | {s['n']} | {g('protein_100')} | {g('protein_per_100kcal')} | {g('salt_100')} | {g('satfat_100')} | {g('sugar_100')} | {g('fiber_100')} ({s['fiber_100'][1]}) | {g('price_per_kg')} | {g('price_per_10g_protein')} | {g('health_score')} |")
w("""
**Achtung:** Bei Trocken-/Instant-Produkten beziehen sich die Nährwerte oft auf das **Trockenpulver**. Das bläht Protein und Salz pro 100 g auf, deshalb ist dort *Protein pro 100 kcal* die faire Kennzahl. „Unklar“ heißt, dass die Quelle keine Kategorie oder Lagerart nennt. „Glas“ hat nur n=10, das ist nicht belastbar.

## Kernaussagen
1. **Sous-vide (z. B. BILLA Genusswelt Rindsbackerl, Ripperl)** liegt beim Protein klar vorne, mit ~14,5 g/100 g und ~11 g pro 100 kcal. Der Health-Score liegt im Median bei 58, dafür ist es am teuersten (~25 €/kg). Pro 10 g Protein ist Sous-vide trotzdem eine der günstigsten Varianten, weil es fast reines Fleisch ist.
2. **Tiefkühl (TK)** ist der beste Allrounder: Median 9,5 g Protein, ~6 g Protein pro 100 kcal, wenig Zucker und ein Health-Score von ~46. Darunter fallen viele Rohprodukte wie Fisch, Spieße und Ripperl, die im Multipot ideal sind.
3. **Kühlregal-Menüschalen (Good Choice, Omis Schmankerl, Hofstädter, Clever)** liegen im Mittelfeld: ~7 g Protein, ~1,1 g Salz und ein Score von ~35. Sie haben die kürzeste Haltbarkeit, sind am wenigsten hitzebelastet und oft eher NOVA 3 als 4.
4. **Dose/Konserve** ist am billigsten pro kg (~8 €/kg), aber proteinarm (~4 g/100 g, Eintöpfe und Suppen ziehen den Wert nach unten). Das Salz liegt mit ~1,2 g ähnlich wie bei Kühlware, der Score bei ~33. Ausreißer nach oben sind Gulasch-Dosen (S-Budget Rindsgulasch: ~38 g Protein für 2,99 €).
5. **Trocken/Instant (Knorr, Maggi, Becher-Nudeln)** schneidet am schlechtesten ab: Salz-Median 2,5 g/100 g, nur ~3,3 g Protein pro 100 kcal, Zucker 4,3 g und fast immer NOVA 4 (Aromen, Geschmacksverstärker, Maltodextrin). Der Score liegt bei ~23, die Kosten bei ~2,3 € pro 10 g Protein.

## Gesundheitsaspekte je Verpackungsart (Recherche)
- **Nährstoffverlust durch Hitze:** Sterilisieren in der Dose (Retort, ~116–121 °C) zerstört wasserlösliche, sauerstoffempfindliche Vitamine (C, B) stärker. Beim Konservieren gehen im Schnitt >60 % Vitamin C verloren, beim Tiefkühlen inkl. Blanchieren ~50 % (Spanne 10–80 %). Danach ist die Dose dank Sauerstoffausschluss stabil, TK verliert bei langer Lagerung weiter (20–50 % nach 1 Jahr bei −18 °C). Protein, Mineralstoffe und Ballaststoffe bleiben weitgehend erhalten. Quelle: Rickman, Barrett & Bruhn 2007, J Sci Food Agric 87:930 – https://onlinelibrary.wiley.com/doi/10.1002/jsfa.2825 (Volltext: https://ucanr.edu/sites/default/files/2010-06/19187.pdf); Teil 2 (Vitamin A, Mineralstoffe, Ballaststoffe): https://doi.org/10.1002/jsfa.2833
- **Kühlregal/Sous-vide:** Pasteurisiert (meist 70–95 °C) statt sterilisiert, daher schonender, aber nur Tage bis wenige Wochen haltbar (Kühlkette ≤ 4 °C nötig).
- **BPA/Dosenbeschichtung:** Die EFSA hat den TDI für BPA 2023 um den Faktor ~20.000 auf 0,2 ng/kg KG/Tag gesenkt; die Exposition liegt in allen Altersgruppen darüber – https://www.efsa.europa.eu/de/news/bisphenol-efsa-draft-opinion-proposes-lowering-tolerable-daily-intake (Gutachten: https://doi.org/10.2903/j.efsa.2023.6857). Die EU-VO 2024/3190 verbietet BPA in Lebensmittelkontaktmaterialien inkl. Doseninnenlacken. Für Einwegdosen gilt eine Übergangsfrist bis **20.07.2026**, für Obst/Gemüse- und Fischkonserven bis 20.01.2028, danach noch 12 Monate Befüllung und Abverkauf bis die Bestände aufgebraucht sind. Ältere Ware im Regal kann also noch BPA-Lacke haben – https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=OJ%3AL_202403190
- **Kunststoffschalen/Beutel:** Mikrowellen-Erhitzen in der Kunststoffschale fördert die Migration. Besser ist es, den Inhalt in einen Edelstahl- oder Glaseinsatz für den Multipot umzufüllen.
- **NOVA-Verarbeitungsgrad** (Monteiro et al. 2019, https://doi.org/10.1017/S1368980018003762): Instant/Trocken ist fast immer **NOVA 4** (Hefeextrakt, Aromen, Glutamat, Maltodextrin, modifizierte Stärke). Dosen-Fertiggerichte sind meist NOVA 4 (modifizierte Stärke, Aromen) und Kühl-Menüschalen schwanken zwischen 3 und 4. Pures TK-/Sous-vide-Fleisch oder -Fisch ist NOVA 1–3. Hoher UPF-Konsum ist mit höherem Risiko u. a. für Herz-Kreislauf-Erkrankungen und Mortalität assoziiert (Lane et al. 2024, BMJ, https://doi.org/10.1136/bmj-2023-077310).
- **Haltbarkeit (typisch):** Dose 2–4 Jahre · Trocken/Instant 12–24 Monate · Glas 1–2 Jahre · TK 12–24 Monate bei −18 °C · Retort-Pouch 12–18 Monate · Sous-vide gekühlt 2–6 Wochen · Kühl-Menüschale 5–21 Tage. (Branchenübliche Werte, keine Einzelquelle; MHD auf der Packung ist maßgeblich.)

## Health-KPI-Score (0–100) – Formel
Basis 30 Punkte, dann:
- **Protein-Dichte** +0…40: `min(Protein g / 100 kcal ÷ 10, 1) × 40` (≥10 g/100 kcal ergibt volle Punktzahl)
- **Salz-Malus** 0…−20: `−min(max(Salz − 0,6, 0) / 1,4, 1) × 20` (ab 2,0 g/100 g volle Strafe)
- **Gesättigte-Fette-Malus** 0…−15: `−min(max(ges. Fett − 1,5, 0) / 4,5, 1) × 15` (ab 6 g volle Strafe)
- **Ballaststoff-/Gemüse-Bonus** 0…+20: `min(Ballaststoffe / 6, 1) × 15` plus +5, wenn Gemüse oder Hülsenfrüchte im Namen stehen
- **Verarbeitungs-Malus** 0…−10: `−(NOVA-Schätzung − 3) × 10`, NOVA je Typ: Dose/Instant/Pouch 4, TK/Kühl/Glas 3,5, Sous-vide 3, rohe/marinierte Fleischstücke 3
- Auf 0–100 begrenzt. Fehlende Werte geben weder Bonus noch Malus. Ohne kcal/Protein gibt es keinen Score.

Die Felder pro Produkt in `scored.json` sind `packaging`, `health_score`, `protein_per_euro` (g Protein/€), `price_per_10g_protein`, `protein_per_100kcal` und `is_meal`.

## Top 10 je Verpackungsart (Health-Score)
""")
for t in sorted(S):
    T=sorted([x for x in M if x['packaging']==t and x['health_score'] is not None],key=lambda x:-x['health_score'])[:10]
    w(f"\n### {t}\n\n| # | Produkt | Marke | Laden | Score | Protein/100g | Salz | € | g Protein/€ |\n|---|---|---|---|---|---|---|---|---|")
    for i,x in enumerate(T,1):
        nm=f"[{x['name'].strip()}]({x['url']})" if x.get('url') else x['name']
        w(f"| {i} | {nm} | {x.get('brand') or ''} | {x.get('store') or ''} | {x['health_score']} | {x.get('protein_100')} | {x.get('salt_100')} | {x.get('price_eur') or '–'} | {x.get('protein_per_euro') or '–'} |")
open('packaging_report.md','w').write('\n'.join(L))
