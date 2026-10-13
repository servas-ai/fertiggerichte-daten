import json,subprocess,time
F='code,product_name,product_name_de,brands,quantity,product_quantity,nutriments,nutriscore_grade,nova_group,categories_tags,image_front_url,ingredients_text_de,ingredients_text,allergens_tags,stores,countries_tags'
out={}
for pg in range(1,10):
  r=subprocess.run(['curl','-s','-m','60','-A','food-connectors/0.1 (+https://github.com/servas-ai/food-connectors)',f'https://search.openfoodfacts.org/search?q=stores:hofer&page_size=100&page={pg}&fields={F}'],capture_output=True)
  h=json.loads(r.stdout).get('hits',[])
  for p in h: out[p['code']]=p
  print(pg,len(h),len(out));
  if not h: break
  time.sleep(2)
json.dump(list(out.values()),open('off_hofer_all.json','w'),ensure_ascii=False)
