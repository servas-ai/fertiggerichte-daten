import json,re
KEYS=list(json.load(open('more_meals_norm.json'))[0].keys())
B=json.load(open('hourly/billa_new.json'))
R=json.load(open('hourly/off_lidl.json'));L=json.load(open('hourly/lidl_live.json'))
F={'kcal':'energy-kcal_100g','protein':'proteins_100g','fat':'fat_100g','satfat':'saturated-fat_100g','carbs':'carbohydrates_100g','sugar':'sugars_100g','fiber':'fiber_100g','salt':'salt_100g'}
def rnd(v): return None if v is None else round(float(v),2)
new=[]
for code,pack,cat in [('4056489886150',None,'Komplettmahlzeit'),('4056489628293',None,'Komplettmahlzeit'),('20113476','Dose','Suppe/Eintopf')]:
  x=R[code];n=x.get('nutriments') or {}
  g=None
  m=re.match(r'\s*(\d+(?:[.,]\d+)?)\s*g',x.get('quantity') or '')
  if m:g=float(m.group(1).replace(',','.'))
  name=x.get('product_name_de') or x.get('product_name')
  brs=[b.strip() for b in x['brands']] if isinstance(x['brands'],list) else [x['brands']]
  r={k:None for k in KEYS};r.update({k+'_100':rnd(n.get(v)) for k,v in F.items()})
  em=x.get('emb_codes');em=', '.join(em) if isinstance(em,list) else em
  r.update(name=name,brand=brs[0],store='LIDL',size_g=g,url='https://world.openfoodfacts.org/product/'+code,image_url=x.get('image_front_url'),
    nutriscore=(x.get('nutriscore_grade') or '').upper() if x.get('nutriscore_grade') in list('abcde') else None,producer_id=em or None,
    nut_source=f'Open Food Facts {code} (countries: Austria)',packaging=pack,category=cat,fertigstufe='Eintopf/Suppe' if cat=='Suppe/Eintopf' else 'Komplettmahlzeit',
    source_url='https://world.openfoodfacts.org/product/'+code,bio=False)
  if g and r['protein_100'] is not None:r['protein_pack']=round(r['protein_100']*g/100,1)
  if g and r['kcal_100'] is not None:r['kcal_pack']=round(r['kcal_100']*g/100)
  r['ean']=code;new.append(r)
for code,g in [('10056720',1000.0),('10056594',500.0)]:
  d=L[code]['gridbox']['data'];pr=d['price']['price']
  r={k:None for k in KEYS}
  r.update(name=d['keyfacts']['title'],brand=d['brand']['name'].title().replace('Mcennedy','McEnnedy'),store='LIDL',price_eur=pr,size_g=g,price_per_kg=round(pr/g*1000,2),
    url='https://www.lidl.at'+d['canonicalUrl'],image_url=d['image'],packaging='TK (Tiefkühl)',category='Komplettmahlzeit',fertigstufe='Komplettmahlzeit',
    price_source='lidl.at Such-API (live, Aktionsware) 2026-10-13',price_date='2026-10-13',source_url='https://www.lidl.at'+d['canonicalUrl'],bio=False)
  r['price_live']=True;new.append(r)
allnew=B+new
for r in allnew:
  if 'protein_per_eur' in r: r['protein_per_eur']=round(r['protein_pack']/r['price_eur'],1) if r.get('protein_pack') and r.get('price_eur') else None
mm=json.load(open('more_meals.json'))
have={(x['name'],x['store'],x.get('size_g')) for x in mm}
add=[r for r in allnew if (r['name'],r['store'],r.get('size_g')) not in have]
mm+=add
json.dump(mm,open('more_meals.json','w'),ensure_ascii=False,indent=1)
json.dump(mm,open('more_meals_norm.json','w'),ensure_ascii=False,indent=1)
json.dump(add,open('hourly/added_2026-10-13.json','w'),ensure_ascii=False,indent=1)
print('added',len(add),'total more_meals',len(mm))
for r in new:print(r['name'],r['brand'],r['price_eur'],r['size_g'],r['protein_100'],bool(r['image_url']))
