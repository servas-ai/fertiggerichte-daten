# hourly T18: producer/manufacturer + Identitätskennzeichen fill for T18 rows in connectors_new.json
# 1) EAN twin: another row with the same EAN already carries a label manufacturer (BILLA/Gurkerl Pflichtangaben)
# 2) Brand consensus: all (>=20) labelled rows of the brand in the dataset name the same Inverkehrbringer (Iglo, Inzersdorfer, Felix, Knorr, Dr. Oetker)
# 3) Public company sources (verified 2026-10-13): Therese Mölk = Produktionsbetrieb der MPREIS Warenvertriebs GmbH, Völs (bio-austria.at partner page);
#    Toni Kaiser = Weinbergmaier GmbH, Wolfern (product spec onlineshop.wedl.com 461517 'Hersteller: Weinbergmaier GmbH');
#    Pan/Alpenstrudel = Pan Tiefkühlprodukte (Pan Surgelati), Leifers BZ (pan.it company page)
# 4) Open Food Facts emb_codes (strict Identitätskennzeichen format only) -> producer_id (hourly/off_t18_2026-10-13T18.json)
import json,re,collections
F='/workspace/fertig/connectors_new.json'; cn=json.load(open(F)); S=json.load(open('/workspace/fertig/scored.json'))
SLOT='2026-10-13T18'
byE=collections.defaultdict(collections.Counter)
for x in S+cn:
  m=x.get('manufacturer')
  if x.get('ean') and m and not re.match(r'(?i)(billa|spar|hofer|lidl|rewe|mpreis|verband)',m): byE[str(x['ean']).lstrip('0')][m.strip()]+=1
CONS={'iglo':None,'inzersdorfer':None,'felix':None,'knorr':None,'dr. oetker':None,'alnatura':None,'wagner':None}
for b in CONS:
  ms=collections.Counter(x['manufacturer'].strip() for x in S+cn if (x.get('brand') or '').lower()==b and x.get('manufacturer') and x.get('added_slot')!=SLOT)
  if not ms: continue
  head=collections.Counter(re.sub(r'\s+',' ',re.split(r'[,\n]',m)[0]).strip().lower().rstrip('.').replace(' gmbh','') for m in ms.elements())
  if sum(ms.values())>=20 and head.most_common(1)[0][1]/sum(ms.values())>=0.9:
    c=[m for m,_ in ms.most_common() if re.split(r'[,\n]',m)[0].strip().lower().replace(' gmbh','').rstrip('.')==head.most_common(1)[0][0] and re.search(r'\d{4}',m)]
    if c: CONS[b]=c[0].replace('\n',', ')
print('consensus',{k:(v or '')[:60] for k,v in CONS.items()})
PUB={'therese mölk':("MPREIS Warenvertriebs GmbH – Bäckerei Therese Mölk (Produktionsbetrieb), Florianiweg 16a, 6176 Völs",'bio-austria.at Partnerbetrieb Bäckerei Therese Mölk (Produktionsbetrieb der MPREIS Warenvertriebs GmbH); mpreis.at/stories/news/10-jahre-mpreis-produktionsbetriebe, 2026-10-13'),
     'toni kaiser':("Weinbergmaier GmbH, Leopold-Werndl-Straße 1, 4493 Wolfern",'Produktspezifikation Toni Kaiser Germknödel (onlineshop.wedl.com prodspecs 461517: Hersteller Weinbergmaier GmbH); weinbergmaier.at Pressemappe (Tochter VIVATIS Holding AG), 2026-10-13'),
     'pan':("Pan Tiefkühlprodukte (Pan Surgelati), Leifers/Laives BZ, Italien",'pan.it/de/einzelhandel/unternehmen (Familienunternehmen, Werk Leifers); GS1-Präfix 8000460 = Marke Pan laut Open Food Facts, 2026-10-13'),
     'alpenstrudel':("Pan Tiefkühlprodukte (Pan Surgelati), Leifers/Laives BZ, Italien",'EAN 8000460010207: Open Food Facts Marke "Pan" (Strudel di mele); pan.it Strudel-Sortiment Werk Leifers, 2026-10-13')}
