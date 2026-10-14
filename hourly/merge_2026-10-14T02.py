# hourly T02 (2026-10-14T02): merge verified MPreis + SPAR (slug-line twin nutrition) candidates into connectors_new.json
import json,re,os,collections,sys
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T02'
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

# --- MPreis T02 ---
MPSEL={'226902':'Dosengerichte','140063':'Dosengerichte','226800':'Dosengerichte','804317':'Paniert/Nuggets','667658':'TK-Fisch',
  '80362':'Paniert/Nuggets','809315':'TK-Fisch','804484':'TK-Fisch','804469':'TK-Fisch','804472':'TK-Fisch','805518':'TK-Fisch',
  '809330':'TK-Fisch','820539':'TK-Fisch','808931':'TK-Fisch'}
MPNAME={'140063':'Inzersdorfer Gefüllte Paprika 800 g','804469':'Iglo Goldschatz Käse MSC 600 g','226902':'Felix Gefüllte Paprika 800 g'}
MPREJ={'810460':'Gemüsemischung für Minestrone (nur Gemüse, keine Suppe)','813763':'Burger-Patty mit Cheddar (rohes Rindfleisch, kein Fertiggericht)',
  '810590':'Burger-Patty (Rindfleisch+Bohnenprotein, kein Fertiggericht)','32141':'kein Packungsgewicht (Stückware Feinkost)',
  '114304':'Pinsa-Boden ohne Belag, keine Nährwerte','114479':'Pinsa-Boden ohne Belag, keine Nährwerte','812196':'keine Nährwerte an der Quelle',
  '292024':'Trocken-Fertiggericht (Pulver/Nudeln, 410 kcal/100 g)'}
for f in ('hourly/cand_mpreis_2026-10-14T02.json','hourly/cand_mpreis2_2026-10-14T02.json'):
 for p in json.load(open(f)):
  sid=p['source_id']; br=p.get('brand') or ''
  full=p['name'] if (not br or p['name'].lower().startswith(br.lower())) else f"{br} {p['name']}"
  if sid in MPREJ: rej.append(('MPreis',full,MPREJ[sid])); continue
  if sid not in MPSEL: continue
  if (p.get('extra') or {}).get('availability')!='InStock': rej.append(('MPreis',full,'nicht lagernd')); continue
  c=p.get('category') or ''
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Konserve/Dose' if ('Dosen' in c or 'Konserve' in c) else None
  add(p,'MPreis',pk,MPSEL[sid],p['price_eur'],f'food-connectors/mpreis-shop {D} (product page JSON-LD offer price, {p["extra"].get("availability")})',f'MPreis Shop Produktseite, Nährwerte je 100 g {D}','MPreis Filiale Linz / MPreis Shop (AT)',name=MPNAME.get(sid,full),extra={'ingredients':(p.get('extra') or {}).get('ingredients')})

# --- SPAR T02: identical-product twin nutrition, identity from interspar URL slug (product line) ---
LINE={'2946092':'Die Ofenfrische','359740':'Steinofen','945233':'Ristorante','2020004740632':'Pietro Pizzi','4795292':'Steinofen','82679':'Ristorante',
 '3612033':'Bistro','6184773':'Ristorante','2020004650009':'La Mia Grande','2020004680037':'Ristorante','3140000':'Bistro','2020002292720':'Die Ofenfrische',
 '2020003155710':'La Mia Grande','945226':'Ristorante','6184797':'Ristorante','3198902':'Ristorante','5109487':'Bistro','2020001902002':'Ristorante',
 '2718026':'Ristorante','2948003':'Die Ofenfrische','6184766':'Ristorante','2020005391666':'Suprema','2020003154119':'La Mia Grande','3140048':'Bistro',
 '2020003736186':'La Mia Grande','2020003928321':'Green Cuisine','2020004624857':'Green Cuisine','2020005006140':'Green Cuisine',
 '8121646':None,'1937275':None,'2020005513327':'Mehlspeistraum','2020002603120':'Mehlspeistraum','372916':"G'sunden Appetit",'2020004393555':'Meister Kessel XL'}
CAT={'3612033':'Baguette (warm)','3140000':'Baguette (warm)','5109487':'Baguette (warm)','3140048':'Baguette (warm)','2020003928321':'Paniert/Nuggets',
 '2020004624857':'Paniert/Nuggets','2020005006140':'TK-Gemüselaibchen','372916':'TK-Gemüselaibchen','8121646':'Paniert/Nuggets','1937275':'Paniert/Nuggets',
 '2020005513327':'Mehlspeisen/Desserts','2020002603120':'Mehlspeisen/Desserts','2020004393555':'Suppe/Eintopf'}
SPREJ={'2438917':'Zwillings-Nährwerte widersprüchlich [251, 271]','1131505':'Zwillings-Nährwerte widersprüchlich [175, 188]',
 '7547829':'Trocken-Mehlspeismix (Pulver, 415 kcal/100 g)','7547812':'Trocken-Mehlspeismix / Zwillinge widersprüchlich [224, 429]',
 '8119759':'Zwillings-Nährwerte widersprüchlich [218, 233]','2020001236992':'Ćevapčići roh (Fleischzubereitung, kein Fertiggericht)'}
# manual twins (same brand + line + variant + pack size; checked by hand against the slug)
MANUAL={'8121646':['https://www.mpreis.at/shop/p/iglo-backhendlstreifen-kuerbiskern-809027'],
 '1937275':['https://www.mpreis.at/shop/p/iglo-huehnernuggets-30er-packung-810227','https://www.gurkerl.at/36978-iglo-huehner-nuggets-vorteilspackung-tief'],
 '2020005513327':['https://www.mpreis.at/shop/p/iglo-6-topfenknoedel-mohn-807060','https://www.gurkerl.at/36238-iglo-mohn-topfenknoedel-tiefgekuehlt'],
 '2020002603120':['https://www.mpreis.at/shop/p/iglo-nougatknoedel-8er-packung-850412','https://www.gurkerl.at/5900-iglo-8-nougatknoedel-tiefgekuehlt','https://shop.billa.at/produkte/iglo-nougatknoedel-00968082'],
 '372916':['https://www.gurkerl.at/5944-iglo-green-cuisine-4-karfiol-kaese-laibche','https://shop.billa.at/produkte/iglo-green-cuisine-karfiol-kaese-laibch'],
 '2020004393555':['https://www.gurkerl.at/9408-knorr-meisterkessel-xl-leberknoedelsuppe','https://shop.billa.at/produkte/knorr-meisterkessel-xl-leberknoedelsupp']}
ALL=S+cn
def byurl(pref): return [x for x in ALL if str(x.get('url') or '').startswith(pref) and x.get('kcal_100')]
T={str(t['spar']['source_id']):t for t in json.load(open('/tmp/h02/spar_twins.json'))}
P={str(p['source_id']):p for p in json.load(open('/tmp/h02/spar_new.json'))}
for sid in MANUAL:
  tw=[]; [tw.extend(byurl(u)) for u in MANUAL[sid]]
  T[sid]=dict(spar=P[sid],twins=tw)
for sid,t in T.items():
  p=t['spar']
  if sid in SPREJ: rej.append(('SPAR',p['name'],SPREJ[sid])); continue
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
  pk='Tiefkühl (TK)' if 'Tiefkühlung' in sc else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in sc else 'Konserve/Dose' if 'Dosensuppen' in sc else z.get('packaging')
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
