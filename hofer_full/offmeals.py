import json,re,datetime
from fill import norm,hp_find,cut,H
OFF=json.load(open('off_hofer_all.json'))
MEALCAT=re.compile(r'en:(meals|prepared-meals|frozen-ready-made-meals|soups|pizzas|lasagnas|sandwiches|salads|prepared-salads|pasta-dishes|filled-pastas|stews|canned-meals|microwave-meals|wraps|dumplings|frozen-pizzas|instant-noodles|noodles-dishes|rice-dishes|ravioli|curries|meals-with-meat|meals-with-fish|vegetarian-meals)\b')
NOT=re.compile(r'en:(sauces|condiments|spreads|dressings|beverages|desserts|biscuits|breads)\b')
have_e={m.group(1) for a in H for m in [re.search(r'product/(\d{8,14})',str(a.get('url')))] if m}
have_n={norm(a['name']) for a in H}
out=[];old=0
for p in OFF:
  c=' '.join(p.get('categories_tags') or [])
  if not MEALCAT.search(c) or NOT.search(c): continue
  nm=p.get('product_name_de') or p.get('product_name')
  if not nm or p['code'] in have_e or norm(nm) in have_n: continue
  nu=p.get('nutriments') or {}
  try: sz=float(p.get('product_quantity')) if p.get('product_quantity') else None
  except: sz=None
  x=dict(name=nm.strip(),brand=(p.get('brands') or [''])[0] if isinstance(p.get('brands'),list) else (p.get('brands') or '').split(',')[0],store='Hofer',
   size_g=sz,url=f"https://world.openfoodfacts.org/product/{p['code']}",image_url=p.get('image_front_url'),ean=p['code'],
   kcal_100=nu.get('energy-kcal_100g'),protein_100=nu.get('proteins_100g'),fat_100=nu.get('fat_100g'),satfat_100=nu.get('saturated-fat_100g'),
   carbs_100=nu.get('carbohydrates_100g'),sugar_100=nu.get('sugars_100g'),fiber_100=nu.get('fiber_100g'),salt_100=nu.get('salt_100g'),
   nutriscore=(p.get('nutriscore_grade') or '').upper() if p.get('nutriscore_grade') in list('abcde') else None,nova=p.get('nova_group'),
   ingredients=p.get('ingredients_text_de') or p.get('ingredients_text'),category=c.split()[-1].replace('en:','') if c else None,
   price_eur=None,price_source=None,price_date=None,notes='OFF stores:Hofer (2026-10-13)',segment='ready_meal')
  h=hp_find(nm,x['brand'])
  if h and sz and h.get('quantity') and h.get('unit') in('g','ml') and abs(h['quantity']-sz)/sz>0.1: h=None
  if h and h.get('price'):
    pd=(h.get('priceHistory') or [{}])[0].get('date');o=bool(pd and pd<cut);old+=o
    x.update(price_eur=h['price'],price_date=pd,price_live=False if o else None,price_old=o,price_source=f"heisse-preise.io Hofer {pd}"+(' Altpreis >12 Monate' if o else ''))
  if x['price_eur'] and sz: x['price_per_kg']=round(x['price_eur']/sz*1000,2)
  out.append(x)
out=[x for x in out if x['price_eur']]
json.dump(out,open('/workspace/fertig/hofer_off_meals.json','w'),ensure_ascii=False,indent=1)
print(len(out),'priced',sum(1 for x in out if x['price_eur']),'old',old,'kcal',sum(1 for x in out if x['kcal_100'] is not None))
