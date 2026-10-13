import json,re,os,shutil
os.chdir('/workspace/fertig')
D='2026-10-13'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (20<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
sk=lambda s:{'gurkerl.at':'gurkerl','gurkerl':'gurkerl','billa':'billa','dm':'dm'}.get(str(s or '').lower(),str(s or '').lower())
have={(k(x['name']),sk(x.get('store'))) for x in S+cn}; haveU={x.get('url') for x in S+cn}
haveE={(str(x.get('ean')).lstrip('0'),sk(x.get('store'))) for x in S+cn if x.get('ean')}
SKIP=re.compile(r'Gemüse ?Pfanne(?! mit Bulgur)|Gemüse-Pilz-Pfanne|Instantnudeln|Asia Noodles|Kimchi Noodles|Korean BBQ|Bratlinge',re.I)
new,rej=[],[]
def add(p,store,pk,cat,price,psrc,nsrc,delivery,extra={}):
  nm=re.sub(r'\s+',' ',p['name']).strip(); n=p.get('nutrition_100g') or {}
  if SKIP.search(nm): rej.append((store,nm,'Gemüsebeilage/Instant (Zubereitet-Basis) – kein Heiß-Fertiggericht im Sinne der Rangliste')); return
  if not n.get('kcal') or n.get('protein') is None: rej.append((store,nm,'keine Nährwerte an der Quelle')); return
  if not consistent(n): rej.append((store,nm,f'Nährwerte inkonsistent an der Quelle {n}')); return
  if not (price and p.get('size_g')): rej.append((store,nm,'kein Preis/Gewicht')); return
  if p['source_url'] in haveU or (k(nm),sk(store)) in have or (p.get('ean') and (str(p['ean']).lstrip('0'),sk(store)) in haveE): rej.append((store,nm,'schon vorhanden')); return
  g=p['size_g']; man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  brand=p.get('brand') or None
  if brand and brand.lower()=='iglo': brand='iglo'
  r=dict(name=nm,brand=brand,store=store,price_eur=price,size_g=g,price_per_kg=round(price/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=p.get('origin'),category=cat,price_source=psrc,price_date=D,nut_source=nsrc,ean=p.get('ean'),packaging=pk,packaging_hint=pk,is_meal=True,delivery=delivery,**extra)
  have.add((k(nm),sk(store))); new.append(r)
# Gurkerl
for p in json.load(open('hourly/cand_gurkerl_2026-10-13T14.json')):
  c=p['category'] or ''; nm=p['name']
  tk='tiefgekühlt' in nm or 'gefroren' in nm or c.startswith('Tiefkühl') or 'Tiefgekühlte' in c
  pk='Tiefkühl (TK)' if tk else 'Kühlregal (Menüschale/frisch)'
  cat=('Tiefkühlpizza' if 'Pizza' in c else 'TK-Fisch' if ('Fisch' in c or re.search('Fish|Fisch|Cod|Haddock|Dorsch|Filegro|Goldschatz',nm)) else 'Knödel (Hauptgericht)' if 'Knödel' in c
       else 'TK-Gemüselaibchen' if re.search('Laibchen|Spinatstangerl',nm) else 'TK-Erdäpfeltascherl' if 'tascherl' in nm.lower() else 'Paniert/Nuggets' if re.search('Nuggets|Sticks|Safari',nm) else 'Vorspeise (Gebackenes)')
  add(p,'Gurkerl.at',pk,cat,p['price_eur'],f'food-connectors/gurkerl {D} (search + products/prices API, inStock)',f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)')
# BILLA
for p in json.load(open('hourly/cand_billa_2026-10-13T14.json')):
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  cp=e.get('category_path') or ''; nm=p['name']
  cat=('Paniert/Nuggets' if 'Nuggets' in nm else 'Tiefkühlpizza' if 'Pizza' in cp else 'TK-Fisch' if 'Fisch' in cp else 'TK-Mehlspeise' if re.search('Mehlspeis|Süßes',cp) else 'TK-Erdäpfeltascherl' if 'tascherl' in nm.lower() else 'Paniert/Nuggets' if 'Nuggets' in nm else 'Vorspeise (Gebackenes)' if 'Champignons' in nm else p.get('category'))
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  add(p,'BILLA',pk,cat,price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',ex)
# dm
for p in json.load(open('hourly/cand_dm_2026-10-13T14.json')):
  add(p,'dm',None,'Fertiggericht',p['price_eur'],f'food-connectors/dm {D} (products.dm.de product JSON, live)',f"dm.at product JSON (Nährwerte {p['extra'].get('nutrition_basis')}) {D}",'dm Filialen Linz (Abholung/Filiale)')

json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(added=new,rejected=rej),open('hourly/added_2026-10-13T14.json','w'),ensure_ascii=False,indent=1)
import collections
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'])
