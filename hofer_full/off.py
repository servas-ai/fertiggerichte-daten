import json,subprocess,time,os
F='code,product_name,product_name_de,brands,quantity,product_quantity,nutriments,nutriscore_grade,nova_group,categories_tags,image_front_url,ingredients_text_de,ingredients_text,allergens_tags,stores_tags,countries_tags'
out={};pg=1
while True:
  u=f'https://world.openfoodfacts.org/api/v2/search?stores_tags=hofer&page_size=100&page={pg}&fields={F}'
  for a in range(5):
    r=subprocess.run(['curl','-s','-m','120','-A','food-connectors/0.1 (+https://github.com/servas-ai/food-connectors)',u],capture_output=True)
    try: d=json.loads(r.stdout);break
    except Exception: time.sleep(30)
  else: break
  ps=d.get('products',[]);[out.__setitem__(p['code'],p) for p in ps]
  print(pg,d.get('count'),len(out),flush=True)
  if not ps or pg>=d.get('page_count',0): break
  pg+=1;time.sleep(7)
json.dump(list(out.values()),open('off_hofer_all.json','w'),ensure_ascii=False)
