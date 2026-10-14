# hourly T05 (2026-10-14T05): merge verified Gurkerl (new public sitemap_base categories not in the adapter's MEAL_CATEGORIES),
# BILLA (catalog diff 12 204 items, detail API) and SPAR (identical-product twin label data) candidates into connectors_new.json
import json,re,os,collections
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T05'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (5<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
sk=lambda s:{'gurkerl.at':'gurkerl','gurkerl':'gurkerl','billa':'billa','spar':'spar','interspar':'spar'}.get(str(s or '').lower(),str(s or '').lower())
have={(k(x['name']),sk(x.get('store'))) for x in S+cn}; haveU={x.get('url') for x in S+cn}
haveE={(str(x.get('ean')).lstrip('0'),sk(x.get('store'))) for x in S+cn if x.get('ean')}
spar_ids={m.group(1) for x in S+cn if 'spar' in str(x.get('url') or '') for m in [re.search(r'/p/(\d+)',x.get('url') or '')] if m}
new,rej=[],[]
NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
def add(p,store,pk,cat,price,psrc,nsrc,delivery,name=None,meal=True,extra={}):
  nm=re.sub(r'\s+',' ',name or p['name']).strip(); n=p.get('nutrition_100g') or {}
  if not n.get('kcal') or n.get('protein') is None: rej.append((store,nm,'keine Nährwerte an der Quelle')); return
  if not consistent(n): rej.append((store,nm,f'Nährwerte inkonsistent/unplausibel an der Quelle {n}')); return
  if not (price and p.get('size_g') and p['size_g']>=50): rej.append((store,nm,'kein Preis/Gewicht')); return
  if p['source_url'] in haveU or (k(nm),sk(store)) in have or (p.get('ean') and (str(p['ean']).lstrip('0'),sk(store)) in haveE): rej.append((store,nm,'schon vorhanden')); return
  if not p.get('image_url'): rej.append((store,nm,'kein Produktfoto')); return
  g=p['size_g']; man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  if man: man=re.sub(r'^(Kontakt|Hersteller|Produzent|Inverkehrbringer)\s*:\s*','',man,flags=re.I)
  r=dict(name=nm,brand=p.get('brand') or None,store=store,price_eur=price,size_g=g,price_per_kg=round(price/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in NUTK},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=(p.get('origin') or '').strip() or None,category=cat,price_source=psrc,price_date=D,nut_source=nsrc,ean=p.get('ean'),packaging=pk,packaging_hint=pk,
    is_meal=True,delivery=delivery,added_slot=SLOT,hourly_kind='Fertiggericht' if meal else 'Heiß-Komponente (paniert/Laibchen)',**extra)
  if (p.get('extra') or {}).get('ingredients'): r['ingredients']=p['extra']['ingredients'][:2000]
  have.add((k(nm),sk(store))); haveU.add(p['source_url'])
  if p.get('ean'): haveE.add((str(p['ean']).lstrip('0'),sk(store)))
  new.append(r)

# --- Gurkerl T05: hand-picked from categories listed in gurkerl.at/sitemap_base.xml (e.g. c135331 Pizzen & Fertiggerichte,
#     c137361/137159 Koreanisch, c137908 Suppen, c135291/137423 Fleisch- & Fischalternativen, c136119 Rösti/Laibchen/Taschen)
TK='Tiefkühl (TK)'; KR='Kühlregal (Menüschale/frisch)'
GSEL={ # id: (category, packaging, meal?)
 '5958':('TK-Fertiggericht',TK,True),'5959':('TK-Fertiggericht',TK,True),'5960':('TK-Fertiggericht',TK,True),
 '41097':('Asia-Fertiggericht',None,True),'40444':('Asia-Fertiggericht',None,True),'40445':('Asia-Fertiggericht',None,True),'40446':('Asia-Fertiggericht',None,True),
 '4144':('Suppe/Eintopf',KR,True),'45117':('TK-Fertiggericht (vegan)',TK,True),'45845':('TK-Fertiggericht (vegan)',TK,True),
 '49391':('TK-Fertiggericht (vegan)',TK,True),'42104':('TK-Fertiggericht (vegan)',TK,True),
 '3944':('Fleischalternative paniert',KR,False),'3945':('Fleischalternative paniert',KR,False),'26532':('Fleischalternative paniert',KR,False),
 '17341':('Fleischalternative paniert',KR,False),'26533':('Fleischalternative paniert',KR,False),'24348':('Fleischalternative paniert',KR,False),
 '28285':('Fleischalternative paniert',KR,False),'47294':('Fleischalternative paniert',KR,False),'18421':('Laibchen',KR,False),
 '1158':('TK-Snack (Rösti-Tasche)',TK,False),'1142':('TK-Snack (Rösti-Tasche)',TK,False)}
