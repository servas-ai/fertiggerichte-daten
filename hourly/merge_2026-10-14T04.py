# hourly T04 (2026-10-14T04): merge verified BILLA (full public catalog listing 12 204 items + detail API) and SPAR (identical-product twin nutrition) candidates into connectors_new.json
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T04'
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
SKIP=re.compile(r'Kaspressknödel$|Leberknödel(?!.*Suppe)|Grießnockerl|Gemüse ?Pfanne(?! mit Bulgur)|Gemüse-Pilz-Pfanne|Instantnudeln|Asia Noodles|Kimchi Noodles|Korean BBQ|Bratlinge|Eierspätzle|Spätzle Knöpfle',re.I)
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


# stronger SPAR dedupe: article id anywhere in URL + brand/token-set/size twins already at SPAR
def _toks(t,brand):
  t=(t or '').lower(); t=re.sub(r'\(.*?\)',' ',t); t=re.sub(r'\d+(?:[.,]\d+)?\s*(g|kg|ml|l|stück|stk)\b',' ',t)
  t=t.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
  bw=set(re.findall(r'[a-z]+',(brand or '').lower().replace('ä','ae').replace('ö','oe').replace('ü','ue')))|{'dr','oetker'}
  return frozenset(w for w in re.findall(r'[a-z]+',t) if len(w)>1 and w not in bw and w not in {'mit','und','in','der','die','das','im','la','pizza','stueck','stk','portionen','msc','tiefgekuehlt','er','x'})
spar_ids={m.group(1) for x in S+cn if 'spar' in str(x.get('url') or '') for m in [re.search(r'/p/(\d+)',x.get('url') or '')] if m}
spar_tok=[(nb_,_toks(x['name'],x.get('brand')),float(x.get('size_g') or 0)) for x in S+cn if sk(x.get('store'))=='spar' for nb_ in [re.sub(r'[^a-z0-9]','',(x.get('brand') or '').lower())]]

