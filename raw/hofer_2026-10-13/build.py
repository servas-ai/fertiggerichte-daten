import json,re,csv,sys,collections,unicodedata
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.schema import looks_like_ready_meal
RM=re.compile(r'lasagne|gefüllte gnocchi|nuggets|vorgegart|pulled|hot dog|sandwich(?!toast)|wrap\b|bowl|sushi|suppe(?!n?brühe|ngrün|nnudel)|eintopf|gulasch(?!fleisch)|risotto|pizza(?!käse|teig|mehl|sauce)|pizzaweckerl|pizzaschnecke|backhendlteller|strudel|knödel|kaiserschmarrn|curry(?! ?-?sauce|pulver)|chili con|salat(?!-/|gurke|herz|kopf|mix\b|sauce|dressing|schüssel|besteck)|panini|burger(?!scheiben|brötchen| bun|sauce)|fertiggericht|menü|ravioli|tortellini|schupfnudel|kasnudel|leberkäse|cordon|cevapcici.*(gegart|gegrillt)|kebab|dürüm|falafel|frühlingsrolle|quiche|focaccia|toast(?!brot|schinken| vegan|$)',re.I)
NOTRM=re.compile(r'gewürz|mühle|bratpfanne|teller,|sauce,|grillzeiten|aufschnitt|käse$|brötchen|bun\b|roll\b|natur|roh|teig',re.I)
def seg(name,cats):
  c=' '.join(cats)
  if re.search(r'sandwichtoast|toastschinken',name,re.I) or 'Käse' in c: return 'grocery'
  if 'Fleisch' in c and not re.search(r'vorgegart|pulled|sous vide|backhendlteller|nuggets|gegart',name,re.I): return 'grocery'
  return 'ready_meal' if RM.search(name) and not NOTRM.search(name) else 'grocery'
def grams(sz):
  m=re.match(r'\s*([\d.,]+)\s*(kg|g|l|ml)\b',sz or '',re.I)
  if not m: return None
  v=float(m.group(1).replace(',','.'));u=m.group(2).lower()
  return v*1000 if u in('kg','l') else v
rows={}
for l in open('products.jsonl'):
  x=json.loads(l)
  if not x.get('p'): continue
  p=x['p'];sku=p['sku']
  pr=(p.get('price') or {});price=pr.get('amountRelevant');price=price/100 if price else None
  cats=[c['name'] for c in p.get('categories') or []] or x.get('breadcrumb') or []
  img=(p.get('assets') or [{}])[0].get('url','')
  img=img.replace('{width}','600').replace('{slug}',re.sub(r'\W+','-',p['name'])) if img else None
  g=grams(p.get('sellingSize'))
  rows[sku]=dict(id=sku,name=p['name'],brand=p.get('brandName'),category_path=' > '.join(cats),category=cats[0] if cats else None,subcategory=cats[-1] if len(cats)>1 else None,
    segment=seg(p['name'],cats),price_eur=price,size=p.get('sellingSize'),size_g=g,
    price_per_kg=round(price/g*1000,2) if price and g else None,price_comparison=pr.get('comparisonDisplay'),
    ingredients=p.get('ingredients') or None,allergens=[a.get('label') if isinstance(a,dict) else a for a in p.get('allergens') or []],
    claims=[c.get('value') for c in p.get('nutritionalClaims') or []],storage=p.get('storageInstructions'),
    image_url=img,url=x['url'],ean=None,kcal_100g=None,protein_100g=None,fat_100g=None,satfat_100g=None,carbs_100g=None,sugar_100g=None,salt_100g=None,fiber_100g=None,
    nutriscore=None,nova=None,nutrition_source=None,source='hofer.at product page (__NUXT_DATA__ + JSON-LD), 2026-10-13')
