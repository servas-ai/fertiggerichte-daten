import json,urllib.request,concurrent.futures as cf
d=json.load(open('raw.json'))
keep={'Menüschalen','Beutel','Dose','Asien','Suppen','Fertiggerichte Ungekühlt','Fertiggerichte Gekühlt','Fertiggerichte gekühlt','Frische Pasta & Beilagen','Reis & Pasta'}
skus=[k for k,v in d.items() if v['category'] in keep]
def f(s):
  try:return s,json.load(urllib.request.urlopen(urllib.request.Request("https://shop.billa.at/api/product-discovery/products/"+s,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
  except Exception as e:return s,None
det={}
with cf.ThreadPoolExecutor(6) as ex:
  for s,r in ex.map(f,skus): det[s]=r
json.dump(det,open('det.json','w'),ensure_ascii=False);print(len(skus),sum(1 for v in det.values() if v))