# --- BILLA T04 (full catalog listing diff + detail API)
D_=D
BSEL={'00-755493':'Tiefkühlpizza','00-578649':'TK-Mehlspeise'}
BREJ={'00-737146':'keine Nährwerte an der Quelle (Aida Apfelstrudel)','00-892041':'keine Packungsgröße an der Quelle (Menüschale; API weight 0.5 = Versandgewicht)','00-892049':'keine Packungsgröße an der Quelle (Menüschale; API weight 0.5 = Versandgewicht)'}
for p in json.load(open('hourly/cand_b1_2026-10-14T04.json')):
  if p['_src']=='mpreis': rej.append(('MPreis',p['name'],'Trockensuppe (370 kcal/100 g, Salz 12 g) – kein Heiß-Fertiggericht')); continue
  if p['source_id'] in BREJ: rej.append(('BILLA',p['name'],BREJ[p['source_id']])); continue
  if p['source_id'] not in BSEL: continue
  e=p['extra']; std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  pk='Tiefkühl (TK)' if e.get('storage')=='frozen' else 'Kühlregal (Menüschale/frisch)' if e.get('storage')=='chilled' else None
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f"BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}"
  add(p,'BILLA',pk,BSEL[p['source_id']],price,f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",f'BILLA Online-Shop API (Nährwerte je 100 g, unzubereitet) {D}','BILLA Zustellung (Linz)',extra=ex)

# --- SPAR T04: identical-product twin nutrition (manual twins checked by hand: same brand + line + variant + pack size)
LINE={'5495429':'Genießer Pfanne','2020006153355':'Ristorante','2020005802704':None,'2020005803015':None}
CAT={'5495429':'TK-Fertiggericht','2020005802704':'Suppe/Eintopf','2020005803015':'Suppe/Eintopf'}
TWINPK={'2020005802704','2020005803015'}  # Frank Soup is chilled (Gurkerl 'gekühlt'), SPAR files it under Dosensuppen -> take twin packaging
SPREJ={'2020005802759':'Zwillings-Nährwerte widersprüchlich (Gurkerl 76 vs MPreis 59 kcal bei gleicher EAN 4260434440803)',
 '2020005802889':'Zwillings-Nährwerte widersprüchlich (Gurkerl 51 vs MPreis 48 kcal) und Sortenname abweichend (Pomodoro Pronto vs mit Meersalz)',
 '2020005802926':'kein Zwilling mit Nährwerten (Rote-Linsencremesuppe)','2020000674139':'Zwillings-Nährwerte widersprüchlich [256, 289]',
 '1131505':'Zwillings-Nährwerte widersprüchlich [175, 188]','2438917':'Zwillings-Nährwerte widersprüchlich [251, 271]',
 '7547829':'Trockenmischung (Knorr Sweety Kaiserschmarrn, 415 kcal/100 g Pulver)','7547812':'Trockenmischung (Knorr Sweety Kaiserschmarrn)','2020004655790':'Trockensuppe (Knorr Disney Packerlsuppe)'}
MANUAL={'5495429':['https://shop.billa.at/produkte/iglo-geniesser-pfanne-stroganoff-00438602'],
 '2020006153355':['https://www.mpreis.at/shop/p/dr-oetker-ristorante-pepperoni-salami-804996'],
 '2020005802704':['https://www.gurkerl.at/13777-frank-soup-bio-brokkolisuppe-mit-cashew-dattel-gekuehlt','https://www.mpreis.at/shop/p/frank-juice-bio-brokkoli-suppe-367103'],
 '2020005803015':['https://www.gurkerl.at/13780-frank-soup-bio-karottensuppe-mit-ingwer-gekuehlt']}
P={str(p['source_id']):p for p in json.load(open('/tmp/h04/spar_new.json'))}
T={}
ALL=S+cn
def byurl(pref): return [x for x in ALL if str(x.get('url') or '').startswith(pref) and x.get('kcal_100')]
for sid in MANUAL:
  tw=[]; [tw.extend(byurl(u)) for u in MANUAL[sid]]
  T[sid]=dict(spar=P[sid],twins=tw)
for sid in SPREJ:
  if sid in P: rej.append(('SPAR',P[sid]['name'],SPREJ[sid]))
for sid,t in T.items():
  p=t['spar']
  if sid not in LINE: continue
  if (p.get('extra') or {}).get('stock_status')!='inStock': rej.append(('SPAR',p['name'],'nicht lagernd laut SPAR-API')); continue
  if sid in spar_ids: rej.append(('SPAR',p['name'],'schon vorhanden (SPAR-Artikelnummer)')); continue
  tw=[x for x in t['twins'] if x.get('kcal_100') and x.get('size_g') and abs(float(x['size_g'])-p['size_g'])<=0.03*p['size_g']]
  if not tw: rej.append(('SPAR',p['name'],'kein Zwilling mit gleicher Packungsgröße')); continue
  ks=[float(x['kcal_100']) for x in tw]
  if max(ks)-min(ks)>0.03*min(ks): rej.append(('SPAR',p['name'],f'Zwillings-Nährwerte widersprüchlich {sorted(set(ks))}')); continue
  tw.sort(key=lambda x:(not x.get('ean'),not x.get('manufacturer')))
  z=tw[0]
  nm=p['name']; L=LINE[sid]; br=p.get('brand') or ''
  if L and L.lower() not in nm.lower():
    nm=(br+' '+L+' '+nm[len(br):].strip()) if nm.startswith(br) else L+' '+nm
  nb_=re.sub(r'[^a-z0-9]','',br.lower()); tk=_toks(nm,br)
  if any(b==nb_ and tt==tk and g and abs(g-p['size_g'])<=0.03*p['size_g'] for b,tt,g in spar_tok): rej.append(('SPAR',nm,'schon vorhanden (gleiches Produkt bei SPAR)')); continue
  n={k_:z.get(f'{k_}_100') for k_ in NUTK}
  q=dict(p); q['nutrition_100g']={k_:v for k_,v in n.items() if v is not None}; q['ean']=z.get('ean'); q['producer']=z.get('manufacturer'); q['producer_id']=z.get('producer_id'); q['origin']=z.get('origin')
  ex=dict(price_regular_eur=(p.get('extra') or {}).get('regular_price_eur'),spar_article=p['source_id'],twin_url=z.get('url'),twin_store=z.get('store'),twin_kcal=sorted(set(ks)),spar_slug=(p.get('source_url') or '').split('/')[-3])
  if (p.get('extra') or {}).get('on_promotion'): ex['offer_text']='SPAR Aktion (API is-on-promotion)'
  nsrc=f"Etikett-Nährwerte je 100 g vom identischen Produkt (Marke+Produktlinie+Sorte laut interspar-URL '{ex['spar_slug']}', Packung {z.get('size_g')} g) bei {z.get('store')} ({z.get('url')}; dortige Quelle: {z.get('nut_source') or 'Shopseite'}); {len(tw)} Zwilling(e) übereinstimmend; SPAR-Index ohne Nährwerte {D}"
  if z.get('manufacturer'): ex['manufacturer_source']=f"Herstellerangabe des identischen Produkts bei {z.get('store')} ({z.get('url')})"
  sc=p.get('category') or ''
  pk=z.get('packaging') if sid in TWINPK else 'Tiefkühl (TK)' if 'Tiefkühlung' in sc else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in sc else 'Konserve/Dose' if 'Dosensuppen' in sc else z.get('packaging')
  cat=CAT.get(sid) or ('Tiefkühlpizza' if 'Pizza' in sc else z.get('category') or 'Fertiggerichte')
  add(q,'SPAR',pk,cat,p['price_eur'],f"food-connectors/spar-shop {D} (SPAR public search API search-spar.spar-ics.com, article {p['source_id']}, {p['extra'].get('stock_status')})",nsrc,'SPAR/INTERSPAR Filialen Linz',name=nm,extra=ex)
  spar_ids.add(sid)

if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  AF=f'hourly/added_{SLOT}.json'
  json.dump(dict(slot=SLOT,added=new,rejected=[list(x) for x in rej]),open(AF,'w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new))
for x in rej: print(' REJ',*x)
for r in new: print(' +',r['store'],'|',r['name'],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:35],'|',r.get('ean'))