json.dump(list(rows.values()),open('rows.json','w'),ensure_ascii=False)
c=collections.Counter(r['segment'] for r in rows.values());print(len(rows),c)
R=list(rows.values())
def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',(s or '').lower()).encode('ascii','ignore').decode()).strip()
# write outputs
rm=[r for r in R if r['segment']=='ready_meal'];gr=[r for r in R if r['segment']=='grocery']
meta=dict(generated='2026-10-13',source='hofer.at sitemap_products.xml + category pages (robots.txt respected: no ?q= search), >=1.1 s/host shared lock',count_total=len(R),count_ready_meal=len(rm),count_grocery=len(gr))
json.dump(dict(meta=meta,products=rm),open('/workspace/fertig/hofer_full_2026-10-13.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(meta=meta,products=gr),open('/workspace/fertig/hofer_grocery_2026-10-13.json','w'),ensure_ascii=False,indent=1)
keys=list(R[0].keys()) if R else []
for fn,L in (('hofer_full_2026-10-13.csv',rm),('hofer_grocery_2026-10-13.csv',gr)):
  w=csv.DictWriter(open('/workspace/fertig/'+fn,'w',newline=''),fieldnames=keys);w.writeheader()
  for r in L: w.writerow({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v) for k,v in r.items()})
fill=json.load(open('/workspace/fertig/hofer_fill_2026-10-13.json')) if __import__('os').path.exists('/workspace/fertig/hofer_fill_2026-10-13.json') else []
app=json.load(open('/workspace/fertig-app/public/data.json'))['rows'];h=[r for r in app if r['store']=='Hofer']
# top30 (ready meals only: app Hofer meal rows + hofer.at ready_meal segment)
A=json.load(open('/workspace/fertig-app/public/data.json'))['rows'];HM=[r for r in A if r['store']=='Hofer' and r.get('segment') in (None,'ready_meal','meal') and not r.get('nonfood')]
B=json.load(open('/tmp/data_before_hofer.json'))['rows'] if __import__('os').path.exists('/tmp/data_before_hofer.json') else []
HB=[r for r in B if r['store']=='Hofer']
def v(r):
  if r.get('price') and r.get('protpack') and r.get('score') is not None: return r['protpack']/r['price']*(0.5+r['score']/200),'P'
  if r.get('price') and r.get('kcalpack') and r.get('score') is not None: return r['kcalpack']/r['price']/10*(0.5+r['score']/200),'K'
  return None,None
L=['# Hofer ready meals: value-for-money Top 30 per category (2026-10-13)','',
 f"Ready meals only (grocery excluded, see hofer_grocery_2026-10-13.json). hofer.at crawl: {len(R)} products in sitemap/categories, of which {len(rm)} classified ready_meal, {len(gr)} grocery. App Hofer rows before → after: {len(HB)} → {len([r for r in A if r['store']=='Hofer'])}.",'',
 '## Formula','- value = protein g per pack ÷ price € × (0.5 + health_score/200)  → health score 0 halves, 100 keeps full value.',
 '- fallback when protein per pack is missing: kcal per pack ÷ price € ÷ 10 × same factor (marked K).','- rows without price or score are not ranked (listed under "Not rankable").',
 '- prices from heisse-preise.io older than 12 months are marked (alt).','',
 '## Completeness of Hofer rows in the app (before → after)','']
for k in ['price','size','kcal','score','img','ns']:
  L.append(f"- {k}: {sum(r.get(k) is not None for r in HB)} → {sum(r.get(k) is not None for r in A if r['store']=='Hofer')}")
cmp=lambda L_:sum(1 for r in L_ if r.get('price') is not None and r.get('score') is not None and r.get('size') is not None)
L.append(f"- price+score+size complete: {cmp(HB)} → {cmp([r for r in A if r['store']=='Hofer'])}")
L+=['','## App Hofer rows per category (pack) before → after','']
cb=collections.Counter(r.get('pack') for r in HB);ca=collections.Counter(r.get('pack') for r in A if r['store']=='Hofer')
for k in sorted(set(cb)|set(ca),key=str): L.append(f"- {k}: {cb.get(k,0)} → {ca.get(k,0)}")
L+=['','## App Hofer rows per brand (top 30) before → after','']
bb=collections.Counter(r.get('brand') for r in HB);ba=collections.Counter(r.get('brand') for r in A if r['store']=='Hofer')
for k,n in ba.most_common(30): L.append(f"- {k}: {bb.get(k,0)} → {n}")
for cat in sorted({r.get('pack') for r in HM},key=str):
  xs=[(v(r),r) for r in HM if r.get('pack')==cat and v(r)[0]];xs.sort(key=lambda t:-t[0][0])
  if not xs: continue
  L+=['',f'## {cat}','','| # | Product | Brand | € | g | score | value |','|---|---|---|---|---|---|---|']
  for i,((val_,k),r) in enumerate(xs[:30],1): L.append(f"| {i} | {r['name']} | {r['brand']} | {r['price']}{' (alt)' if 'Altpreis' in str(r.get('psrc')) or 'heisse' in str(r.get('psrc')) and str(r.get('price_date') or '')<'2025-10-13' else ''} | {r.get('size')} | {r.get('score')} | {val_:.1f}{k} |")
L+=['',f"Not rankable (missing price or score): {sum(1 for r in HM if v(r)[0] is None)} of {len(HM)}",'',
 '## hofer.at crawl: products per category > subcategory (all segments)','']
for k,n in sorted(collections.Counter((r['category_path'] or '(none)',r['segment']) for r in R).items()): L.append(f"- {k[0]} [{k[1]}]: {n}")
L+=['','## hofer.at crawl: products per brand (top 40)','']+[f"- {b}: {n}" for b,n in collections.Counter(r['brand'] for r in R).most_common(40)]
import os;os.makedirs('/workspace/fertig/analysis',exist_ok=True);open('/workspace/fertig/analysis/hofer_top30.md','w').write('\n'.join(L)+'\n')
print('HM',len(HM))
