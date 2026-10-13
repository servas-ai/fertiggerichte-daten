import json,urllib.request,concurrent.futures as cf
C=json.load(open('cand.json'));det=json.load(open('det.json'))
ids=[c['id'] for c in C if c['store']=='billa' and not det.get(c['id'])]
def f(s):
  try:return s,json.load(urllib.request.urlopen(urllib.request.Request("https://shop.billa.at/api/product-discovery/products/"+s,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
  except Exception as e:return s,None
out={}
with cf.ThreadPoolExecutor(6) as ex:
  for s,r in ex.map(f,ids): out[s]=r
json.dump(out,open('det2.json','w'),ensure_ascii=False);print(len(ids),sum(1 for v in out.values() if v))
