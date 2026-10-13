import json,urllib.request,time
out=[]
for brand in ['spar','s-budget','spar-natur-pur','spar-premium','spar-veggie','good-choice','primana','chef-select','clever','billa','ja-naturlich','simply-good','le-gusto','cucina-nobile','spar-feine-kuche','omis-schmankerl','leibspeis','tann','despar','spar-enjoy']:
  for page in range(1,6):
    u=f'https://world.openfoodfacts.org/api/v2/search?brands_tags={brand}&fields=code,product_name,brands,emb_codes,manufacturing_places,stores&page_size=200&page={page}'
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research-bot/1.0'}),timeout=60))
    except Exception as e: print(brand,e); break
    ps=d.get('products',[]); out+= [dict(p,qbrand=brand) for p in ps]
    if len(ps)<200: break
    time.sleep(1)
  print(brand,sum(1 for p in out if p['qbrand']==brand),sum(1 for p in out if p['qbrand']==brand and p.get('emb_codes')))
json.dump(out,open('off_brand.json','w'),ensure_ascii=False)
