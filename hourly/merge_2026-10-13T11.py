import json,re,os,shutil
os.chdir('/workspace/fertig')
D='2026-10-13'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (20<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
SKIP=re.compile(r'Pizza Pockets|Mezeteller|Tabouleh|Fledermaus|Schinkenrollen|Schweinebacken',re.I)
C=json.load(open('hourly/cand_enriched_2026-10-13T11.json'))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
have={(k(x['name']),k(x.get('brand')),x.get('store')) for x in S}|{(k(x['name']),k(x.get('brand')),x.get('store')) for x in cn}
haveE={(str(x.get('ean')).lstrip('0'),x.get('store')) for x in S+cn if x.get('ean')}
new,rej=[],[]
for p in C:
  n=p.get('nutrition_100g') or {}; nm=re.sub(r'\s+',' ',p['name']).strip(); cat=p['category'].split(' > ')[-1]
  if SKIP.search(nm): rej.append((nm,'kein Heiß-Fertiggericht/keine Nährwerte')); continue
  if not n.get('kcal') or n.get('protein') is None: rej.append((nm,'keine Nährwerte')); continue
  if not consistent(n): rej.append((nm,f'Nährwerte inkonsistent {n}')); continue
  if not (p.get('price_eur') and p.get('size_g')): rej.append((nm,'kein Preis/Gewicht')); continue
  if (k(nm),k(p.get('brand')),'Gurkerl.at') in have or (p.get('ean') and (str(p['ean']).lstrip('0'),'Gurkerl.at') in haveE): rej.append((nm,'schon vorhanden')); continue
  tk='tiefgekühlt' in nm or 'Tiefkühl' in p['category']
  pk='Tiefkühl (TK)' if tk else ('Dose/Konserve' if 'gulasch' in nm.lower() else 'Trocken/Instant' if re.search('Nudel|Ramen|Topokki',nm) else 'Kühlregal (Menüschale/frisch)')
  g=p['size_g']; brand=p.get('brand') or None
  if brand=='Ristorante': brand='Dr. Oetker'
  r=dict(name=nm,brand=brand,store='Gurkerl.at',price_eur=p['price_eur'],size_g=g,price_per_kg=round(p['price_eur']/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=(p.get('producer') or '').rstrip('.') or None,producer_id=p.get('producer_id'),
    origin=p.get('origin'),category=cat,price_source=f'food-connectors/gurkerl {D} (category API, inStock)',price_date=D,
    nut_source=f'Gurkerl.at API (composition) {D}',ean=p.get('ean'),packaging=pk,packaging_hint=pk,is_meal=True,delivery='Lieferung nach Linz (Gurkerl.at)')
  have.add((k(nm),k(brand),'Gurkerl.at')); new.append(r)
shutil.copy('connectors_new.json','connectors_new.json.bak_hourly11')
json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(added=new,rejected=rej),open('hourly/added_2026-10-13T11.json','w'),ensure_ascii=False,indent=1)
print('added',len(new)); [print(' REJ',*x) for x in rej]
