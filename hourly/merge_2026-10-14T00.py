# hourly T00 (2026-10-14T00): merge verified MPreis (sitemap gap, product pages + Nährwerte tab), BILLA (brand/dish stem search + detail API), Gurkerl (search walk + composition API) and SPAR (search API + identical-product twin label data) candidates into connectors_new.json — same gates as T23
# NEW in T20: Gurkerl rows whose composition API has a single obvious decimal/field slip (e.g. protein 26 instead of 2.6) are corrected ONLY when Open Food Facts
#  for the identical EAN agrees on kcal (±3 %) and on all other macros, differs in at most one macro field, and OFF quantity does not contradict the pack size; the OFF value replaces that one field (nut_source documents it).
# same gates as T16 (nutrition present+consistent, price+size>=50 g, true heat-up meal, not yet present by url/sku/EAN/name+store)
# MPreis items without a Nährwerte tab: only when the identical EAN has Open Food Facts nutriments per 100 g and OFF quantity does not contradict the MPreis pack size (nut_source documents it).
# Brand for MPreis items without JSON-LD brand: OFF 'brands' of the identical EAN (brand_source documents it).
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T00'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (20<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
sk=lambda s:{'gurkerl.at':'gurkerl','gurkerl':'gurkerl','billa':'billa','dm':'dm','penny':'penny','mpreis':'mpreis','spar':'spar','interspar':'spar','spar/interspar':'spar','interspar (live)':'spar'}.get(str(s or '').lower(),str(s or '').lower())
have={(k(x['name']),sk(x.get('store'))) for x in S+cn}; haveU={x.get('url') for x in S+cn}
haveE={(str(x.get('ean')).lstrip('0'),sk(x.get('store'))) for x in S+cn if x.get('ean')}
mpsku={m.group(1) for x in S+cn if 'mpreis' in str(x.get('url')) for m in [re.search(r'-(\d+)$',x.get('url') or '')] if m}
SKIP=re.compile(r'Kaspressknödel$|Leberknödel|Grießnockerl|Gemüse ?Pfanne(?! mit Bulgur)|Gemüse-Pilz-Pfanne|Instantnudeln|Asia Noodles|Kimchi Noodles|Korean BBQ|Bratlinge',re.I)
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

NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
# --- MPreis T00: sitemap gap list (mp_gap_2026-10-14T00.py) -> hand-picked slugs; every accepted row has a Nährwerte tab on the page itself
MPSEL={'227512':'Dosengerichte','812506':'Teigtaschen/Dumplings','810162':'Mehlspeisen/Desserts','806031':'Mehlspeisen/Desserts','803527':'Tiefkühlpizza','200073':'Dosengerichte','366236':'Fertiggerichte'}
MPREJ={'186778':'Würzpaste/Beutelsauce 50 g (Salz 11,5 g/100 g)','186799':'Gewürzsauce 50 g','233119':'Kaspressknödel – Beilage/kalter To-Go-Snack (wie frühere Stunden ausgeschlossen)','850745':'Hot-Dog-Brötchen (Gebäck, keine Nährwerte)',
       '242793':'Weichkäse (Böreklik)','296776':'Reisbeilage (Express-Reis natur)','611577':'pflanzliche Fleischalternative als Zutat (Kebab-Streifen roh zum Anbraten)','602996':'frische Teigwaren (Rohware, keine Nährwerte)'}
for p in json.load(open('hourly/cand_mpreis_2026-10-14T00.json')):
  sid=p['source_id']; c=p.get('category') or ''; br=p.get('brand') or ''
  full=p['name'] if (not br or p['name'].lower().startswith(br.lower())) else f"{br} {p['name']}"
  if sid in MPREJ: rej.append(('MPreis',full,MPREJ[sid])); continue
  if sid not in MPSEL: continue
  if (p.get('extra') or {}).get('availability')!='InStock': rej.append(('MPreis',full,'nicht lagernd')); continue
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Konserve/Dose' if 'Dosengerichte' in c else 'Kühlregal (To-Go)' if 'To-Go' in c else None
  add(p,'MPreis',pk,MPSEL[sid],p['price_eur'],f'food-connectors/mpreis-shop {D} (product page JSON-LD offer price, {p["extra"].get("availability")})',f'MPreis Shop Produktseite, Nährwerte je 100 g {D}','MPreis Filiale Linz / MPreis Shop (AT)',name=full)
