# hourly T06 (2026-10-14T06): merge verified Gurkerl items left over from the T05 sitemap-category walk (fresh filled pasta, sous-vide
# pre-cooked meat, soup inserts, Knödel/Püree sides, vegan Cevapcici/Köttbullar, wrap, warm dessert) into connectors_new.json
import json,re,os,collections
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T06'
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
def add(p,store,pk,cat,price,psrc,nsrc,delivery,name=None,meal=True,extra={},kind=None):
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
    is_meal=True,delivery=delivery,added_slot=SLOT,hourly_kind=kind or ('Fertiggericht' if meal else 'Heiß-Komponente (paniert/Laibchen)'),**extra)
  if (p.get('extra') or {}).get('ingredients'): r['ingredients']=p['extra']['ingredients'][:2000]
  have.add((k(nm),sk(store))); haveU.add(p['source_url'])
  if p.get('ean'): haveE.add((str(p['ean']).lstrip('0'),sk(store)))
  new.append(r)


TK='Tiefkühl (TK)'; KR='Kühlregal (Menüschale/frisch)'; SV='Sous-vide (vakuum)'
FP=('Frische Pasta (gefüllt)',KR,False,'Heiß-Komponente (frische gefüllte Pasta)')
SE=('Suppeneinlage',KR,False,'Heiß-Komponente (Suppeneinlage)')
SVK=('Fleisch sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)')
BL=('Beilage (Knödel/Püree)',KR,False,'Heiß-Komponente (Beilage)')
FA=('Fleischalternative (Bällchen/Cevapcici)',KR,False,'Heiß-Komponente (Fleischalternative)')
GSEL={'6076':('TK-Fertiggericht',TK,True,'Fertiggericht'),'14035':FP,'29852':('Wrap',KR,True,'Fertiggericht'),'25856':('Dessert (warm, Lavakuchen)',KR,True,'Fertiggericht (Nachspeise)'),
 '13112':SVK,'13107':SVK,'36121':SVK,'43980':SVK,
 **{i:FP for i in '35820 1590 1592 1591 1596 1597 32681 32675 32669 32674 32682 32679 47579 39172 39171 39173 25565 46107 10705 47993 47994 47992 47991'.split()},
 **{i:SE for i in '41319 41318 11755 12968'.split()},'5950':('Suppeneinlage',TK,False,'Heiß-Komponente (Suppeneinlage)'),
 **{i:BL for i in '42675 42080 42083 40837 40842'.split()},**{i:FA for i in '26411 26412 10853'.split()}}
GREJ={'46435':'frittierte Teigstangen (Youtiao) – Snack/Beilage, kein Fertiggericht',
 **{i:'kaltes Sandwich (verzehrfertig, kein Heiß-Gericht)' for i in '6615 6618 6617 6616 6614 43196 43195'.split()},
 '21157':'Zutatenliste an der Quelle nennt nur Gewürze (kein Fleischanteil) und Nährwerte identisch mit Entenkeule – nicht übernommen',
 '21149':'Zutatenliste an der Quelle nennt nur Gewürze, EAN 2741376 (7-stellig, kein GTIN) – nicht übernommen',
 '40005':'Porchetta im Ganzen 2,32 kg (Catering-/Bratenstück, kein Portionsprodukt) – nicht übernommen',
 '46402':'keine Nährwerte an der Quelle','28394':'keine Nährwerte an der Quelle','28393':'keine Nährwerte an der Quelle',
 '5490':'Trockenware (LAND-LEBEN Frittaten 549 kcal/100 g, ungekühlt) – keine Heiß-Komponente wie die gekühlten Frittaten',
 '49066':'TK-Mini-Bagels zum Auftauen (kalt serviert), kein Heiß-Gericht'}
# producer gap fill from the public product page / brand Impressum (source cited per row)
PROD={'12968':('Herbert Lugitsch u. Söhne Ges.mbH','Gurkerl.at Produktseite „Produzent“ (gurkerl.at/12968-steirerhuhn-gourmet-huehnerleberknoedel) 2026-10-14'),
 '40842':('Agrofresh GmbH, Jagenbach 135, 3923 Jagenbach','Impressum gabelkönig.at (Markeninhaber, UID ATU65057733) 2026-10-14'),
 '25856':('Interfood Lebensmittelgroßhandel Ges.m.b.H., Innsbruckerstrasse 77, 6060 Hall in Tirol','Gurkerl.at composition „Kontaktdaten“ 2026-10-14')}
G={p['source_id']:p for p in json.load(open('/tmp/h06/g_cand.json'))+json.load(open('/tmp/h06/g_cand2.json'))}
for sid,p in G.items():
  if sid in GREJ: rej.append(('Gurkerl.at',p['name'],GREJ[sid])); continue
  if sid not in GSEL: continue
  if not p['extra'].get('in_stock'): rej.append(('Gurkerl.at',p['name'],'nicht lagernd')); continue
  cat,pk,meal,kind=GSEL[sid]; q=dict(p)
  if q.get('ean') and not re.fullmatch(r'\d{8}|\d{12,14}',str(q['ean']).strip()): q['ean']=None
  elif q.get('ean'): q['ean']=str(q['ean']).strip()
  ex={}
  if sid in PROD and not q.get('producer'): q['producer'],ex['manufacturer_source']=PROD[sid]
  add(q,'Gurkerl.at',pk,cat,p['price_eur'],f"food-connectors/gurkerl {D} (T06: products/prices/stock API, inStock; ids from T05 sitemap-category walk)",f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',meal=meal,extra=ex,kind=kind)
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=[list(x) for x in rej]),open(f'hourly/added_{SLOT}.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['hourly_kind'] for r in new))
for x in rej: print(' REJ',*x)
for r in new: print(' +',r['name'][:55],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:30],'|',r.get('ean'))
