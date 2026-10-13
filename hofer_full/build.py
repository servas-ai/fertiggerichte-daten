import json,re,csv,sys,collections,unicodedata
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.schema import looks_like_ready_meal
EXTRA=re.compile(r'salat(?!gurke|kopf|herz|mix\b)|bowl|wrap|sandwich|panini|burger|hot dog|toast|suppe|eintopf|gulasch|lasagne|pizza|nudeln? mit|risotto|curry|knödel|strudel|schnitzel|nuggets|sushi|fertig|instant|cup\b|snack ?box|backbox',re.I)
NOT=re.compile(r'gewürz|dressing|essig|öl\b|tee\b|saft|wasser|katzen|hunde',re.I)
def seg(name,cats):
  s=name+' '+' '.join(cats)
  return 'ready_meal' if (looks_like_ready_meal(name,' '.join(cats)) or EXTRA.search(name)) and not NOT.search(name) else 'grocery'
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
# top30
def val(r):
  if r['protein_100g'] and r['price_eur'] and r['size_g']: return ('protein',r['protein_100g']*r['size_g']/100/r['price_eur'])
  if r['price_per_kg']: return ('g_per_eur',1000/r['price_per_kg'])
  return (None,None)
L=['# Hofer ready meals: value-for-money Top 30 per category (2026-10-13)','',
 f"Source: hofer.at, {len(R)} products crawled ({len(rm)} ready_meal, {len(gr)} grocery). App dataset before: {len(h)} Hofer rows; matched/fillable from hofer.at: {len(fill)} (of which {sum(not f['had_price'] for f in fill)} were missing a price).",'',
 '## Formula','value = protein grams per € (protein_100g × size_g/100 ÷ price) × (1 − 0.1 × max(0, salt_100g − 1.25)/0.25 capped at 0.5). hofer.at publishes no nutrition and no EAN, so where OFF nutrition is missing the fallback is grams per € (1000 ÷ €/kg), marked `g/€`. Grocery items are excluded.','',
 '## Counts per category > subcategory (all segments)','']
for k,v in sorted(collections.Counter((r['category_path'] or '?',r['segment']) for r in R).items()): L.append(f"- {k[0]} [{k[1]}]: {v}")
L+=['','## Counts per brand (top 40)','']+[f"- {b}: {n}" for b,n in collections.Counter(r['brand'] for r in R).most_common(40)]
for cat in sorted({r['category'] for r in rm if r['category']}):
  xs=[(val(r),r) for r in rm if r['category']==cat and val(r)[1]];xs.sort(key=lambda t:-t[0][1])
  L+=['',f'## {cat}','','| # | Product | Brand | € | Size | €/kg | value |','|---|---|---|---|---|---|---|']
  for i,((kind,v),r) in enumerate(xs[:30],1): L.append(f"| {i} | [{r['name']}]({r['url']}) | {r['brand']} | {r['price_eur']} | {r['size']} | {r['price_per_kg']} | {v:.1f} {'g prot/€' if kind=='protein' else 'g/€'} |")
import os;os.makedirs('/workspace/fertig/analysis',exist_ok=True);open('/workspace/fertig/analysis/hofer_top30.md','w').write('\n'.join(L)+'\n')
print('fill',len(fill),'rm',len(rm))
