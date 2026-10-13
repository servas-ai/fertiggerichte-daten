import json,urllib.request
cats="fertiggerichte-gekuehlt-15390 fertiggerichte-ungekuehlt-15391 suppen-15394 suppen-15400 schnelle-kueche-15389 fertiggerichte-gekuehlt-15232 fertiggerichte-ungekuehlt-15233".split()
allp={}
for c in cats:
  p=0
  while True:
    u=f"https://shop.billa.at/api/product-discovery/categories/{c}/products?page={p}&pageSize=100"
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
    r=d.get('results',[])
    for x in r: x['_cat']=c; allp.setdefault(x['sku'],x)
    if len(r)<100: break
    p+=1
  print(c,d.get('total'))
json.dump(allp,open('raw.json','w'),ensure_ascii=False)
print(len(allp))