OFF=json.load(open('/workspace/fertig/hourly/off_t18_2026-10-13T18.json'))
n=collections.Counter()
for r in cn:
  if r.get('added_slot')!=SLOT: continue
  e=str(r.get('ean') or '').lstrip('0'); b=(r.get('brand') or '').lower()
  if not r.get('manufacturer'):
    if e and byE.get(e):
      r['manufacturer']=byE[e].most_common(1)[0][0]; r['manufacturer_source']=f'EAN-Zwilling {e}: Etikett-Herstellerangabe einer anderen Kette im Datensatz'; n['ean_twin']+=1
    elif CONS.get(b):
      r['manufacturer']=CONS[b]; r['manufacturer_source']=f'Marken-Konsens: alle ≥20 Etiketten der Marke {r["brand"]} im Datensatz nennen diesen Inverkehrbringer'; n['brand_consensus']+=1
    elif b in PUB:
      r['manufacturer'],r['manufacturer_source']=PUB[b]; n['public_source']+=1
  if not r.get('producer_id') and r.get('ean'):
    o=OFF.get(str(r['ean']).strip()) or {}
    if o.get('code_strict') and ',' not in o['code_strict']:
      r['producer_id']=o['code_strict']; r['producer_id_source']=f"Open Food Facts emb_codes '{o.get('emb_codes')}' (EAN {r['ean']}), 2026-10-13"; n['idk_off']+=1
json.dump(cn,open(F,'w'),ensure_ascii=False,indent=1)
mine=[r for r in cn if r.get('added_slot')==SLOT]
print(dict(n),'| T18 rows',len(mine),'with manufacturer',sum(1 for r in mine if r.get('manufacturer')),'with producer_id',sum(1 for r in mine if r.get('producer_id')),'with ean',sum(1 for r in mine if r.get('ean')),'with image',sum(1 for r in mine if r.get('image_url')))
for r in mine:
  if not r.get('manufacturer'): print('  no manufacturer:',r['store'],r['name'],r.get('ean'))
# 5) second pass (smaller brands): unanimous label manufacturer of the brand elsewhere in the dataset, or verified public/OFF company field
EXTRA={'leitgeb\'s nudelspezialitäten':("Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH, Industriestraße 18, 9360 Friesach",'Marken-Konsens: alle 4 Etiketten der Marke im Datensatz (Gurkerl) nennen diesen Hersteller; FN 662213v (evi.gv.at), 2026-10-13'),
       'alnatura':("Alnatura GmbH, Mahatma-Gandhi-Straße 7, 64295 Darmstadt",'Mehrheit der Alnatura-Etiketten im Datensatz (25/33; übrige: Alnatura Produktions- und Handels GmbH = frühere Firmierung), 2026-10-13'),
       'delamaris':("Delamaris d.o.o., Izola, Slowenien",'Marken-Konsens: alle Etiketten der Marke Delamaris im Datensatz nennen Delamaris d.o.o.; OFF-Marke NJAMI (Delamaris-Linie) für EAN 3838929620071, 2026-10-13'),
       'followfood':("followfood GmbH, Friedrichshafen",'Etikett einer weiteren followfood-Zeile im Datensatz (followfood GmbH); HRB 631854 AG Ulm (brand_tree T11, de.wikipedia Followfood), 2026-10-13'),
       'arteoliva':("Comerandalus S.L. (Marke Arteoliva), Spanien",'Open Food Facts brands für EAN 8437001133147 (Gazpacho Andaluz, 1 l): COMERANDALUS S.L., 2026-10-13')}
cn=json.load(open(F)); m2=0
for r in cn:
  if r.get('added_slot')==SLOT and not r.get('manufacturer') and (r.get('brand') or '').lower() in EXTRA:
    r['manufacturer'],r['manufacturer_source']=EXTRA[(r.get('brand') or '').lower()]; m2+=1
json.dump(cn,open(F,'w'),ensure_ascii=False,indent=1)
print('second pass',m2,'| still without manufacturer:',[r['name'] for r in cn if r.get('added_slot')==SLOT and not r.get('manufacturer')])
