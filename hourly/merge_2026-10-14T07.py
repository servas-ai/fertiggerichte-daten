# hourly T07 (2026-10-14T07): merge verified BILLA/Gurkerl/MPreis heat-up products (sous-vide pulled meats,
# planted. heat-up components, baguettes, chili con carne, sides) into connectors_new.json
import json,re,os,collections
os.chdir('/workspace/fertig')
D='2026-10-14'; SLOT='2026-10-14T07'
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (5<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  return abs(9*f+4*p+4*c+2*(n.get('fiber') or 0)-k)<=max(25,0.25*k)
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
cn=json.load(open('connectors_new.json')); S=json.load(open('scored.json'))
sk=lambda s:{'gurkerl.at':'gurkerl','gurkerl':'gurkerl','billa':'billa','spar':'spar','interspar':'spar','mpreis':'mpreis'}.get(str(s or '').lower(),str(s or '').lower())
have={(k(x['name']),sk(x.get('store'))) for x in S+cn}; haveU={x.get('url') for x in S+cn}
haveE={(str(x.get('ean')).lstrip('0'),sk(x.get('store'))) for x in S+cn if x.get('ean')}
new,rej=[],[]
NUTK=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
def add(p,store,pk,cat,price,psrc,nsrc,delivery,name=None,meal=True,extra={},kind=None):
  nm=re.sub(r'\s+',' ',name or p['name']).strip(); n=p.get('nutrition_100g') or {}
  if not n.get('kcal') or n.get('protein') is None: rej.append((store,nm,'keine Nährwerte an der Quelle')); return
  if not consistent(n): rej.append((store,nm,f'Nährwerte inkonsistent/unplausibel an der Quelle {n}')); return
  if not (price and p.get('size_g') and p['size_g']>=50): rej.append((store,nm,'kein Preis/Gewicht')); return
  if p.get('size_g') and p['size_g']>=900: rej.append((store,nm,'Catering-/Großpackung ≥900 g')); return
  if p['source_url'] in haveU or (k(nm),sk(store)) in have or (p.get('ean') and (str(p['ean']).lstrip('0'),sk(store)) in haveE): rej.append((store,nm,'schon vorhanden')); return
  if not p.get('image_url'): rej.append((store,nm,'kein Produktfoto')); return
  g=p['size_g']; man=re.sub(r'\s*\n\s*',', ',(p.get('producer') or '').strip()).rstrip('.') or None
  if man: man=re.sub(r'^(Kontakt|Hersteller|Produzent|Inverkehrbringer)\s*:\s*','',man,flags=re.I)
  r=dict(name=nm,brand=p.get('brand') or None,store=store,price_eur=price,size_g=g,price_per_kg=round(price/g*1000,2),
    url=p['source_url'],image_url=p.get('image_url'),**{f'{x}_100':(None if n.get(x) is None else float(n[x])) for x in NUTK},
    protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=man,producer_id=p.get('producer_id'),
    origin=(p.get('origin') or '').strip() or None,category=cat,price_source=psrc,price_date=D,nut_source=nsrc,ean=p.get('ean'),packaging=pk,packaging_hint=pk,
    is_meal=True,delivery=delivery,added_slot=SLOT,hourly_kind=kind or ('Fertiggericht' if meal else 'Heiß-Komponente (sous-vide/paniert)'),**extra)
  if (p.get('extra') or {}).get('ingredients'): r['ingredients']=p['extra']['ingredients'][:2000]
  have.add((k(nm),sk(store))); haveU.add(p['source_url'])
  if p.get('ean'): haveE.add((str(p['ean']).lstrip('0'),sk(store)))
  new.append(r)

SV='Sous-vide (vakuum)'; TK='Tiefkühl (TK)'; KR='Kühlregal (Menüschale/frisch)'; DO='Dose/Konserve'
# --- Gurkerl ---
G=json.load(open('/tmp/h07/g_ready.json'))
# reject identical-nutrition Nemetz grill cuts (Bauch/Schopf/Karree all 220/17/0.4/15)
GREJ={
  '40716':'Nährwerte an der Quelle identisch mit Grill Schopf/Karreefilet (220 kcal / 17 g Fett) – nicht übernommen',
  '40717':'Nährwerte an der Quelle identisch mit Grill Bauch/Karreefilet (220 kcal / 17 g Fett) – nicht übernommen',
  '40718':'Nährwerte an der Quelle identisch mit Grill Bauch/Schopf (220 kcal / 17 g Fett) – nicht übernommen',
  '23882':'nicht lagernd','40211':'nicht lagernd','49204':'nicht lagernd','9600':'nicht lagernd',
}
GSEL={
  '3650':('Fleisch sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
  '40714':('Fleisch sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
  '21886':('Geflügel sous-vide vorgegart',SV,True,'Fertiggericht'),
  '40715':('Geflügel sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
  '40214':('Fleischalternative (Steak)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '45805':('Fleischalternative (Würfel)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '45806':('Fleischalternative (Würfel)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '40209':('Fleischalternative (Kebab)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '40210':('Fleischalternative (pulled)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '48433':('TK-Fisch (Nuggets)',TK,False,'Heiß-Komponente (paniert/Laibchen)'),
  '30440':('TK-Baguette (überbacken)',TK,True,'Fertiggericht'),
  '30441':('TK-Baguette (überbacken)',TK,True,'Fertiggericht'),
  '41316':('Beilage (Nockerl)',KR,False,'Heiß-Komponente (Beilage)'),
  '45608':('Geflügelschnitzel (paniert)',KR,False,'Heiß-Komponente (paniert/Laibchen)'),
}
for sid,why in GREJ.items():
  if sid in G: rej.append(('Gurkerl.at',G[sid].get('name',sid),why))
for sid,(cat,pk,meal,kind) in GSEL.items():
  p=G[sid]
  if not (p.get('extra') or {}).get('in_stock'): rej.append(('Gurkerl.at',p['name'],'nicht lagernd')); continue
  q=dict(p)
  if q.get('ean'):
    e=str(q['ean']).strip()
    q['ean']=e if re.fullmatch(r'\d{8}|\d{12,14}',e) else None
  add(q,'Gurkerl.at',pk,cat,p['price_eur'],
      f'food-connectors/gurkerl {D} (T07: products/prices/stock API, inStock; search leftovers)',
      f'Gurkerl.at API (composition) {D}','Lieferung nach Linz (Gurkerl.at)',meal=meal,kind=kind)

# --- BILLA ---
B={p['source_id']:p for p in json.load(open('/tmp/h07/billa_cand.json'))}
BSEL={
  '00-756535':('Fleisch sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
  '00-730177':('Fleisch sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
  '00-894631':('Fleisch sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
  '00-868682':('TK-Snack (Mozzarella Sticks)',TK,False,'Heiß-Komponente (paniert/Laibchen)'),
  '00-889480':('Fleischalternative (Steak)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '00-745502':('Fleischalternative (Kebab)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '00-745511':('Fleischalternative (Chicken)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '00-721752':('Geflügel sous-vide vorgegart',SV,False,'Heiß-Komponente (sous-vide vorgegart)'),
}
for sid,(cat,pk,meal,kind) in BSEL.items():
  p=B[sid]; e=p.get('extra') or {}
  std=e.get('price_standard_eur'); promo=e.get('in_promotion') and std
  price=std if promo else p['price_eur']
  ex={'price_promo_eur':p['price_eur'],'promotion_text':e.get('promotion_text')} if promo else {}
  if p.get('producer'): ex['manufacturer_source']=f'BILLA Online-Shop Pflichtangaben (manufacturersAddress) {D}'
  # normalize brand for DG wholesale-looking SKU
  name=p['name']
  if sid=='00-894631': name='Pulled Chicken sous vide 500 g'
  add(p,'BILLA',pk,cat,price,
      f"food-connectors/billa {D} (product-discovery API, {'Normalpreis; Aktion separat' if promo else 'regulärer Preis'})",
      f'BILLA Online-Shop API (Nährwerte je 100 g) {D}','BILLA Zustellung (Linz)',name=name,meal=meal,extra=ex,kind=kind)

# --- MPreis ---
M={str(p['source_id']):p for p in json.load(open('/tmp/h07/mpreis_cand.json'))}
MSEL={
  '227512':('Chili con Carne (Dose)',DO,True,'Fertiggericht'),
  '611578':('Fleischalternative (Bratwurst)',KR,False,'Heiß-Komponente (Fleischalternative)'),
  '611186':('Beilage (Gnocchi)',KR,False,'Heiß-Komponente (Beilage)'),
}
for sid,(cat,pk,meal,kind) in MSEL.items():
  p=M[sid]
  avail=(p.get('extra') or {}).get('availability') or ''
  if avail and avail.lower() not in ('instock','in_stock','available'):
    rej.append(('MPreis',p['name'],f'nicht lagernd ({avail})')); continue
  ex={}
  if p.get('producer'): ex['manufacturer_source']=f'MPreis Shop Produktseite {D}'
  add(p,'MPreis',pk,cat,p['price_eur'],
      f'food-connectors/mpreis_shop {D} (T07 sitemap meal-gap)',
      f'MPreis Shop (Nährwerte je 100 g) {D}','MPreis Filiale / Shop (Linz-Einzugsgebiet)',meal=meal,extra=ex,kind=kind)

if not os.environ.get('DRY'):
  json.dump(cn+new,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
  json.dump(dict(slot=SLOT,added=new,rejected=[list(x) for x in rej]),open(f'hourly/added_{SLOT}.json','w'),ensure_ascii=False,indent=1)
print('added',len(new),collections.Counter(r['store'] for r in new),collections.Counter(r['hourly_kind'] for r in new))
for x in rej: print(' REJ',*x)
for r in new: print(' +',r['store'],'|',r['name'][:55],'|',r['brand'],'|',r['price_eur'],r['size_g'],'|',r['category'],'|',r['kcal_100'],r['protein_100'],'|',(r.get('manufacturer') or '')[:30],'|',r.get('ean'))