GREJ={'25925':None,'45894':None,'46402':None,'22185':None,
 '45803':'Gurkerl-Nährwerte identisch mit planted. schnitzel und abweichend vom MPreis-Etikett derselben EAN (287 vs 270 kcal) – nicht übernommen',
 '45802':'Gurkerl-Nährwerte identisch mit planted. nuggets (vermutlich Kopierfehler an der Quelle) – nicht übernommen',
 '20974':'Seitan natur (nicht paniert/gegart) – Rohzutat','6078':'Gemüsebeilage (Letscho-Gemüse), kein Fertiggericht','43015':'Trockenmischung (Risotto, 358 kcal/100 g)'}
G={p['source_id']:p for p in json.load(open('/tmp/h05/g_cand.json'))}
for sid,p in G.items():
  if sid in GREJ and GREJ[sid]: rej.append(('Gurkerl.at',p['name'],GREJ[sid])); continue
  if sid not in GSEL and sid not in GREJ: continue
  if not p['extra'].get('in_stock'): rej.append(('Gurkerl.at',p['name'],'nicht lagernd')); continue
  cat,pk,meal=GSEL.get(sid,('Fertiggerichte',None,True))
  add(p,'Gurkerl.at',pk,cat,p['price_eur'],f"food-connectors/gurkerl {D} (T05 sitemap-category walk, products/prices/stock API, inStock)",f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',meal=meal)

# --- BILLA T05: catalog diff (dish/brand terms beyond the T04 category regex) + detail API
BSEL={'00-242928':('TK-Fertiggericht',True),'00-242934':('TK-Fertiggericht',True),'00-242938':('TK-Fertiggericht',True),
      '00-916929':('TK-Fisch (paniert)',True),'00-372578':('TK-Snack (Rösti-Tasche)',False),'00-372579':('TK-Snack (Rösti-Tasche)',False),'00-768018':('TK-Fertiggericht (vegan)',True)}
for p in json.load(open('/tmp/h05/billa_cand.json')):
  if p['source_id'] not in BSEL: continue
  cat,meal=BSEL[p['source_id']]; e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk=TK if e.get('storage')=='frozen' else KR if e.get('storage')=='chilled' else None
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}"
  add(p,'BILLA',pk,cat,price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g) {D}','BILLA Zustellung (Linz)',meal=meal,extra=ex)

# --- SPAR T05: identical-product twins (same brand + product line per interspar URL slug + pack size), twin kcal must agree within 3 %
Bc={p['source_id']:p for p in json.load(open('/tmp/h05/billa_cand.json'))}
TW={'2020002740092':(['5960'],['00-242934'],'TK-Fertiggericht',True,'Iglo Ideenküche Zucchini Bulgur'),
    '2020003233852':(['1158'],['00-372579'],'TK-Snack (Rösti-Tasche)',False,None),
    '2020002898328':(['1142'],['00-372578'],'TK-Snack (Rösti-Tasche)',False,None),
    '2020002740078':(['5959'],['00-242938'],'TK-Fertiggericht',True,'Iglo Ideenküche Kürbis Quinoa'),
    '2020002740085':(['5958'],['00-242928'],'TK-Fertiggericht',True,'Iglo Ideenküche Broccoli Buchweizen')}
SPREJ={'2020004317117':'Zwillings-Nährwerte widersprüchlich (Gurkerl 220 vs MPreis 209 kcal bei gleicher EAN 4000405005026)',
       '2020005951907':'Zwillings-Nährwerte widersprüchlich (Gurkerl 287 vs MPreis 270 kcal bei gleicher EAN 7630294505375)'}
