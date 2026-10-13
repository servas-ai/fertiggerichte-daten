import json,urllib.request,urllib.parse
terms="good choice;fertiggerichte;suppe;eintopf;gulasch;chili con carne;curry;risotto;lasagne;bowl;nudeln sauce fertig;linsen;knödel;gemüsepfanne;erbsensuppe;ravioli;tortellini;couscous;dal;bolognese;spätzle;gnocchi;hühnersuppe;rindsuppe;paella;reisgericht;5 minuten terrine;cup noodles;ja natürlich suppe;clever suppe".split(';')
allp={}
for t in terms:
  for p in range(3):
    u="https://shop.billa.at/api/product-discovery/products?"+urllib.parse.urlencode({'searchTerm':t,'page':p,'pageSize':50,'storeId':'00-10'})
    try:d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
    except Exception as e: print(t,e);break
    for r in d.get('results',[]): allp[r['sku']]=r
    if len(d.get('results',[]))<50: break
  print(t,d.get('total'))
json.dump(allp,open('raw.json','w'),ensure_ascii=False)
from collections import Counter
print(len(allp));print(Counter(r['category'] for r in allp.values()).most_common(60))
