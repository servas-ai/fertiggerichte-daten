# hourly T01 (2026-10-14T01): merge verified MPreis / BILLA / SPAR twin candidates into connectors_new.json
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T01'
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
mpsku={m.group(1) for x in S+cn if 'mpreis' in str(x.get('url') or '') for m in [re.search(r'-(\d+)$',x.get('url') or '')] if m}
SKIP=re.compile(r'Kaspressknödel$|Leberknödel|Grießnockerl|Gemüse ?Pfanne(?! mit Bulgur)|Gemüse-Pilz-Pfanne|Instantnudeln|Asia Noodles|Kimchi Noodles|Korean BBQ|Bratlinge|Eierspätzle|Spätzle Knöpfle',re.I)
new,rej=[],[]
def add(p,store,pk,cat,price,psrc,nsrc,delivery,name=None,extra={}):
  nm=re.sub(r'\s+',' ',name or p['name']).strip(); n=p.get('nutrition_100g') or {}
  if SKIP.search(nm): rej.append((store,nm,'Beilage/Instant – kein Heiß-Fertiggericht')); return
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
  have.add((k(nm),sk(store))); haveU.add(p['source_url']);
  if p.get('ean'): haveE.add((str(p['ean']).lstrip('0'),sk(store)))
  if sk(store)=='mpreis': mpsku.add(str(p.get('source_id')))
  new.append(r)

NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')

# --- MPreis T01 ---
MPSEL={
  '804935':'Paniert/Nuggets','809027':'Paniert/Nuggets','810166':'Mehlspeisen/Desserts','805014':'Tiefkühlpizza',
  '814504':'TK-Fisch','805610':'TK-Fisch','815069':'TK-Fisch','805660':'TK-Fisch','805284':'TK-Fisch',
  '804923':'TK-Fisch','805269':'TK-Fisch','811848':'TK-Fisch','811846':'TK-Fisch','81219':'TK-Fisch',
  '292078':'Pasta-Fertiggericht','292010':'Pasta-Fertiggericht','292006':'Pasta-Fertiggericht',
  '814507':'Tiefkühlpizza','186411':'Asia-Fertiggericht','186407':'Asia-Fertiggericht','186408':'Asia-Fertiggericht',
  '812294':'Paniert/Nuggets',
}
MPREJ={
  '606526':'keine Nährwerte an der Quelle','226502':'schon vorhanden (name)',
  '803234':'keine Nährwerte an der Quelle','802223':'keine Nährwerte an der Quelle',
  '133557':'Knabbergebäck/Cocktail, keine Nährwerte','365205':'Beutelsuppe 46 g',
  '365204':'Beutelsuppe ohne Packungsgewicht','367104':'keine Nährwerte an der Quelle',
  '845098':'Risotto-Reis roh / keine Nährwerte','275303':'Würzmischung Air-Fryer (Beutelsauce)',
  '275305':'Würzmischung Air-Fryer','275304':'Würzmischung Air-Fryer',
  '611572':'keine Nährwerte an der Quelle','611160':'keine Nährwerte an der Quelle',
  '812011':'keine Nährwerte an der Quelle','803726':'keine Nährwerte an der Quelle',
  '365847':'Cocktailgebäck Pizza Minis','365310':'frische Teigwaren (Rohware)',
  '365715':'keine Nährwerte an der Quelle','365194':'keine Nährwerte an der Quelle',
  '811410':'Eierspätzle/Knöpfle – Beilage ohne Sauce',
}
for p in json.load(open('hourly/cand_mpreis_2026-10-14T01.json')):
  sid=p['source_id']; br=p.get('brand') or ''
  full=p['name'] if (not br or p['name'].lower().startswith(br.lower())) else f"{br} {p['name']}"
  if sid in MPREJ: rej.append(('MPreis',full,MPREJ[sid])); continue
  if sid not in MPSEL: continue
  if (p.get('extra') or {}).get('availability')!='InStock': rej.append(('MPreis',full,'nicht lagernd')); continue
  c=p.get('category') or ''
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Konserve/Dose' if ('Dosen' in c or 'Konserve' in c) else 'Vorratsschrank (Beutel/Box)' if 'Fertiggerichte' in c else None
  add(p,'MPreis',pk,MPSEL[sid],p['price_eur'],f'food-connectors/mpreis-shop {D} (product page JSON-LD offer price, {p["extra"].get("availability")})',f'MPreis Shop Produktseite, Nährwerte je 100 g {D}','MPreis Filiale Linz / MPreis Shop (AT)',name=full)

