# hourly T20 (2026-10-13T20): merge verified Gurkerl (+ MPreis part 2) candidates into connectors_new.json
# NEW in T20: Gurkerl rows whose composition API has a single obvious decimal/field slip (e.g. protein 26 instead of 2.6) are corrected ONLY when Open Food Facts
#  for the identical EAN agrees on kcal (±3 %) and on all other macros, differs in at most one macro field, and OFF quantity does not contradict the pack size; the OFF value replaces that one field (nut_source documents it).
# same gates as T16 (nutrition present+consistent, price+size>=50 g, true heat-up meal, not yet present by url/sku/EAN/name+store)
# MPreis items without a Nährwerte tab: only when the identical EAN has Open Food Facts nutriments per 100 g and OFF quantity does not contradict the MPreis pack size (nut_source documents it).
# Brand for MPreis items without JSON-LD brand: OFF 'brands' of the identical EAN (brand_source documents it).
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-13'; SLOT='2026-10-13T20'
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
# MPreis (robots-allowed product pages, JSON-LD + Nährwerte-Tab je 100 g unzubereitet)
MP=json.load(open('hourly/mp_sel_2026-10-13T20.json'))  # hand-picked T20 MPreis ids (Frank Juice soups, Iglo/Jeden Tag Schlemmerfilet + Ofenbackfisch, Blasko Cordon Bleu/Putenschnitzel)
pool=json.load(open('/tmp/h20/mpreis_new.json'))+(json.load(open('/tmp/h20/mpreis_new2.json')) if os.path.exists('/tmp/h20/mpreis_new2.json') else [])
for p in pool:
  if p['source_id'] not in MP: continue
  c=p['category'] or ''; b=p.get('brand'); e=str(p.get('ean') or '').strip(); o=OFF.get(e) or {}
  ex={}; nsrc=f'MPreis Shop Produktseite, Nährwerte je 100 g (unzubereitet) {D}'
  if not b and o.get('brands'):
    b=o['brands'].split(',')[0].strip(); b={'iglo':'Iglo','DOZZ':'Dozz','Südtiroler kochwerk':'Südtiroler Kochwerk'}.get(b,b)
    ex['brand_source']=f"Open Food Facts 'brands' für EAN {e} ({o.get('product_name')}, {o.get('quantity')}), {D}"
  p=dict(p); p['brand']=b
  if not (p.get('nutrition_100g') or {}).get('kcal'):
    n=o.get('n100') or {}
    if n.get('kcal') and n.get('protein') is not None and offqty_ok(o.get('quantity'),p.get('size_g') or 0):
      p['nutrition_100g']={k:v for k,v in n.items() if v is not None}
      nsrc=f"Open Food Facts nutriments je 100 g für identische EAN {e} ('{o.get('product_name')}', Menge '{o.get('quantity')}'); MPreis-Seite ohne Nährwerttabelle {D}"
    elif n.get('kcal'):
      rej.append(('MPreis',(b or '')+' '+p['name'],f"OFF-Menge '{o.get('quantity')}' widerspricht MPreis-Packung {p.get('size_g')} g – OFF-Nährwerte nicht übernommen")); continue
  full=MP[p['source_id']] or ((b+' '+p['name']) if b and not p['name'].lower().startswith(b.lower()) else p['name'])
  if re.match(r'(?i)frank',b or ''): pk=None  # MPreis 'Dosensuppen' shelf, container type not stated on the page
  elif 'Tiefkühl' in c: pk='Tiefkühl (TK)'
  elif 'To-Go' in c: pk='Kühlregal (Menüschale/frisch)'
  else: pk='Dose/Konserve'
  cat=('TK-Fisch' if re.search(r'Schlemmerfilet|Ofenbackfisch',full) else 'Paniert/Nuggets' if re.search(r'Cordon|gebacken',full) else 'Tiefkühlpizza' if 'Pizza' in c else 'Mehlspeisen/Desserts' if 'Mehlspeisen' in c else 'Suppe/Eintopf' if ('suppe' in c.split(' / ')[-1].lower() or re.search(r'suppe|eintopf',full,re.I)) else
       'Knödel, Spätzle & Co' if 'knödel' in full.lower() else 'Dosengerichte' if 'Dosengerichte' in c else 'TK-Gericht' if 'Tiefkühl' in c else 'Fertiggerichte')
  add(p,'MPreis',pk,cat,p['price_eur'],f'food-connectors/mpreis-shop {D} (category pages + sitemap, product JSON-LD offer price, {p["extra"].get("availability")})',nsrc,'MPreis Filiale Linz / MPreis Shop (AT)',name=full,extra=ex)
# Gurkerl (composition API)
GSEL={'37023','33405','13220','12927','12928','17912','17911','40026','40025','40022','41326','40052'}
MAC=('kcal','fat','satfat','carbs','sugar','protein','salt','fiber')
def off_fix(p):
  n=dict(p.get('nutrition_100g') or {}); e=str(p.get('ean') or ''); o=OFF.get(e) or {}; on=o.get('n100') or {}
  if consistent(n) or not on.get('kcal') or not n.get('kcal') or not offqty_ok(o.get('quantity'),p.get('size_g') or 0): return None
  if abs(on['kcal']-n['kcal'])>0.03*n['kcal']: return None
  diff=[x for x in MAC if x!='kcal' and n.get(x) is not None and on.get(x) is not None and abs(float(n[x])-float(on[x]))>max(0.15,0.03*abs(float(on[x])))]
  if len(diff)!=1: return None
  f=diff[0]; old=n[f]; n[f]=float(on[f])
  if not consistent(n): return None
  return n,f"Gurkerl.at API (composition) {D}; Feld '{f}' {old}→{on[f]} korrigiert nach Open Food Facts identische EAN {e} ('{o.get('product_name')}', Menge '{o.get('quantity')}'; alle übrigen Makros + kcal stimmen überein)"
for p in json.load(open('hourly/cand_gurkerl_2026-10-13T20.json')):
  if p['source_id'] not in GSEL: continue
  c=p.get('category') or ''
  fx=off_fix(p); nsrc=f'Gurkerl.at API (composition) {D}'
  if fx: p=dict(p); p['nutrition_100g'],nsrc=fx
  pk='Tiefkühl (TK)' if ('Tiefkühl' in c or 'tiefgekühlt' in p['name']) else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in c else 'Dose/Konserve' if 'Vorratsschrank' in c else None
  pk=pk or ('Kühlregal (Menüschale/frisch)' if 'Kühlregal' in c else None)
  cat=('Tiefkühlpizza' if 'Pizza' in c else 'TK-Fisch' if 'Cod' in p['name'] else 'Mehlspeisen/Desserts' if 'Süßer' in p['name'] else 'Frische Pasta' if re.search(r'Käsnudel|Nudelteller',p['name']) else 'Knödel, Spätzle & Co' if re.search(r'Gnocchi|Maultaschen',p['name']) else 'Fertiggerichte')
  add(p,'Gurkerl.at',pk,cat,p['price_eur'],f'food-connectors/gurkerl {D} (category walk + search, products/prices/stock API, inStock)',nsrc,'Lieferung nach Linz (Gurkerl.at)')
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=rej),open('hourly/added_2026-10-13T20.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new)); [print(' REJ',*x) for x in rej]
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'])
