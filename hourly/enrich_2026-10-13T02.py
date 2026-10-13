import sys,json,re,concurrent.futures as cf,urllib.request
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.http import get
from food_connectors.adapters.gurkerl import parse_composition
mm=json.load(open('/workspace/fertig/more_meals.json')); new=json.load(open('added_2026-10-13T02.json'))
rows=mm+new
def gid(r):
  m=re.search(r'gurkerl\.at/(\d+)-',r.get('url') or '');return m.group(1) if m else None
def comp(r):
  i=gid(r)
  if not i: return None
  try: return parse_composition(get(f'https://www.gurkerl.at/api/v1/products/{i}/composition'))
  except Exception as e: return None
with cf.ThreadPoolExecutor(8) as ex: CO=list(ex.map(comp,rows))
json.dump([list(c) if c else None for c in CO],open('enrich_comp_2026-10-13T02.json','w'),ensure_ascii=False)
def off(ean):
  try:
    d=get(f'https://world.openfoodfacts.org/api/v2/product/{ean}.json?fields=code,product_name,brands,nutriments,emb_codes,image_front_url,countries_tags,quantity,manufacturing_places,packaging_tags')
    return d.get('product') if d.get('status')==1 else None
  except Exception: return None
eans=set()
for r,c in zip(rows,CO):
  if c and c[4] and not r.get('ean'): r['_ean']=c[4]
  e=r.get('ean') or r.get('_ean')
  if e: eans.add(str(e))
with cf.ThreadPoolExecutor(4) as ex: OFF=dict(zip(sorted(eans),ex.map(off,sorted(eans))))
json.dump(OFF,open('enrich_off_2026-10-13T02.json','w'),ensure_ascii=False)
print('gurkerl comp',sum(1 for c in CO if c),'eans',len(eans),'off hits',sum(1 for v in OFF.values() if v))
