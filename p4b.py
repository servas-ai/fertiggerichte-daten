import json,urllib.request,time
out=[]
B=['spar','s-budget','spar-natur-pur','spar-premium','spar-veggie','good-choice','primana','chef-select','clever','billa','ja-naturlich','simply-good','le-gusto','cucina-nobile','spar-feine-kuche','omis-schmankerl','leibspeis','despar','spar-enjoy','billa-immer-gut','inzersdorfer','hofstadter','billa-genusswelt','vemondo','vitasia','fair-hof']
def get(u):
  for t in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research-bot/1.0 (contact via grokbot)'}),timeout=60))
    except Exception as e: time.sleep(5*(t+1))
  return None
for brand in B:
  for page in range(1,11):
    d=get(f'https://world.openfoodfacts.org/api/v2/search?brands_tags={brand}&fields=code,product_name,brands,emb_codes,manufacturing_places,stores,countries_tags&page_size=100&page={page}')
    if not d: print('fail',brand,page); break
    ps=d.get('products',[]); out+=[dict(p,qbrand=brand) for p in ps]
    if len(ps)<100: break
    time.sleep(2)
  print(brand,sum(1 for p in out if p['qbrand']==brand),sum(1 for p in out if p['qbrand']==brand and p.get('emb_codes')),flush=True)
  json.dump(out,open('off_brand.json','w'),ensure_ascii=False)
