import json,re,os,shutil
os.chdir('/workspace/fertig')
D='2026-10-13'
exec(open('hourly/merge_2026-10-13T11.py').read().split('SKIP=')[0].split("D='2026-10-13'")[1])  # consistent()
SKIP=re.compile(r'Bowl',re.I)  # kalte Bowls: kein Heiß-Fertiggericht
P=json.load(open('hourly/cand_billa_2026-10-13T12.json'))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
have={(k(x['name']),(x.get('store') or '').upper()) for x in S+cn}; haveU={x.get('url') for x in S+cn}
new,rej=[],[]
for p in P:
  nm=re.sub(r'\s+',' ',p['name']).strip(); n=p.get('nutrition_100g') or {}; brand=p.get('brand')
  if SKIP.search(nm): rej.append((nm,'kalte Bowl, kein Heiß-Fertiggericht')); continue
  if not n.get('kcal') or n.get('protein') is None: rej.append((nm,'keine Nährwerte')); continue
  if not consistent(n): rej.append((nm,f'Nährwerte inkonsistent {n}')); continue
  if not (p.get('price_eur') and p.get('size_g')): rej.append((nm,'kein Preis/Gewicht')); continue
  if p['source_url'] in haveU or (k(nm),'BILLA') in have: rej.append((nm,'schon vorhanden')); continue
  pk='Trocken/Instant' if 'Cup' in nm else 'Tiefkühl (TK)'
  cat={'Pizza':'Tiefkühlpizza','Asien':'Instant-Nudeln/Cup','Gemüse':'TK-Gemüsepfanne','Gemüse & Käsegerichte':'TK-Fertiggericht','Mehlspeisen, Torten':'TK-Mehlspeise'}.get(p.get('category'),p.get('category'))
  g=p['size_g']; man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  r=dict(name=nm,brand=brand,store='BILLA',price_eur=p['price_eur'],size_g=g,price_per_kg=round(p['price_eur']/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=p.get('origin'),category=cat,price_source=f'food-connectors/billa {D} (product-discovery API, regulärer Preis)',price_date=D,
    nut_source=f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}',ean=p.get('ean'),packaging=pk,packaging_hint=pk,is_meal=True,delivery='BILLA Zustellung (Linz)')
  have.add((k(nm),'BILLA')); new.append(r)
shutil.copy('connectors_new.json','connectors_new.json.bak_hourly12')
json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(added=new,rejected=rej),open('hourly/added_2026-10-13T12.json','w'),ensure_ascii=False,indent=1)
print('added',len(new)); [print(' REJ',*x) for x in rej]
