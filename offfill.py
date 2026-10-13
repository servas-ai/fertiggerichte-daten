import json,urllib.request,urllib.parse,time,difflib,re
L=json.load(open('hofer_lidl.json'));res={}
for i,x in enumerate(L):
  if x['kcal_100'] is not None: continue
  q=re.sub(r'\d+\s*(g|kg|ml)\b','',x['name']).replace('Fertiggericht','').strip()
  u='https://world.openfoodfacts.org/cgi/search.pl?'+urllib.parse.urlencode(dict(search_terms=q,search_simple=1,json=1,page_size=5,countries_tags_en='austria',fields='code,product_name,brands,quantity,image_front_url,nutriments,nutriscore_grade,emb_codes,origins,manufacturing_places,stores'))
  for t in range(3):
    try: res[x['name']]=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research-bot/1.0'}),timeout=40)).get('products',[]);break
    except Exception as e: time.sleep(10)
  print(x['name'],[(p.get('brands'),p.get('product_name')) for p in res.get(x['name'],[])][:3],flush=True)
  time.sleep(2)
json.dump(res,open('offfill_raw.json','w'),ensure_ascii=False)
