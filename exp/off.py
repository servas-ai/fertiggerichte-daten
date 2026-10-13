import json,urllib.request,time
cats=['en:meals','en:soups','en:desserts','en:prepared-salads','en:frozen-ready-made-meals','en:pasta-dishes','en:meals-with-meat','en:puddings']
out={}
for c in cats:
  for page in range(1,6):
    u=f"https://world.openfoodfacts.org/api/v2/search?countries_tags_en=austria&categories_tags_en={c}&page_size=200&page={page}&fields=code,product_name,product_name_de,brands,stores,image_front_url,nutriments,nutriscore_grade,nova_group,quantity,product_quantity,categories_tags,emb_codes,manufacturing_places,labels_tags"
    for t in range(3):
      try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'fertig-vergleich/1.0 (martin)'}),timeout=60));break
      except Exception as e: print('err',c,page,e);time.sleep(10);d={'products':[]}
    for p in d['products']: out[p['code']]=p
    print(c,page,len(d['products']),len(out),flush=True)
    if len(d['products'])<200: break
    time.sleep(6)
json.dump(list(out.values()),open('off_at.json','w'),ensure_ascii=False)
