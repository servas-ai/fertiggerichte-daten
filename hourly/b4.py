import json,re
src=open('ex.py').read();exec(src[src.index('NM='):src.index('KEYS=')]);exec(src[src.index('def billa'):src.index('W=lambda')])
D=json.load(open('hourly/b_det.json'));KEYS=list(json.load(open('more_meals_norm.json'))[0].keys())
S=json.load(open('scored.json'))
KEEP=['00-11369','00-2154','00-243700','00-397837','00-397847','00-425794','00-429185','00-429186','00-429189','00-438602','00-440303','00-500534','00-501793','00-514675','00-637089','00-637093','00-683828','00-697010','00-721918','00-728757','00-731854','00-733103','00-733272','00-745143','00-746119','00-775290','00-776181','00-776522','00-778880','00-832791','00-875583','00-875588','00-875590','00-905081','00-905082','00-912707','00-918195']
W=lambda s:set(re.findall(r'[a-zäöüß]{3,}',(s or '').lower()))
out=[]
for s in KEEP:
  c=D['cand'][s];v=D['det'][s]
  if not v:print('nodet',s);continue
  # fuzzy dup check
  nw=W(c['name']);g=float(re.sub(r'[^\d.]','',str(c.get('amount') or 0)) or 0)
  dup=[p['name'] for p in S if (p.get('store') or '').lower()=='billa' and len(nw&W(p['name']))/max(len(nw|W(p['name'])),1)>=0.75 and abs((p.get('size_g') or 0)-g)<5]
  if dup:print('DUP?',c['name'],dup);continue
  b=billa(c,v);pr=c['price']['regular']['value']/100
  promo=(c['price'].get('discounted') or {}).get('value') if isinstance(c['price'].get('discounted'),dict) else None
  can='Dose' in c['_path'];frozen='Tiefkühl' in c['_path']
  r={k:None for k in KEYS};r.update({k:b[k] for k in b if k in KEYS})
  r.update(name=c['name'],store='BILLA',price_eur=pr,size_g=g or None,price_per_kg=round(pr/g*1000,2) if g else None,
    protein_pack=round(b['protein_100']*g/100,1) if b['protein_100'] is not None and g else None,
    kcal_pack=round(b['kcal_100']*g/100) if b['kcal_100'] is not None and g else None,
    bio=bool(re.search(r'\bbio\b',c['name'],re.I)) or 'pp-bio' in (v.get('badges') or []),
    category='Suppe/Eintopf' if re.search(r'gulasch',c['name'],re.I) and can else 'Komplettmahlzeit',
    price_source='BILLA shop API 2026-10-13',price_date='2026-10-13',packaging='TK (Tiefkühl)' if frozen else 'Dose' if can else None,
    source_url=b['url'],fertigstufe='Eintopf/Suppe' if re.search(r'gulasch',c['name'],re.I) and can else 'Komplettmahlzeit')
  if 'protein_per_eur' in KEYS: r['protein_per_eur']=round(r['protein_pack']/pr,1) if r['protein_pack'] else None
  out.append(r)
json.dump(out,open('hourly/billa_new.json','w'),ensure_ascii=False,indent=1)
print(len(out))
for x in out:print(x['name'],x['price_eur'],x['size_g'],x['protein_100'],x['kcal_100'],x['salt_100'],bool(x['image_url']),(x['manufacturer'] or '').split('\n')[0],x['producer_id'],x['origin'])
