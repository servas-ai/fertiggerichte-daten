import json,urllib.request,time,sys
F='code,product_name,product_name_de,brands,nutriments,emb_codes,image_front_url,image_url,quantity,stores,origins,nutriscore_grade'
allp=[];p=1
while True:
  u=f'https://world.openfoodfacts.org/api/v2/search?countries_tags=en:austria&page_size=1000&page={p}&fields={F}'
  try:d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'GrokBot-research/1.0 (contact via app)'}),timeout=120))
  except Exception as e: print('err',p,e,flush=True);time.sleep(20);continue
  pr=d.get('products',[]);allp+=pr;print(p,len(allp),d.get('count'),flush=True)
  if not pr or len(allp)>=d.get('count',0):break
  p+=1;time.sleep(7)
json.dump(allp,open('off_at.json','w'),ensure_ascii=False)
