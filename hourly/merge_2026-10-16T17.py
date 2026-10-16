# hourly T17 (2026-10-16T17): merge verified new heat-up meals (Gurkerl/MPreis search leftovers + Alfies getvoila/Rana/Radatz/
# Knödelwerkstatt/Hänsel&Gretel/Every/Ben Fatto/Freda/Dean&David) into connectors_new.json. Only source data, no invented values.
import json,re,os,collections
os.chdir('/workspace/fertig')
D='2026-10-16'; SLOT='2026-10-16T17'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (5<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
sk=lambda s:{'gurkerl.at':'gurkerl','gurkerl':'gurkerl','billa':'billa','spar':'spar','interspar':'spar','mpreis':'mpreis','alfies':'alfies'}.get(str(s or '').lower(),str(s or '').lower())
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
A=json.load(open('alfies_src.json')); A=A if isinstance(A,list) else A.get('products',[])
ALL=S+cn+A
have={(k(x['name']),sk(x.get('store'))) for x in ALL}; haveU={x.get('url') for x in ALL}
haveE={(str(x.get('ean')).lstrip('0'),sk(x.get('store'))) for x in ALL if x.get('ean')}
new,rej=[],[]
NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
def add(p,store,pk,cat,price,psrc,nsrc,delivery,kind='Fertiggericht',extra={}):
  nm=re.sub(r'\s+',' ',p['name']).strip(); n=p.get('nutrition_100g') or {}
  if not n.get('kcal') or n.get('protein') is None: rej.append((store,nm,'keine Nährwerte an der Quelle')); return
  if not consistent(n): rej.append((store,nm,f'Nährwerte inkonsistent an der Quelle {n}')); return
  g=p.get('size_g')
  if not (price and g and g>=50): rej.append((store,nm,'kein Preis/Gewicht')); return
  if g>=900: rej.append((store,nm,'Großpackung ≥900 g')); return
  if p.get('source_url') in haveU or (k(nm),sk(store)) in have or (p.get('ean') and (str(p['ean']).lstrip('0'),sk(store)) in haveE): rej.append((store,nm,'schon vorhanden')); return
  if not p.get('image_url'): rej.append((store,nm,'kein Produktfoto')); return
  man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  if man: man=re.sub(r'^(Kontakt|Hersteller|Produzent|Inverkehrbringer)\s*:\s*','',man,flags=re.I)
  e=str(p.get('ean') or '').strip(); ean=e if re.fullmatch(r'\d{8}|\d{12,14}',e) else None
  r=dict(name=nm,brand=p.get('brand') or None,store=store,price_eur=price,size_g=g,price_per_kg=round(price/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in NUTK},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=(p.get('origin') or '').strip() or None,category=cat,price_source=psrc,price_date=D,nut_source=nsrc,ean=ean,packaging=pk,packaging_hint=pk,
    is_meal=True,delivery=delivery,added_slot=SLOT,hourly_kind=kind,**extra)
  ing=(p.get('extra') or {}).get('ingredients') or p.get('ingredients')
  if ing: r['ingredients']=str(ing)[:2000]
  have.add((k(nm),sk(store))); haveU.add(p['source_url'])
  if ean: haveE.add((ean.lstrip('0'),sk(store)))
  BR={'getvoila':'getvoila','iglo':'Iglo','knödelwerkstatt ges. m.b.h':'Die Knödelwerkstatt','organic veggie food gmbh':'Soto'}
  b0=(r['brand'] or '').lower()
  if b0 in BR:
    if b0 in ('knödelwerkstatt ges. m.b.h','organic veggie food gmbh') and not r['manufacturer']: r['manufacturer']=r['brand']
    r['brand']=BR[b0]
  new.append(r)
TK='Tiefkühl (TK)'; KR='Kühlregal (Menüschale/frisch)'
V=json.load(open('/tmp/h17/verified.json'))+json.load(open('/tmp/h17/alfies_sel.json'))
SKIP={'Synear Deep-Fried Sticks':'Frittierte Teigstangen (Youtiao) – Beilage, kein Gericht',
      'Knorr Spaghetteria':'Trockenmischung (Beutel, mit Wasser/Milch zubereiten) – kein Heiß-Fertiggericht'}
seen=set()
for p in V:
  nm=p['name']; src=p['_src']
  if (src,str(p['source_id'])) in seen: continue
  seen.add((src,str(p['source_id'])))
  why=next((w for s,w in SKIP.items() if nm.startswith(s)),None)
  if why: rej.append((src,nm,why)); continue
  cat=p.get('category') or ''
  frozen=bool(re.search(r'tiefk|gefroren',cat+' '+nm,re.I))
  kind='Fertiggericht'
  if re.search(r'Leberknödel|Back-Taler',nm): kind='Heiß-Komponente (Knödel/Laibchen)'
  if src=='gurkerl':
    pk=TK if frozen else (KR if 'Kühlregal' in cat else None)
    add(p,'Gurkerl.at',pk,cat.split(' > ')[-1] or None,p['price_eur'],
        f'food-connectors/gurkerl {D} (T17: search leftovers, products/prices/stock API, inStock)',
        f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',kind=kind)
  elif src=='mpreis':
    pk=TK if frozen else None
    add(p,'MPreis',pk,cat.split(' / ')[-1] or None,p['price_eur'],
        f'food-connectors/mpreis_shop {D} (T17 search, InStock)',f'MPreis Shop (Nährwerte je 100 g) {D}',
        'MPreis Filiale / Shop (Linz-Einzugsgebiet)',kind=kind,extra={'manufacturer_source':f'MPreis Shop Produktseite {D}'} if p.get('producer') else {})
  elif src=='alfies':
    pk=TK if frozen else (KR if cat in ('Fertiggerichte','Pasta Frisch & Gefüllt') else None)
    add(p,'Alfies',pk,cat or None,p['price_eur'],
        f'food-connectors/alfies {D} (alfies.at Wien warehouse, Algolia index price incl. MwSt.)',
        f'Alfies catalogue API Nährwerttabelle je 100 g {D}',
        'Alfies Lieferung Wien (60/120 Min) + Graz (Vorbestellung) – nicht Linz',kind=kind)
if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=[list(x) for x in rej]),open(f'hourly/added_{SLOT}.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new),collections.Counter(r['hourly_kind'] for r in new))
for x in rej: print(' REJ',*x)
for r in new: print(' +',r['store'],'|',r['name'][:55],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['packaging'],'|',r['kcal_100'],r['protein_100'],'|',r.get('ean'))
