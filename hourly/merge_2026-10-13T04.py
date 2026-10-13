import json,re,os,shutil
os.chdir('/workspace/fertig')
D='2026-10-13'; NK=['kcal','protein','fat','satfat','carbs','sugar','fiber','salt']
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (20<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
mm=json.load(open('more_meals.json'));mn=json.load(open('more_meals_norm.json'))
KEYS=list(mn[0].keys())
have={(x['name'],x['store'],x.get('size_g')) for x in mm}; haveE={str(x.get('ean')) for x in mm if x.get('ean')}
C=json.load(open('hourly/cand_enriched_2026-10-13T04.json'))
new=[];rej=[]
for c in C:
  p,cat,pack=c['p'],c['cat'],c['pack']; n=p.get('nutrition_100g') or {}
  if not n.get('kcal') or n.get('protein') is None: rej.append((p['name'],'keine Nährwerte')); continue
  if not consistent(n): rej.append((p['name'],f'Nährwerte inkonsistent {n}')); continue
  if not (p.get('price_eur') and p.get('size_g')): rej.append((p['name'],'kein Preis/Gewicht')); continue
  r={k:None for k in KEYS}
  r.update(name=p['name'],brand=p.get('brand'),store='Gurkerl.at',price_eur=p['price_eur'],size_g=p['size_g'],
    price_per_kg=round(p['price_eur']/p['size_g']*1000,2),url=p['source_url'],image_url=p.get('image_url'),
    **{k+'_100':(None if n.get(k) is None else round(float(n[k]),2)) for k in NK},
    manufacturer=p.get('producer'),producer_id=p.get('producer_id'),origin=p.get('origin'),
    bio=bool(re.search(r'\bBIO\b',p['name'])),veg=True if re.search(r'vegan',p['name'],re.I) else None,
    category=cat,packaging=pack,fertigstufe='Eintopf/Suppe' if cat=='Suppe/Eintopf' else ('Nachspeise' if cat=='Nachspeise' else 'Komplettmahlzeit'),
    price_source=f'food-connectors/gurkerl {D} (category API, inStock)',price_date=D,
    nut_source=f'Gurkerl.at API (composition) {D}',source_url=p['source_url'],ean=p.get('ean'))
  g=r['size_g']; r['protein_pack']=round(r['protein_100']*g/100,1); r['kcal_pack']=round(r['kcal_100']*g/100)
  r['protein_per_eur']=round(r['protein_pack']/r['price_eur'],1)
  if (r['name'],r['store'],r['size_g']) in have or (r['ean'] and str(r['ean']) in haveE): rej.append((p['name'],'schon vorhanden')); continue
  new.append(r)
shutil.copy('more_meals.json','hourly/more_meals.before_2026-10-13T04.json')
json.dump(mm+new,open('more_meals.json','w'),ensure_ascii=False,indent=1)
json.dump(mn+new,open('more_meals_norm.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(added=new,rejected=rej),open('hourly/added_2026-10-13T04.json','w'),ensure_ascii=False,indent=1)
print('added',len(new)); [print(' REJ',*x) for x in rej]
