# hourly T16 (2026-10-13T16): merge verified Gurkerl + BILLA candidates into connectors_new.json (same gates as T14: nutrition present+consistent, price+size, not yet present)
import json,re,os,collections
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
  if not consistent(n): rej.append((store,nm,f'Nährwerte inkonsistent/unplausibel an der Quelle {n}')); return
  if not (price and p.get('size_g') and p['size_g']>=50): rej.append((store,nm,'kein Preis/Gewicht')); return
  if p['source_url'] in haveU or (k(nm),sk(store)) in have or (p.get('ean') and (str(p['ean']).lstrip('0'),sk(store)) in haveE): rej.append((store,nm,'schon vorhanden')); return
  g=p['size_g']; man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  brand=p.get('brand') or None
  if brand and brand.lower()=='iglo': brand='iglo'
  r=dict(name=nm,brand=brand,store=store,price_eur=price,size_g=g,price_per_kg=round(price/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=p.get('origin'),category=cat,price_source=psrc,price_date=D,nut_source=nsrc,ean=p.get('ean'),packaging=pk,packaging_hint=pk,is_meal=True,delivery=delivery,added_slot='2026-10-13T16',**extra)
  have.add((k(nm),sk(store))); new.append(r)
# Gurkerl
for p in json.load(open('hourly/cand_gurkerl_2026-10-13T16.json')):
  c=p['category'] or ''; nm=p['name']
  tk='tiefgekühlt' in nm or 'gefroren' in nm or c.startswith('Tiefkühl')
  pk='Tiefkühl (TK)' if tk else ('Konserve/Dose (ungekühlt)' if c.startswith('Vorratsschrank') else 'Kühlregal (Menüschale/frisch)')
  cat=('Tiefkühlpizza' if ('Pizza' in c or 'Pizza' in nm or 'AirFryer Snack' in nm) else 'TK-Fisch' if ('Fisch' in c) else 'Dosengerichte' if c.startswith('Vorratsschrank') else
       'Suppe/Eintopf' if 'Suppe' in c else 'Knödel, Spätzle & Co' if 'Pasta, Spätzle' in c else c.split(' > ')[-1] or 'Fertiggerichte')
  add(p,'Gurkerl.at',pk,cat,p['price_eur'],f'food-connectors/gurkerl {D} (category walk + search, products/prices/stock API, inStock)',f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)')
# BILLA
for p in json.load(open('hourly/cand_billa_2026-10-13T16.json')):
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  cp=e.get('category_path') or ''; nm=p['name']
  cat=('Tiefkühlpizza' if 'Pizza' in cp else 'TK-Fisch' if 'Fisch' in cp else 'Fertiggerichte')
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  add(p,'BILLA',pk,cat,price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',ex)
json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(slot='2026-10-13T16',added=new,rejected=rej),open('hourly/added_2026-10-13T16.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'])