# --- BILLA T01 ---
BSEL={
  '00-10042':'TK-Fisch','00-708562':'TK-Fisch','00-886427':'Paniert/Nuggets',
  '00-723753':'Paniert/Nuggets','00-723755':'Burger/Patties','00-404589':'Burger/Patties',
  '00-416106':'TK-Fisch','00-909535':'TK-Fisch','00-431606':'TK-Fisch',
  '00-868704':'Paniert/Nuggets','00-746319':'TK-Fisch','00-667910':'Paniert/Nuggets',
}
BREJ={
  '00-901948':'kalte Salat-Bowl (kein Heat-up)',
  '00-730112':'Scholle natur (Rohware)','00-82502':'Dorsch natur (Rohware)',
  '00-3298':'Polar-Dorsch natur (Rohware)','00-605251':'Polar-Dorsch natur Vorteilspack (Rohware)',
  '00-886410':'Polar-Dorsch Filets natur (Rohware)',
}
for p in json.load(open('hourly/cand_billa_2026-10-14T01.json')):
  if p['source_id'] in BREJ: rej.append(('BILLA',p['name'],BREJ[p['source_id']])); continue
  if p['source_id'] not in BSEL: continue
  e=p.get('extra') or {}; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}"
  add(p,'BILLA',pk,BSEL[p['source_id']],price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',extra=ex)

# --- Gurkerl T01 ---
rej.append(('Gurkerl.at','Iglo Backhendlstreifen mit Kürbiskernen','nicht lagernd (Gurkerl stock API)'))
rej.append(('Gurkerl.at','Marks & Spencer 4 Battered Haddock Fillets','nicht lagernd (Gurkerl stock API)'))
rej.append(('Gurkerl.at','Marks & Spencer 4 Wild Icelandic Cod Fillets','Rohware natur (kein paniertes Heat-up)'))
rej.append(('Gurkerl.at','Everest Bao Buns','frischer Teig / Bao-Teiglinge (keine fertige Mahlzeit)'))

# --- SPAR T01 (identical-product twin nutrition) ---
SPOK={'111607','482332','3545034','2020002185862'}  # consistent twin kcal only
SPREJ={
  '2020000674139':'Zwillings-Nährwerte widersprüchlich [256, 289]',
  '3306086':'Zwillings-Nährwerte widersprüchlich [229, 237]',
  '2438917':'Zwillings-Nährwerte widersprüchlich [251, 271]',
}
if os.path.exists('/tmp/h01/spar_twins.json'):
 for t in json.load(open('/tmp/h01/spar_twins.json')):
  p=t['spar']; sid=str(p['source_id'])
  if sid in SPREJ: rej.append(('SPAR',p['name'],SPREJ[sid])); continue
  if sid not in SPOK: continue
  if (p.get('extra') or {}).get('stock_status')!='inStock': rej.append(('SPAR',p['name'],'nicht lagernd laut SPAR-API')); continue
  tw=[x for x in t['twins'] if x.get('kcal_100')]
  ks=[float(x['kcal_100']) for x in tw]
  if max(ks)-min(ks)>0.03*min(ks): rej.append(('SPAR',p['name'],f'Zwillings-Nährwerte widersprüchlich {sorted(set(ks))}')); continue
  tw.sort(key=lambda x:(not x.get('ean'),not x.get('manufacturer')))
  z=tw[0]
  n={k_:z.get(f'{k_}_100') for k_ in NUTK}
  q=dict(p); q['nutrition_100g']={k_:v for k_,v in n.items() if v is not None}; q['ean']=z.get('ean'); q['producer']=z.get('manufacturer'); q['producer_id']=z.get('producer_id'); q['origin']=z.get('origin')
  ex=dict(price_regular_eur=(p.get('extra') or {}).get('regular_price_eur'),spar_article=p['source_id'],twin_url=z.get('url'),twin_store=z.get('store'))
  if (p.get('extra') or {}).get('on_promotion'): ex['offer_text']='SPAR Aktion (API is-on-promotion)'
  nsrc=f"Etikett-Nährwerte je 100 g vom identischen Produkt (Marke+Bezeichnung+Packung {z.get('size_g')} g) bei {z.get('store')} ({z.get('url')}; dortige Quelle: {z.get('nut_source') or 'Shopseite'}); SPAR-Index ohne Nährwerte {D}"
  if z.get('manufacturer'): ex['manufacturer_source']=f"Herstellerangabe des identischen Produkts bei {z.get('store')} ({z.get('url')})"
  sc=p.get('category') or ''
  pk='Tiefkühl (TK)' if 'Tiefkühlung' in sc else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in sc else z.get('packaging')
  add(q,'SPAR',pk,z.get('category') or 'Fertiggerichte',p['price_eur'],f"food-connectors/spar-shop {D} (SPAR public search API search-spar.spar-ics.com, article {p['source_id']}, {p['extra'].get('stock_status')})",nsrc,'SPAR/INTERSPAR Filialen Linz',extra=ex)

if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  AF=f'hourly/added_{SLOT}.json'
  json.dump(dict(slot=SLOT,added=new,rejected=[list(x) for x in rej]),open(AF,'w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new))
for x in rej: print(' REJ',*x)
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:35],'|',r.get('ean'))
