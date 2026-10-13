import json,urllib.request,time
out=[]
for p in range(130):
  for t in range(3):
    try:
      r=urllib.request.urlopen(urllib.request.Request(f"https://shop.billa.at/api/product-discovery/products?page={p}&pageSize=100",headers={'User-Agent':'Mozilla/5.0'}),timeout=30);d=json.load(r);break
    except Exception as e: time.sleep(3);d={'results':[]}
  out+=d['results']
  if len(d['results'])<100 and p>5: break
  time.sleep(0.7)
json.dump(out,open('billa_all.json','w'),ensure_ascii=False);print(len(out))
