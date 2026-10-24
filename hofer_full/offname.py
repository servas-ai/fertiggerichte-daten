import json,re,subprocess,time,urllib.parse
from fill import norm
A=json.load(open('/workspace/fertig-app/public/data.json'))['rows']
h=[r for r in A if r['store']=='Hofer' and r.get('kcal') is None]
got={}
for r in h:
  q=f'"{r["name"]}"'
  u='https://search.openfoodfacts.org/search?'+urllib.parse.urlencode({'q':q,'page_size':10,'fields':'code,product_name,product_name_de,brands,nutriments,nutriscore_grade,nova_group,product_quantity,countries_tags,stores'})
  try: hits=json.loads(subprocess.run(['curl','-s','-m','30','-A','food-connectors/0.1 (+https://github.com/servas-ai/food-connectors)',u],capture_output=True).stdout).get('hits',[])
  except Exception: hits=[]
  for p in hits:
    nm=p.get('product_name_de') or p.get('product_name') or ''
    b=' '.join(p.get('brands') or []) if isinstance(p.get('brands'),list) else str(p.get('brands'))
    st=str(p.get('stores'))+b
    if norm(nm)==norm(r['name']) and (norm(r.get('brand') or '') in norm(b) or 'hofer' in st.lower() or 'aldi' in st.lower()) and (p.get('nutriments') or {}).get('energy-kcal_100g') is not None:
      got[r['name']]=p;break
  time.sleep(1.1)
print(len(h),'matched',len(got));json.dump(got,open('off_name_match.json','w'),ensure_ascii=False)
