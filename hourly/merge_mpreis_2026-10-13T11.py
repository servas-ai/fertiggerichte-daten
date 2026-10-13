import json,re,os
os.chdir('/workspace/fertig')
D='2026-10-13'
exec(open('hourly/merge_2026-10-13T11.py').read().split('SKIP=')[0].split("D='2026-10-13'")[1])  # consistent()
KEEP=re.compile(r'Ristorante|Ofenfrische|Tradizionale|La Mia Grande|Suprema|Cinque Formaggi|Salame Romano|Intermezzo|Amore Napoli|Gustavo|Holy Slice|Steinofen|Big Sensation|Lasagne|Nasi Goreng|Wienerschnitzel|Selchfleischknödel',re.I)
P=json.load(open('hourly/cand_mpreis_2026-10-13T11.json'))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
have={(k(x['name']),k(x.get('brand')),x.get('store')) for x in S+cn}
haveE={(str(x.get('ean')).lstrip('0'),x.get('store')) for x in S+cn if x.get('ean')}
haveU={x.get('url') for x in S+cn}
add=json.load(open('hourly/added_2026-10-13T11.json'))
new,rej=[],[]
for p in P:
  nm=p['name'].strip(); n=p.get('nutrition_100g') or {}; brand=p.get('brand')
  full=f"{brand} {nm}" if brand and not nm.lower().startswith(brand.lower()) else nm
  if not KEEP.search(full) or p['extra'].get('availability')!='InStock': rej.append((full,'kein Heiß-Fertiggericht/Snack/nicht lieferbar')); continue
  if not n.get('kcal') or n.get('protein') is None: rej.append((full,'keine Nährwerte je 100 g')); continue
  if not consistent(n): rej.append((full,f'Nährwerte inkonsistent {n}')); continue
  if not (p.get('price_eur') and p.get('size_g')): rej.append((full,'kein Preis/Gewicht')); continue
  if p['source_url'] in haveU or (k(full),k(brand),'MPreis') in have or (k(nm),k(brand),'MPreis') in have or (p.get('ean') and (str(p['ean']).lstrip('0'),'MPreis') in haveE): rej.append((full,'schon vorhanden')); continue
  cat=(p.get('category') or '')
  pk='Tiefkühl (TK)' if 'Tiefkühl' in cat else None
  g=p['size_g']
  r=dict(name=full,brand=brand,store='MPreis',price_eur=p['price_eur'],size_g=g,price_per_kg=round(p['price_eur']/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=None,producer_id=None,origin=None,category=cat,
    price_source=f'food-connectors/mpreis-shop {D} (JSON-LD, InStock)',price_date=D,nut_source=f'MPreis Webshop (Nährwerte je 100 g) {D}',
    ean=p.get('ean'),packaging=pk,packaging_hint=pk,is_meal=True,delivery='Lieferung MPreis')
  have.add((k(full),k(brand),'MPreis')); new.append(r)
json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
add['added']+=new; add['rejected']+=rej
json.dump(add,open('hourly/added_2026-10-13T11.json','w'),ensure_ascii=False,indent=1)
print('added',len(new)); [print(' +',x['name'],x['kcal_100'],x['protein_100']) for x in new]; [print(' REJ',*x) for x in rej]
