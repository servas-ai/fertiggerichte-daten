# hourly T23 (2026-10-13T23): merge verified MPreis (product pages, Nährwerte tab), Gurkerl (search-metadata walk + composition API) and BILLA (brand-stem search + detail API) candidates into connectors_new.json — same gates as T22
# NEW in T20: Gurkerl rows whose composition API has a single obvious decimal/field slip (e.g. protein 26 instead of 2.6) are corrected ONLY when Open Food Facts
#  for the identical EAN agrees on kcal (±3 %) and on all other macros, differs in at most one macro field, and OFF quantity does not contradict the pack size; the OFF value replaces that one field (nut_source documents it).
# same gates as T16 (nutrition present+consistent, price+size>=50 g, true heat-up meal, not yet present by url/sku/EAN/name+store)
# MPreis items without a Nährwerte tab: only when the identical EAN has Open Food Facts nutriments per 100 g and OFF quantity does not contradict the MPreis pack size (nut_source documents it).
# Brand for MPreis items without JSON-LD brand: OFF 'brands' of the identical EAN (brand_source documents it).
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-13'; SLOT='2026-10-13T23'
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

OFF={}
def offqty_ok(q,g):
  if not q: return True
  m=re.findall(r'(\d+(?:[.,]\d+)?)\s*(kg|g|ml|l)\b',q.lower())
  if not m: return True
  v=float(m[0][0].replace(',','.'))*(1000 if m[0][1] in ('kg','l') else 1)
  return abs(v-g)<=max(10,0.03*g)
NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
ALL=S+cn
# --- MPreis T23: hand-picked sitemap slugs (fetch_mpreis_2026-10-13T23.py); every accepted row has a Nährwerte tab on the page itself
MPSEL={'365944':'Fertiggerichte','365790':'Fertiggerichte','820540':'Paniert/Nuggets','815188':'TK-Fisch','813376':'Paniert/Nuggets','804982':'Fertiggerichte','611543':'Fertiggerichte',
       '813759':'TK-Fisch','813754':'TK-Fisch','226502':'Dosengerichte','296774':'Fertiggerichte','812102':'Paniert/Nuggets','812124':'Paniert/Nuggets','80186':'Paniert/Nuggets',
       '770186':'Baguette (warm)','770159':'Baguette (warm)','770154':'Baguette (warm)'}
MPREJ={'365204':'Beutelsuppe (Trockenpulver)','365205':'Beutelsuppe (Trockenpulver)','366299':'Beutelsuppe (Trockenpulver)','366300':'58 g Trockensuppe (Nährwerte je zubereitet)',
       '145786':'Lasagneblätter (Rohware)','366198':'getrocknete Tortellini (Rohware)','365847':'Knabbergebäck','259423':'Suppenkonzentrat (Salz 50 g/100 g)','259421':'Suppenkonzentrat (Salz 50 g/100 g)',
       '81219':'Fischkonserve in Öl (kalt)','233136':'Feinkostsalat ohne Packungsgröße','846120':'Thekenware ohne Marke/Packungsangabe','80120':'Fleischtheke, Zubereitungsstatus unklar',
       '899416':'keine Nährwerte an der Quelle','899436':'keine Nährwerte an der Quelle','812011':'keine Nährwerte an der Quelle','809410':'keine Nährwerte an der Quelle','812171':'keine Nährwerte an der Quelle',
       '733302':'keine Nährwerte/Packung an der Quelle','133557':'Knabbergebäck','278790':'Beutelsuppe (Trockenpulver)','277602':'Beutelsuppe (Trockenpulver)','278404':'Beutelsuppe (Trockenpulver)','278700':'Beutelsuppe (Trockenpulver)'}
for p in json.load(open('hourly/cand_mpreis_2026-10-13T23.json')):
  sid=p['source_id']; c=p.get('category') or ''; br=p.get('brand') or ''
  full=p['name'] if (not br or p['name'].lower().startswith(br.lower())) else f"{br} {p['name']}"
  if sid in MPREJ: rej.append(('MPreis',full,MPREJ[sid])); continue
  if sid not in MPSEL: continue
  if (p.get('extra') or {}).get('availability')!='InStock': rej.append(('MPreis',full,'nicht lagernd')); continue
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Konserve/Dose' if 'Dosengerichte' in c else 'Kühlregal (To-Go)' if 'To-Go' in c else None
  add(p,'MPreis',pk,MPSEL[sid],p['price_eur'],f'food-connectors/mpreis-shop {D} (product page JSON-LD offer price, {p["extra"].get("availability")})',f'MPreis Shop Produktseite, Nährwerte je 100 g {D}','MPreis Filiale Linz / MPreis Shop (AT)',name=full)
# --- Gurkerl T23 (search-metadata walk, fresh stock, composition API)
GSEL={'33500':'Paniert/Nuggets','5953':'Paniert/Nuggets','49191':'Fertiggerichte','40104':'Mehlspeisen/Desserts'}
GREJ={'2673':'Composition-Protein 0,9 g bei paniertem Kabeljau unplausibel – nicht übernommen','25925':'Composition-kcal 812/100 g unplausibel – nicht übernommen','29852':'kalter Wrap (kein Heißgericht)'}
for p in json.load(open('hourly/cand_gurkerl_search_2026-10-13T23.json')):
  sid=p['source_id']; nm=re.sub(r'\s*\((tiefgekühlt|gefroren)\)','',p['name']).replace('™','')
  if sid in GREJ: rej.append(('Gurkerl.at',nm,GREJ[sid])); continue
  if sid not in GSEL: continue
  c=p.get('category') or ''
  pk='Tiefkühl (TK)' if ('Tiefk' in c or 'tiefgekühlt' in p['name']) else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in c else 'Ungekühlt (Beutel)' if 'Vorratsschrank' in c else None
  add(p,'Gurkerl.at',pk,GSEL[sid],p['price_eur'],f'food-connectors/gurkerl {D} (T23 search-metadata walk, products/prices/stock API, inStock)',f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',name=nm)
# --- BILLA T23 (brand-stem search + detail API)
BSEL={'00-774139':'Paniert/Nuggets','00-382821':'TK-Fisch','00-736994':'TK-Fisch','00-723599':'Vorspeise (Gebackenes)','00-734526':'Paniert/Nuggets','00-723600':'Paniert/Nuggets','00-774425':'TK-Fisch','00-774429':'TK-Fisch'}
BREJ={'00-648626':'marinierte Garnelen (Rohware, 0 g KH)'}
for p in json.load(open('hourly/cand_billa_2026-10-13T23.json')):
  if p['source_id'] in BREJ: rej.append(('BILLA',p['name'],BREJ[p['source_id']])); continue
  if p['source_id'] not in BSEL: continue
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}"
  add(p,'BILLA',pk,BSEL[p['source_id']],price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',extra=ex)
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=rej),open('hourly/added_2026-10-13T23.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:30],'|',r.get('ean'))
