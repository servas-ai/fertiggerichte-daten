import json,re
src=open('ex.py').read();exec(src[src.index('NM='):src.index('KEYS=')]);exec(src[src.index('def billa'):src.index('W=lambda')])
D=json.load(open('mm_raw.json'));KEYS=list(json.load(open('expand.json'))[0].keys())
ok=re.compile(r'Inzersdorfer|Iglo (Rindsgulasch|Selchfleisch|Fleischknödel|Grammel|Pasta Asciutta|Green Cuisine Karfiol)|Meisterkessel')
out=[]
for s,v in D['det'].items():
  c=D['cand'][s]
  if not v or not ok.search(c['name']):continue
  b=billa(c,v);g=float(c.get('amount') or 0);pr=c['price']['regular']['value']/100
  r={k:None for k in KEYS};r.update({k:b[k] for k in b if k in KEYS})
  frozen='tiefkuehl' in c['_cat'];can='dose' in c['_cat']
  r.update(name=c['name'],store='BILLA',price_eur=pr,size_g=g,price_per_kg=round(pr/g*1000,2) if g else None,
    protein_pack=round(b['protein_100']*g/100,1) if b['protein_100'] is not None else None,kcal_pack=round(b['kcal_100']*g/100) if b['kcal_100'] is not None else None,
    bio=False,category='Suppe/Eintopf' if 'Meisterkessel' in c['name'] else 'Komplettmahlzeit',
    price_source='BILLA shop API 2026-10-12',price_date='2026-10-12',packaging='Tiefkühl' if frozen else 'Dose' if can else 'Beutel',source_url=b['url'],fertigstufe='Komplettmahlzeit')
  out.append(r)
json.dump(out,open('mm_billa.json','w'),ensure_ascii=False,indent=1);print(len(out),[(x['name'],x['protein_100']) for x in out])