SP={p['source_id']:p for p in json.load(open('/tmp/h05/spar_twinsearch.json'))}
for sid,why in SPREJ.items(): rej.append(('SPAR',SP[sid]['name'],why))
for sid,(gs,bs,cat,meal,nm) in TW.items():
  p=SP[sid]
  if p['extra'].get('stock_status')!='inStock': rej.append(('SPAR',p['name'],'nicht lagernd laut SPAR-API')); continue
  if sid in spar_ids: rej.append(('SPAR',p['name'],'schon vorhanden (SPAR-Artikelnummer)')); continue
  tw=[('Gurkerl.at',G[i]['source_url'],G[i]) for i in gs]+[('BILLA',Bc[i]['source_url'],Bc[i]) for i in bs]
  tw=[t for t in tw if t[2].get('nutrition_100g',{}).get('kcal') and t[2].get('size_g') and abs(t[2]['size_g']-p['size_g'])<=0.03*p['size_g']]
  ks=[float(t[2]['nutrition_100g']['kcal']) for t in tw]
  if not tw: rej.append(('SPAR',p['name'],'kein Zwilling mit gleicher Packungsgröße')); continue
  if max(ks)-min(ks)>0.03*min(ks): rej.append(('SPAR',nm or p['name'],f'Zwillings-Nährwerte widersprüchlich {sorted(set(ks))} (Gurkerl vs BILLA)')); continue
  z=sorted(tw,key=lambda t:(not t[2].get('ean'),))[0]
  q=dict(p); q['nutrition_100g']=dict(z[2]['nutrition_100g']); q['ean']=z[2].get('ean') or next((t[2].get('ean') for t in tw if t[2].get('ean')),None)
  q['producer']=next((t[2].get('producer') for t in tw if t[2].get('producer')),None); q['origin']=None
  slug=p['source_url'].split('/')[-3]
  ex=dict(price_regular_eur=p['extra'].get('regular_price_eur'),spar_article=sid,twin_url=z[1],twin_store=z[0],twin_kcal=sorted(set(ks)),spar_slug=slug)
  if q['producer']: ex['manufacturer_source']=f"Herstellerangabe des identischen Produkts bei {next(t[0] for t in tw if t[2].get('producer'))}"
  nsrc=f"Etikett-Nährwerte je 100 g vom identischen Produkt (Marke+Produktlinie+Sorte laut interspar-URL '{slug}', Packung {z[2]['size_g']:.0f} g) bei {z[0]} ({z[1]}); {len(tw)} Zwilling(e) übereinstimmend {sorted(set(ks))}; SPAR-Index ohne Nährwerte {D}"
  add(q,'SPAR',TK,cat,p['price_eur'],f"food-connectors/spar-shop {D} (SPAR public search API search-spar.spar-ics.com, article {sid}, inStock)",nsrc,'SPAR/INTERSPAR Filialen Linz',name=nm or p['name'],meal=meal,extra=ex)
  spar_ids.add(sid)

# producer gap fill: Gurkerl composition has no Inverkehrbringer for Iglo Ideenküche / 11er Taschen -> take the label address
# published for the identical product (same brand + line + variety + pack size) in the BILLA shop's Pflichtangaben
PAIR={'5958':'00-242928','5959':'00-242938','5960':'00-242934','1158':'00-372579','1142':'00-372578'}
for r in new:
  if r['store']!='Gurkerl.at' or r.get('manufacturer'): continue
  sid=re.search(r'gurkerl\.at/(\d+)-',r['url']).group(1)
  b=Bc.get(PAIR.get(sid,''))
  if b and b.get('producer'):
    r['manufacturer']=re.sub(r'\s*\n\s*',', ',b['producer'].strip()); r['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben des identischen Produkts ({b['source_url']}) {D}"
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=[list(x) for x in rej]),open(f'hourly/added_{SLOT}.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new),'meals',sum(r['hourly_kind']=='Fertiggericht' for r in new))
for x in rej: print(' REJ',*x)
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:35],'|',r.get('ean'))
