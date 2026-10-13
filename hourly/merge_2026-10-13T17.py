# hourly T17 (2026-10-13T17): merge verified MPreis + BILLA + PENNY candidates into connectors_new.json
# same gates as T16 (nutrition present+consistent, price+size>=50 g, true heat-up meal, not yet present by url/sku/EAN/name+store)
# PENNY: penny.at lists no nutrition; only items whose REWE article number is identical to a BILLA article (78-N == 00-N) get the BILLA label values (documented in nut_source).
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-13'; SLOT='2026-10-13T17'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (20<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
sk=lambda s:{'gurkerl.at':'gurkerl','gurkerl':'gurkerl','billa':'billa','dm':'dm','penny':'penny','mpreis':'mpreis'}.get(str(s or '').lower(),str(s or '').lower())
have={(k(x['name']),sk(x.get('store'))) for x in S+cn}; haveU={x.get('url') for x in S+cn}
haveE={(str(x.get('ean')).lstrip('0'),sk(x.get('store'))) for x in S+cn if x.get('ean')}
mpsku={m.group(1) for x in S+cn if 'mpreis' in str(x.get('url')) for m in [re.search(r'-(\d+)$',x.get('url') or '')] if m}
SKIP=re.compile(r'Gemüse ?Pfanne(?! mit Bulgur)|Gemüse-Pilz-Pfanne|Instantnudeln|Asia Noodles|Kimchi Noodles|Korean BBQ|Bratlinge',re.I)
new,rej=[],[]
def add(p,store,pk,cat,price,psrc,nsrc,delivery,name=None,extra={}):
  nm=re.sub(r'\s+',' ',name or p['name']).strip(); n=p.get('nutrition_100g') or {}
  if SKIP.search(nm): rej.append((store,nm,'Gemüsebeilage/Instant – kein Heiß-Fertiggericht')); return
  if not n.get('kcal') or n.get('protein') is None: rej.append((store,nm,'keine Nährwerte an der Quelle')); return
  if not consistent(n): rej.append((store,nm,f'Nährwerte inkonsistent/unplausibel an der Quelle {n}')); return
  if not (price and p.get('size_g') and p['size_g']>=50): rej.append((store,nm,'kein Preis/Gewicht')); return
  if p['source_url'] in haveU or (k(nm),sk(store)) in have or (p.get('ean') and (str(p['ean']).lstrip('0'),sk(store)) in haveE): rej.append((store,nm,'schon vorhanden')); return
  if sk(store)=='mpreis' and str(p.get('source_id')) in mpsku: rej.append((store,nm,'schon vorhanden (SKU)')); return
  g=p['size_g']; man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  brand=p.get('brand') or None
  r=dict(name=nm,brand=brand,store=store,price_eur=price,size_g=g,price_per_kg=round(price/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=p.get('origin'),category=cat,price_source=psrc,price_date=D,nut_source=nsrc,ean=p.get('ean'),packaging=pk,packaging_hint=pk,is_meal=True,delivery=delivery,added_slot=SLOT,**extra)
  have.add((k(nm),sk(store))); haveU.add(p['source_url']); new.append(r)
# MPreis (robots-allowed product pages, JSON-LD + Nährwerte-Tab je 100 g unzubereitet)
MP={'225801','365192','158310','225400','226502','200192','803710','810359','805805','805039','805806','804999','805703','803177','802249','158321','226503','225710','365679','365650','187011','187007','225712','286630','286300','286400','186168','186167','233120','233122','233121','805960'}
for p in json.load(open('/tmp/h17/mpreis_new.json')):
  if p['source_id'] not in MP: continue
  c=p['category'] or ''; b=p.get('brand')
  full=(b+' '+p['name']) if b and not p['name'].lower().startswith(b.lower()) else p['name']
  if 'Tiefkühl' in c: pk='Tiefkühl (TK)'
  elif 'To-Go' in c: pk='Kühlregal (Menüschale/frisch)'
  else: pk='Dose/Konserve'
  cat=('Tiefkühlpizza' if 'Pizza' in c else 'Suppe/Eintopf' if ('suppe' in c.split(' / ')[-1].lower() or re.search(r'suppe|eintopf',full,re.I)) else
       'Knödel, Spätzle & Co' if 'knödel' in full.lower() else 'Dosengerichte' if 'Dosengerichte' in c else 'TK-Gericht' if 'Tiefkühl' in c else 'Fertiggerichte')
  add(p,'MPreis',pk,cat,p['price_eur'],f'food-connectors/mpreis-shop {D} (category pages + sitemap, product JSON-LD offer price, {p["extra"].get("availability")})',f'MPreis Shop Produktseite, Nährwerte je 100 g (unzubereitet) {D}','MPreis Filiale Linz / MPreis Shop (AT)',name=full)
# BILLA
for p in json.load(open('hourly/cand_billa_2026-10-13T17.json')):
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  cp=e.get('category_path') or ''; nm=p['name']
  cat=('Tiefkühlpizza' if ('Pizza' in cp or 'Pizza' in nm) else 'TK-Fisch' if 'Fisch' in cp else 'Desserts' if 'Mehlspeise' in cp else 'Fertiggerichte')
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  add(p,'BILLA',pk,cat,price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',extra=ex)
# PENNY (article twins of BILLA)
B={x['url'].rsplit('-',1)[-1][2:]:x for x in S+cn if 'shop.billa.at' in str(x.get('url'))}
for x in json.load(open('hourly/cand_billa_2026-10-13T17.json')): B[x['source_id'][3:]]={'_raw':x}
PEN=json.load(open('/tmp/h17/penny_all.json'))
for sid in ['78-348973','78-538048','78-616589']:
  p=[q for q in PEN if q['source_id']==sid][0]; num=sid[3:]; t=B.get(num)
  if not t: rej.append(('PENNY',p['name'],'kein BILLA-Zwilling')); continue
  if '_raw' in t:
    tw=t['_raw']; nut=tw['nutrition_100g']; tname=tw['name']; tsize=tw['size_g']; turl=tw['source_url']; man=tw.get('producer')
  else:
    nut={x:t.get(f'{x}_100') for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt') if t.get(f'{x}_100') is not None}; tname=t['name']; tsize=t.get('size_g'); turl=t['url']; man=t.get('manufacturer')
  if tsize!=p['size_g']: rej.append(('PENNY',p['name'],f'Packungsgröße weicht vom BILLA-Zwilling ab ({tsize} vs {p["size_g"]})')); continue
  q=dict(p); q['nutrition_100g']=nut; q['producer']=man
  nm=tname if tname.lower().startswith((p.get('brand') or '').lower()) else f"{p.get('brand')} {p['name'].rstrip('*')}"
  add(q,'PENNY','Tiefkühl (TK)','TK-Fisch' if 'Fisch' in (p['category'] or '')+tname or 'Goldschatz' in tname else 'TK-Gericht',p['price_eur'],
      f'food-connectors/penny {D} (penny.at Online-Sortiment, Listenpreis)',f'BILLA Online-Shop Etikett des identischen REWE-Artikels {num} ({turl}); penny.at nennt keine Nährwerte {D}',
      'PENNY Filialen Linz (Filialkauf)',name=nm,extra={'nut_twin_url':turl})
json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(slot=SLOT,added=new,rejected=rej),open('hourly/added_2026-10-13T17.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'])
