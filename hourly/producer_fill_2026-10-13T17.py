# hourly T17: producer/manufacturer fill for connectors_new rows (T17 adds + older gaps)
# 1) EAN twin: another row with the same EAN already carries a label manufacturer (BILLA/Gurkerl Pflichtangaben)
# 2) Brand consensus: all (>=20) labelled rows of the brand in the dataset name the same Inverkehrbringer (Felix, Inzersdorfer/Maresi, Dr. Oetker, Knorr/Unilever, Iglo)
# 3) Public company sources: WP Fine Food GmbH (wp-finefood.com/about-me-de.html, Handelskammer Bozen 02660690211);
#    Exotic Food (exoticfoodthailand.com; EU-Importeur Kreyenhop & Kluge GmbH & Co. KG, Oyten laut Etikett-Text)
# 4) Open Food Facts emb_codes (strict Identitätskennzeichen format only) -> producer_id
import json,re,collections
F='/workspace/fertig/connectors_new.json'; cn=json.load(open(F)); S=json.load(open('/workspace/fertig/scored.json'))
SLOT='2026-10-13T17'
byE=collections.defaultdict(collections.Counter)
for x in S+cn:
  m=x.get('manufacturer')
  if x.get('ean') and m and not re.match(r'(?i)(billa|spar|hofer|lidl|rewe|mpreis|verband)',m): byE[str(x['ean']).lstrip('0')][m.strip()]+=1
CONS={'felix':None,'inzersdorfer':None,'dr. oetker':None,'knorr':None,'iglo':None}
for b in CONS:
  ms=collections.Counter(x['manufacturer'].strip() for x in S+cn if (x.get('brand') or '').lower()==b and x.get('manufacturer') and x.get('added_slot')!=SLOT)
  head=collections.Counter(re.sub(r'\s+',' ',re.split(r'[,\n]',m)[0]).strip().lower().rstrip('.').replace(' gmbh','') for m in ms.elements())
  if sum(ms.values())>=20 and head.most_common(1)[0][1]/sum(ms.values())>=0.9: CONS[b]=next(m for m,_ in ms.most_common() if re.split(r'[,\n]',m)[0].strip().lower().replace(' gmbh','')==head.most_common(1)[0][0] and re.search(r'\d{4}',m)).replace('\n',', ')
print('consensus',CONS)
PUB={'wolfensberger & pomella':("WP Fine Food GmbH (Srl), Milla 3, 39040 Kurtatsch/Cortaccia BZ, Italien; Produktion Dürer Straße 26, 39100 Bozen",'wp-finefood.com/about-me-de.html (Gesellschafter Klaus Wolfensberger & Gert Pomella, Handelskammer Bozen 02660690211), 2026-10-13'),
     'exotic food':("Exotic Food Public Company Limited (Thailand); EU-Importeur Kreyenhop & Kluge GmbH & Co. KG, Industriestr. 40-42, 28876 Oyten",'exoticfoodthailand.com/product/tom-kha-soup (EAN 8853662002026); Importeur laut Etikett-Text (amazon.de B0050O7R98), 2026-10-13')}
OFF=json.load(open('/workspace/fertig/hourly/off_idk_2026-10-13T17.json'))
n=collections.Counter()
for r in cn:
  e=str(r.get('ean') or '').lstrip('0'); b=(r.get('brand') or '').lower()
  if not r.get('manufacturer'):
    if e and byE.get(e):
      r['manufacturer']=byE[e].most_common(1)[0][0]; r['manufacturer_source']=f'EAN-Zwilling {e}: Etikett-Herstellerangabe einer anderen Kette im Datensatz'; n['ean_twin']+=1
    elif r.get('added_slot')==SLOT and CONS.get(b):
      r['manufacturer']=CONS[b]; r['manufacturer_source']=f'Marken-Konsens: alle ≥20 Etiketten der Marke {r["brand"]} im Datensatz nennen diesen Inverkehrbringer'; n['brand_consensus']+=1
    elif b in PUB:
      r['manufacturer'],r['manufacturer_source']=PUB[b]; n['public_source']+=1
  if not r.get('producer_id') and r.get('ean'):
    o=OFF.get(str(r['ean']).strip())
    if o and o.get('code_strict') and ',' not in o['code_strict']:
      r['producer_id']=o['code_strict']; r['producer_id_source']=f"Open Food Facts emb_codes '{o.get('emb_codes')}' (EAN {r['ean']}), 2026-10-13"; n['idk_off']+=1
json.dump(cn,open(F,'w'),ensure_ascii=False,indent=1)
print(dict(n))
