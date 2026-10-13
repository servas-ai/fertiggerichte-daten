import json,urllib.request,concurrent.futures as cf
E=json.load(open('eans.json'))
def g(e):
  try:
    u=f'https://world.openfoodfacts.org/api/v2/product/{e}.json?fields=product_name,brands,emb_codes,manufacturing_places,origins,stores,labels'
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research-bot/1.0'}),timeout=30)
    return e,json.load(r).get('product')
  except Exception as ex: return e,{'err':str(ex)}
with cf.ThreadPoolExecutor(8) as p: R=dict(p.map(g,E))
json.dump(R,open('off_prod.json','w'),ensure_ascii=False)
print(sum(1 for v in R.values() if v and v.get('emb_codes')), sum(1 for v in R.values() if v and v.get('manufacturing_places')), sum(1 for v in R.values() if v and 'err' in v))
for e,v in R.items():
  if v and (v.get('emb_codes') or v.get('manufacturing_places')): print(e,v.get('brands'),'|',v.get('product_name'),'|',v.get('emb_codes'),'|',v.get('manufacturing_places'))
