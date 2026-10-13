# hourly T21 (2026-10-13T21): merge verified SPAR (spar-shop search API + identical-product twin label data), Gurkerl and MPreis candidates into connectors_new.json
# NEW in T20: Gurkerl rows whose composition API has a single obvious decimal/field slip (e.g. protein 26 instead of 2.6) are corrected ONLY when Open Food Facts
#  for the identical EAN agrees on kcal (±3 %) and on all other macros, differs in at most one macro field, and OFF quantity does not contradict the pack size; the OFF value replaces that one field (nut_source documents it).
# same gates as T16 (nutrition present+consistent, price+size>=50 g, true heat-up meal, not yet present by url/sku/EAN/name+store)
# MPreis items without a Nährwerte tab: only when the identical EAN has Open Food Facts nutriments per 100 g and OFF quantity does not contradict the MPreis pack size (nut_source documents it).
# Brand for MPreis items without JSON-LD brand: OFF 'brands' of the identical EAN (brand_source documents it).
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-13'; SLOT='2026-10-13T21'
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
OFF=json.load(open('hourly/off_t18_2026-10-13T18.json')); OFF.update(json.load(open('hourly/off_t20_2026-10-13T20.json')))
def offqty_ok(q,g):
  if not q: return True
  m=re.findall(r'(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)\b',q.lower())  # T20: ml/l included (soups: 1 ml ~ 1 g for the contradiction check)
  if not m: return True
  # "1050 g (3 × 350 g)" -> first number is the total
  v=float(m[0][0].replace(',','.'))*(1000 if m[0][1] in ('kg','l') else 1)
  return abs(v-g)<=max(10,0.03*g)

OFF=json.load(open('hourly/off_t21_2026-10-13T21.json'))
def offqty_ok(q,g):
  if not q: return True
  m=re.findall(r'(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)\b',q.lower())
  if not m: return True
  v=float(m[0][0].replace(',','.'))*(1000 if m[0][1] in ('kg','l') else 1)
  return abs(v-g)<=max(10,0.03*g)
NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
# --- SPAR: price/stock/image from the SPAR public search API; label data (nutrition per 100 g, EAN, producer) only from an IDENTICAL product row
#     (same brand, same product words, pack size within 3 %) already in the dataset from another chain; all twins must agree on kcal within 3 %.
SPSEL={'6573836','2020005546097','2020002695026','2020002695033','5305964','2020005391710','2020005391765','4047803','2020003736155','6751043','2438917','7222580',
       '3238356','3061275','2020001310036','145893','5897278','68451','6750954','2020005860711','2020006248624','2020005555815','3306086'}
for t in json.load(open('/tmp/h21/spar_twins.json')):
  p=t['spar']
  if p['source_id'] not in SPSEL: continue
  if (p['extra'] or {}).get('stock_status')!='inStock': rej.append(('SPAR',p['name'],'nicht lagernd laut SPAR-API')); continue
  tw=[x for x in t['twins'] if x.get('kcal_100')]
  ks=[float(x['kcal_100']) for x in tw]
  if max(ks)-min(ks)>0.03*min(ks): rej.append(('SPAR',p['name'],f'Zwillings-Nährwerte widersprüchlich {sorted(set(ks))}')); continue
  tw.sort(key=lambda x:(not x.get('ean'),not x.get('manufacturer')))
  z=tw[0]
  n={k:z.get(f'{k}_100') for k in NUTK}
  q=dict(p); q['nutrition_100g']={k:v for k,v in n.items() if v is not None}; q['ean']=z.get('ean'); q['producer']=z.get('manufacturer'); q['producer_id']=z.get('producer_id'); q['origin']=z.get('origin')
  ex=dict(price_regular_eur=p['extra'].get('regular_price_eur'),spar_article=p['source_id'],twin_url=z.get('url'),twin_store=z.get('store'))
  if p['extra'].get('on_promotion'): ex['offer_text']='SPAR Aktion (API is-on-promotion)'
  nsrc=f"Etikett-Nährwerte je 100 g vom identischen Produkt (Marke+Bezeichnung+Packung {z.get('size_g')} g) bei {z.get('store')} ({z.get('url')}; dortige Quelle: {z.get('nut_source') or 'Shopseite'}); SPAR-Index ohne Nährwerte {D}"
  if z.get('manufacturer'): ex['manufacturer_source']=f"Herstellerangabe des identischen Produkts bei {z.get('store')} ({z.get('url')})"
  sc=p.get('category') or ''; nm=p['name']
  pk='Tiefkühl (TK)' if 'Tiefkühlung' in sc else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in sc else (None if 'Gazpacho' in nm else z.get('packaging'))  # SPAR shelf path; ambient container type from the twin row (cans), Gazpacho container unknown
  cat=('Tiefkühlpizza' if re.search(r'Piccolinis|Oetker',nm) else 'Suppe/Eintopf' if 'Suppen' in sc else 'Mehlspeisen/Desserts' if re.search(r'knödel|Mohnnudeln',nm) else 'Paniert/Nuggets' if re.search(r'Nuggets|Sticks',nm)
       else 'TK-Fisch' if 'Dorsch' in nm else 'Dosengerichte' if 'Vorratsschrank' in sc else 'Fertiggerichte')
  add(q,'SPAR',pk,cat,p['price_eur'],f"food-connectors/spar-shop {D} (SPAR public search API search-spar.spar-ics.com, article {p['source_id']}, {p['extra'].get('stock_status')})",nsrc,'SPAR/INTERSPAR Filialen Linz',extra=ex)
