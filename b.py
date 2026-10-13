import json,re,collections
raw=json.load(open('raw.json'));det=json.load(open('det.json'))
NM={'ENER-':'kcal','PRO-':'protein','FAT':'fat','FASAT':'satfat','CHOAVL':'carbs','SUGAR-':'sugar','FIBTG':'fiber','SALTEQ':'salt'}
out=[]
for s,p in det.items():
  if not p: continue
  txt=json.dumps(p,ensure_ascii=False)
  ai=(p.get('additionalInformation') or [{}])[-1]
  fi=ai.get('foodInformation',{}) or {}; pi=ai.get('productInformation',{}) or {}
  n={}
  for ni in fi.get('nutritionInfos',[]):
    if ni.get('relationValue')!=100: continue
    if n and ni.get('preparationGrade')!='Unzubereitet': continue
    for x in ni.get('nutrients',[]):
      k=NM.get(x['nutrientId'])
      if not k: continue
      if k=='kcal' and x['unit']['symbol']!='kcal': continue
      n[k]=x['value']
  pr=p['price']['regular']; price=pr['value']/100
  size=None
  for m in pi.get('measurements',[]):
    if m['type']=='Nettogehalt' and m['unit'] in('Gramm','Milliliter'): size=m['value']
  if size is None:
    try:
      a=float(p['amount']); size=a*1000 if p['volumeLabelShort'] in('kg','l') else a if p['volumeLabelShort'] in('g','ml') else None
    except: pass
  ids=sorted(set(re.findall(r'\bAT[ -]?\d{4,5}[ -]?(?:EG|EWG|EC)\b|\b(?:DE|IT|HU|PL|CZ|SK|SI)[ -][A-Z0-9-]{2,10}[ -](?:EG|EWG|EC)\b',txt)))
  b=p.get('badges') or raw[s].get('badges',[])
  low=txt.lower()
  name=p['name']; cat=p['category']
  bio='pp-bio' in b or 'bio' in name.lower() or 'natürlich' in (p.get('brand') or raw[s].get('brand') or {}).get('name','').lower()
  veg='vegan' if 'pp-vegan' in b else 'vegetarisch' if 'pp-veget' in b else None
  prep=[w for w in ['Mikrowelle','Topf','Pfanne','Backrohr','Wasserbad','heißes Wasser','Aufgießen'] if w.lower() in low]
  nl=name.lower()
  if cat in('Suppen',) or 'suppe' in nl or 'eintopf' in nl: ip='Sauté-Modus (Simmer/Low) 5-8 Min. unter Rühren erhitzen; alternativ Dampfgaren 5 Min. im Glas/Schale auf Gitter, Quick Release'
  elif cat=='Menüschalen' or cat.startswith('Fertiggerichte'): ip='Dampfgaren (Steam) in ofenfester Schale auf Gitter, 250 ml Wasser, 5-8 Min., Quick Release'
  elif cat=='Frische Pasta & Beilagen' or cat=='Reis & Pasta': ip='Frischpasta/Gnocchi: Sauté (Boil) in Wasser 2-4 Min.; oder Pressure Cook Low 1-2 Min. mit Sauce, Quick Release'
  elif cat=='Asien': ip='Nudeln/Instant: Sauté (Boil) Wasser aufkochen, 3-5 Min. ziehen lassen'
  elif cat=='Dose': ip='Inhalt in Topfeinsatz, Sauté (Low) 5-7 Min. erhitzen; alternativ Steam 6 Min. in Schale'
  else: ip='Beutel/Trockengericht: Pressure Cook High 3-5 Min. mit angegebener Wassermenge, Natural Release 5 Min. (Schätzung)'
  sz=size; pk=lambda v:(round(v*sz/100,1) if v is not None and sz else None)
  out.append(dict(name=name,brand=(p.get('brand') or raw[s].get('brand') or {}).get('name'),store='BILLA',price_eur=price,size_g=sz,
    price_per_kg=round(pr['perStandardizedQuantity']/100,2) if pr.get('perStandardizedQuantity') else None,
    url='https://shop.billa.at/produkte/'+p['slug'],image_url=(p.get('images') or [None])[0],
    kcal_100=n.get('kcal'),protein_100=n.get('protein'),fat_100=n.get('fat'),satfat_100=n.get('satfat'),carbs_100=n.get('carbs'),sugar_100=n.get('sugar'),fiber_100=n.get('fiber'),salt_100=n.get('salt'),
    protein_pack=pk(n.get('protein')),kcal_pack=pk(n.get('kcal')),nutriscore=None,
    manufacturer=(pi.get('manufacturersAddress') or (pi.get('contactDetails') or {}).get('name') or None),
    producer_id=', '.join(ids) or None,origin=p.get('countryOfOrigin') or None,bio=bio,veg=veg,
    prep=', '.join(prep) or None,instantpot=ip,category=cat))
json.dump(out,open('billa.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['protein_100'] is not None),sum(1 for o in out if o['manufacturer']),sum(1 for o in out if o['producer_id']))
# shared manufacturers across brands
m=collections.defaultdict(set)
for o in out:
  if o['manufacturer']: m[o['manufacturer'].split('\n')[0].strip()].add(o['brand'])
for k,v in sorted(m.items(),key=lambda x:-len(x[1])):
  if len(v)>1: print(k,'|',v)
print(collections.Counter(o['brand'] for o in out).most_common(15))