# --- Gurkerl T00 (search walk, fresh stock, composition API)
GSEL={'32859':'TK-Fisch','36971':'TK-Fisch','45599':'TK-Fisch','45598':'TK-Fisch','45600':'TK-Fisch'}
for p in json.load(open('hourly/cand_gurkerl_search_2026-10-14T00.json')):
  sid=p['source_id']; nm=re.sub(r'\s*\((tiefgekühlt|gefroren)\)','',p['name']).replace('™','')
  if sid not in GSEL: continue
  c=p.get('category') or ''
  pk='Tiefkühl (TK)' if ('Tiefk' in c or 'tiefgekühlt' in p['name']) else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in c else None
  add(p,'Gurkerl.at',pk,GSEL[sid],p['price_eur'],f'food-connectors/gurkerl {D} (T00 search walk, products/prices/stock API, inStock)',f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',name=nm)
rej.append(('Gurkerl.at','Iglo Backhendlstreifen mit Kürbiskernen','nicht lagernd (Gurkerl stock API)'))
# --- BILLA T00 (brand/dish stem search + detail API)
BSEL={'00-746412':'Paniert/Nuggets','00-616605':'Paniert/Nuggets','00-721002':'Paniert/Nuggets','00-723595':'Paniert/Nuggets','00-878830':'Paniert/Nuggets','00-648634':'TK-Fisch','00-447286':'TK-Fisch'}
BREJ={'00-692685':'BILLA-API Kohlenhydrate 279 g/100 g (Tippfehler an der Quelle, kein EAN für OFF-Abgleich) – nicht übernommen','00-889324':'Kabeljau natur (Rohware, 0 g KH)',
      '00-892041':'keine Packungsgröße an der Quelle (Menüschale)','00-892049':'keine Packungsgröße an der Quelle (Menüschale)'}
for p in json.load(open('hourly/cand_billa_2026-10-14T00.json')):
  if p['source_id'] in BREJ: rej.append(('BILLA',p['name'],BREJ[p['source_id']])); continue
  if p['source_id'] not in BSEL: continue
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}"
  add(p,'BILLA',pk,BSEL[p['source_id']],price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',extra=ex)
# --- SPAR T00 (spar-shop search API; label data only from an IDENTICAL product row already in the dataset: same brand, same product words, pack size within 3 %, all twins agree on kcal within 3 %)
SPSEL=set(json.load(open('hourly/spar_sel_2026-10-14T00.json'))) if os.path.exists('hourly/spar_sel_2026-10-14T00.json') else set()
rej.append(('SPAR','Iglo Pasta Asciutta Sauce im Block','Sauce (keine Mahlzeit)'))
if os.path.exists('/tmp/h00/spar_twins.json'):
 for t in json.load(open('/tmp/h00/spar_twins.json')):
  p=t['spar']
  if p['source_id'] not in SPSEL: continue
  if (p['extra'] or {}).get('stock_status')!='inStock': rej.append(('SPAR',p['name'],'nicht lagernd laut SPAR-API')); continue
  tw=[x for x in t['twins'] if x.get('kcal_100')]
  ks=[float(x['kcal_100']) for x in tw]
  if max(ks)-min(ks)>0.03*min(ks): rej.append(('SPAR',p['name'],f'Zwillings-Nährwerte widersprüchlich {sorted(set(ks))}')); continue
  tw.sort(key=lambda x:(not x.get('ean'),not x.get('manufacturer')))
  z=tw[0]
  n={k_:z.get(f'{k_}_100') for k_ in NUTK}
  q=dict(p); q['nutrition_100g']={k_:v for k_,v in n.items() if v is not None}; q['ean']=z.get('ean'); q['producer']=z.get('manufacturer'); q['producer_id']=z.get('producer_id'); q['origin']=z.get('origin')
  ex=dict(price_regular_eur=p['extra'].get('regular_price_eur'),spar_article=p['source_id'],twin_url=z.get('url'),twin_store=z.get('store'))
  if p['extra'].get('on_promotion'): ex['offer_text']='SPAR Aktion (API is-on-promotion)'
  nsrc=f"Etikett-Nährwerte je 100 g vom identischen Produkt (Marke+Bezeichnung+Packung {z.get('size_g')} g) bei {z.get('store')} ({z.get('url')}; dortige Quelle: {z.get('nut_source') or 'Shopseite'}); SPAR-Index ohne Nährwerte {D}"
  if z.get('manufacturer'): ex['manufacturer_source']=f"Herstellerangabe des identischen Produkts bei {z.get('store')} ({z.get('url')})"
  sc=p.get('category') or ''
  pk='Tiefkühl (TK)' if 'Tiefkühlung' in sc else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in sc else z.get('packaging')
  add(q,'SPAR',pk,z.get('category') or 'Fertiggerichte',p['price_eur'],f"food-connectors/spar-shop {D} (SPAR public search API search-spar.spar-ics.com, article {p['source_id']}, {p['extra'].get('stock_status')})",nsrc,'SPAR/INTERSPAR Filialen Linz',extra=ex)
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  AF='hourly/added_2026-10-14T00.json'  # second pass (SPAR after twin match) appends; earlier-pass rows re-seen as 'schon vorhanden' are not re-logged
  prev=json.load(open(AF)) if os.path.exists(AF) else dict(added=[],rejected=[])
  pu={r['url'] for r in prev['added']}; rej=[x for x in rej if not (x[2].startswith('schon vorhanden') and any(r['name']==x[1] for r in prev['added']))]
  pr={tuple(x) for x in prev['rejected']}
  json.dump(dict(slot=SLOT,added=prev['added']+[r for r in new if r['url'] not in pu],rejected=prev['rejected']+[list(x) for x in rej if tuple(x) not in pr]),open(AF,'w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:30],'|',r.get('ean'))