# --- MPreis (robots-allowed product pages, JSON-LD offer + Nährwerte-Tab je 100 g), leftover T20 walk
MPSEL={'807037':'Iglo Brezel Fischstäbchen MSC','809317':'Iglo Backfischstäbchen MSC','366169':'Alnatura Bio Fischstäbchen','611119':'Rügenwalder Mühle Vegane Mühlen Cordon Bleu',
       '611649':'Planted. Nuggets','233128':'Fine Schlutzkrapfen mit Speckfüllung','233127':'Fine Schlutzkrapfen mit Spinatfüllung','365310':'Alnatura Bio Dinkel Tortelloni Ricotta Spinat'}
for p in json.load(open('/tmp/h20/mpreis_new.json'))+json.load(open('/tmp/h20/mpreis_new2.json')):
  if p['source_id'] not in MPSEL: continue
  c=p['category'] or ''; full=MPSEL.pop(p['source_id'])
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Kühlregal (Menüschale/frisch)'
  cat='TK-Fisch' if 'stäbchen' in full else 'Paniert/Nuggets' if re.search('Cordon|Nuggets',full) else 'Frische Pasta'
  ex={}
  o=OFF.get(str(p.get('ean'))) or {}
  if o.get('product_name'): ex['off_match']=f"OFF {p.get('ean')} '{o.get('product_name')}' ({o.get('brands')}, {o.get('quantity')})"
  add(p,'MPreis',pk,cat,p['price_eur'],f'food-connectors/mpreis-shop {D} (category pages + sitemap, product JSON-LD offer price, {p["extra"].get("availability")})',f'MPreis Shop Produktseite, Nährwerte je 100 g {D}','MPreis Filiale Linz / MPreis Shop (AT)',name=full,extra=ex)
# --- Gurkerl (products/prices/stock API + composition API), leftover T20 walk
GSEL={'49189','49190','49191','49192','31596'}
for p in json.load(open('hourly/cand_gurkerl_2026-10-13T21.json')):
  if p['source_id'] not in GSEL: continue
  nm=p['name'].replace('™','')
  cat='Asia-Gericht' if 'Street Food' in nm else 'Fleischgericht'
  pk='Kühlregal (Menüschale/frisch)' if 'Kühlregal' in (p.get('category') or '') else None  # Vorratsschrank pouch: container type not stated → unknown
  add(p,'Gurkerl.at',pk,cat,p['price_eur'],f'food-connectors/gurkerl {D} (category walk + search, products/prices/stock API, inStock)',f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',name=nm)
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=rej),open('hourly/added_2026-10-13T21.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:30])
# NOTE (post-gate, applied surgically to connectors_new.json + added file): dropped Iglo Hühner Nuggets im Backteig (SPAR; pipeline 'teig' filter),
#  Ben's Original Street Food x3 (score.py 'noodle' → Trocken/Instant, container not documented) and Alnatura Dinkel Tortelloni (dry pasta);
#  Fine Schlutzkrapfen packaging set to None (MPreis shelf 'Teigwaren' – chilled/ambient not stated).
