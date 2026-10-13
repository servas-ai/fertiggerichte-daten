import json,urllib.request,concurrent.futures as cf
H={'User-Agent':'Mozilla/5.0'}
def J(u):return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60))
PS=100
d=J(f"https://shop.billa.at/api/product-discovery/products?page=0&pageSize={PS}");tot=d['total'];print('total',tot,len(d['results']))
def P(p):
  for i in range(3):
    try:return J(f"https://shop.billa.at/api/product-discovery/products?page={p}&pageSize={PS}")['results']
    except Exception as e:err=e
  print('fail',p,err);return []
allp={r['sku']:r for r in d['results']}
with cf.ThreadPoolExecutor(8) as ex:
  for rs in ex.map(P,range(1,tot//PS+2)):
    for r in rs:allp[r['sku']]=r
print('got',len(allp))
json.dump(allp,open('hourly/billa_all.json','w'),ensure_ascii=False)
