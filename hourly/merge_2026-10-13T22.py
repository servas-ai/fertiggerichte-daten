# hourly T22 (2026-10-13T22): merge verified BILLA (detail API), MPreis (product pages; OFF-by-EAN / identical-product twins where the page has no Nährwerte) and Gurkerl (composition API) candidates into connectors_new.json
# NEW in T20: Gurkerl rows whose composition API has a single obvious decimal/field slip (e.g. protein 26 instead of 2.6) are corrected ONLY when Open Food Facts
#  for the identical EAN agrees on kcal (±3 %) and on all other macros, differs in at most one macro field, and OFF quantity does not contradict the pack size; the OFF value replaces that one field (nut_source documents it).
# same gates as T16 (nutrition present+consistent, price+size>=50 g, true heat-up meal, not yet present by url/sku/EAN/name+store)
# MPreis items without a Nährwerte tab: only when the identical EAN has Open Food Facts nutriments per 100 g and OFF quantity does not contradict the MPreis pack size (nut_source documents it).
# Brand for MPreis items without JSON-LD brand: OFF 'brands' of the identical EAN (brand_source documents it).
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-13'; SLOT='2026-10-13T22'
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

OFF=json.load(open('hourly/off_t22_2026-10-13T22.json'))
def offqty_ok(q,g):
  if not q: return True
  m=re.findall(r'(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)\b',q.lower())
  if not m: return True
  v=float(m[0][0].replace(',','.'))*(1000 if m[0][1] in ('kg','l') else 1)
  return abs(v-g)<=max(10,0.03*g)
NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
ALL=S+cn
# --- BILLA (product-discovery detail API: Nährwerte je 100 g unzubereitet, Hersteller, storage, Normalpreis)
BSEL={'00-423347','00-822507','00-730948','00-306542','00-306554','00-13992','00-886424','00-680707','00-891310','00-758304','00-891835','00-692685','00-892041','00-892049'}
for p in json.load(open('hourly/cand_billa_2026-10-13T22.json')):
  if p['source_id'] not in BSEL: continue
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  nm=p['name']
  cat=('Tiefkühlpizza' if re.search(r'Pizza|Suprema|Piccolinis',nm) else 'Paniert/Nuggets' if re.search(r'garnelen',nm,re.I) else 'TK-Fisch' if re.search(r'Dorsch|Scholle|Fisch|Knusper Abenteuer',nm) else 'Fertiggerichte')
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}"
  add(p,'BILLA',pk,cat,price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',extra=ex)
# --- MPreis (robots-allowed product pages: JSON-LD offer + Nährwerte-Tab je 100 g)
# Pages without Nährwerte: (a) OFF nutriments of the IDENTICAL EAN when OFF quantity does not contradict the pack size, or
#  (b) identical-product twin rows (same brand + product words + pack size within 3 %) of other chains, all twins agreeing on kcal within 3 % (T21 SPAR rule).
TWIN={'802246':['https://www.gurkerl.at/3601-wagner-piccolinis-drei-kaese-tiefgekuehlt','https://shop.billa.at/produkte/wagner-piccolinis-dreikaese-00438048'],
      '802284':['https://www.gurkerl.at/3602-wagner-piccolinis-salami-tiefgekuehlt','https://shop.billa.at/produkte/wagner-piccolinis-salami-00427523'],
      '802223':['https://www.gurkerl.at/25924-wagner-piccolinis-tomate-mozzarella-tiefgekuehlt','https://shop.billa.at/produkte/wagner-piccolinis-tomate-mozzarella-009'],
      '803234':['https://www.gurkerl.at/3604-wagner-pizza-steinofenpizza-diavlo-tiefgekuehlt','https://shop.billa.at/produkte/wagner-steinofen-pizza-diavolo-00825921'],
      '815059':['https://shop.billa.at/produkte/wagner-steinofen-pizza-salami-00788311'],
      '803176':['https://shop.billa.at/produkte/wagner-steinofen-pizza-schinken-0040683']}
def twins(prefixes): return [x for x in ALL if any(str(x.get('url') or '').startswith(u) for u in prefixes) and x.get('kcal_100')]
MPNAME={'802246':'Wagner Piccolinis Drei-Käse','802284':'Wagner Piccolinis Salami','802223':'Wagner Piccolinis Tomate-Mozzarella','803234':'Wagner Steinofen Pizza Diavolo','815059':'Wagner Steinofen Pizza Salami','803176':'Wagner Steinofen Pizza Schinken'}
MPSKIP={'770161':'keine Nährwerte an der Quelle (MPreis-Seite ohne Nährwerte, keine EAN)','738005':'keine Nährwerte an der Quelle (MPreis-Seite ohne Nährwerte, keine EAN)','606526':'keine Nährwerte an der Quelle (MPreis-Seite ohne Nährwerte, keine EAN)',
        '812013':'OFF-Nährwerte für Panier-Nuggets unplausibel (1,2 g Fett) – nicht übernommen','803726':'OFF-Packungsgröße 900 g widerspricht MPreis 1007 g','803725':'OFF-Packungsgröße 1050 g widerspricht MPreis 1200 g',
        '367104':'OFF-EAN ist 350-ml-Variante, MPreis 560 g – widersprüchlich','585629':'OFF ohne Nährwerte','226115':'EAN nicht in OFF, Seite ohne Nährwerte'}
for p in json.load(open('hourly/cand_mpreis_2026-10-13T22.json')):
  sid=p['source_id']; c=p.get('category') or ''; br=p.get('brand') or ''
  full=MPNAME.get(sid) or (p['name'] if (not br or br in ('M',) or p['name'].lower().startswith(br.lower())) else f"{br} {p['name']}")
  if sid in MPSKIP: rej.append(('MPreis',full,MPSKIP[sid])); continue
  if (p.get('extra') or {}).get('availability')!='InStock': rej.append(('MPreis',full,'nicht lagernd')); continue
  ex={}; nsrc=f'MPreis Shop Produktseite, Nährwerte je 100 g {D}'
  if not (p.get('nutrition_100g') or {}).get('kcal'):
    o=OFF.get(str(p.get('ean'))) if p.get('ean') else None
    if o and (o.get('n100') or {}).get('kcal') and offqty_ok(o.get('quantity'),p['size_g']):
      p['nutrition_100g']={k:v for k,v in o['n100'].items() if v is not None}
      nsrc=f"Open Food Facts EAN {p['ean']} ('{o.get('product_name')}', {o.get('brands')}, {o.get('quantity')}; nutriments je 100 g) – MPreis-Seite ohne Nährwerte, {D}"
      ex['off_match']=f"OFF {p['ean']} '{o.get('product_name')}' ({o.get('brands')}, {o.get('quantity')})"
    elif sid in TWIN:
      tw=twins(TWIN[sid]); tw=[x for x in tw if abs(float(x['size_g'])-p['size_g'])<=0.03*p['size_g']]
      ks=[float(x['kcal_100']) for x in tw]
      if not tw: rej.append(('MPreis',full,'kein identischer Zwilling mit Nährwerten')); continue
      if max(ks)-min(ks)>0.03*min(ks): rej.append(('MPreis',full,f'Zwillings-Nährwerte widersprüchlich {sorted(set(ks))}')); continue
      tw.sort(key=lambda x:(not x.get('ean'),not x.get('manufacturer'))); z=tw[0]
      p['nutrition_100g']={k:z.get(f'{k}_100') for k in NUTK if z.get(f'{k}_100') is not None}
      p['ean']=p.get('ean') or z.get('ean'); p['producer']=p.get('producer') or z.get('manufacturer'); p['producer_id']=p.get('producer_id') or z.get('producer_id')
      nsrc=f"Etikett-Nährwerte je 100 g vom identischen Produkt (Marke+Bezeichnung+Packung {z.get('size_g')} g) bei {z.get('store')} ({z.get('url')}); {len(tw)} Zwilling(e), kcal {sorted(set(ks))}; MPreis-Seite ohne Nährwerte {D}"
      ex.update(twin_url=z.get('url'),twin_store=z.get('store'))
      if z.get('manufacturer'): ex['manufacturer_source']=f"Herstellerangabe des identischen Produkts bei {z.get('store')} ({z.get('url')})"
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else None  # MPreis 'Fertigmenüs'/'Suppen' shelf: chilled vs ambient not stated
  cat=('Tiefkühlpizza' if 'Pizza' in c else 'TK-Fisch' if re.search('stäbchen',full,re.I) else 'Paniert/Nuggets' if re.search(r'nuggets|schnitzel',full,re.I) else
       'Vorspeise (Gebackenes)' if re.search(r'Back-|Gebackene',full) else 'Suppe/Eintopf' if re.search('Gazpacho|Suppe',full) else 'Fertiggerichte')
  add(p,'MPreis',pk,cat,p['price_eur'],f'food-connectors/mpreis-shop {D} (product page JSON-LD offer price, {p["extra"].get("availability")})',nsrc,'MPreis Filiale Linz / MPreis Shop (AT)',name=full,extra=ex)
# --- Gurkerl (products/prices/stock API + composition API), leftovers of the T20 walk
GSEL={'5909','5952','29967','31528','31529','31530','42103','6795','2673','6084','25925','4144','45894','22185','21878','46402','44765'}
GREJ={'45894':'keine Nährwerte an der Quelle (Composition leer, EAN fehlt)','22185':'keine Nährwerte an der Quelle (EAN nicht in OFF)','21878':'keine Nährwerte an der Quelle (EAN nicht in OFF)',
      '46402':'keine Nährwerte an der Quelle','44765':'keine Nährwerte an der Quelle (EAN nicht in OFF)'}
for p in json.load(open('hourly/cand_gurkerl_2026-10-13T22.json')):
  sid=p['source_id']
  if sid not in GSEL: continue
  nm=re.sub(r'\s*\((tiefgekühlt|gefroren)\)','',p['name']).replace('WIENER MITZL - Das pflanzliche Schnitzel','Wiener Mitzl pflanzliches Schnitzel')
  if sid in GREJ: rej.append(('Gurkerl.at',nm,GREJ[sid])); continue
  if not (p.get('extra') or {}).get('in_stock'): rej.append(('Gurkerl.at',nm,'nicht lagernd')); continue
  c=p.get('category') or ''
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in c else None
  cat='Tiefkühlpizza' if 'Pizza' in c else 'TK-Fisch' if re.search('Fisch|Kabeljau',nm) else 'Suppe/Eintopf' if 'Suppe' in nm else 'Paniert/Nuggets'
  add(p,'Gurkerl.at',pk,cat,p['price_eur'],f'food-connectors/gurkerl {D} (T20 walk ids, fresh products/prices/stock API {D}, inStock)',f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',name=nm)
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=rej),open('hourly/added_2026-10-13T22.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:30])
