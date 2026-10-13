import json,re,collections
S=json.load(open('../scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={k(x['name']) for x in S}; codes=set()
for x in S:
  for f in ('url','image_url'):
    m=re.findall(r'\d{8,14}',str(x.get(f) or '').replace('/','')); codes|=set(m)
  if x.get('ean'): codes.add(str(x['ean']))
V=json.load(open('../expand_v5.json')); names|={k(x['name']) for x in V}
BADC=r'en:sauces|en:condiments|en:soup-bases|en:broths|en:dehydrated|en:instant-soups|en:baby|en:spreads|en:yogurts|en:ice-creams|en:cereals|en:dried|en:pasta$|en:pastas$|en:rices$|en:breads|en:biscuits|en:beverages|en:plant-milks|en:dessert-mixes|skyr|petits-suisses|soy-yogurt|en:stuffed-pastas|beets-salads|en:cheeses|fresh-cheese|quark|en:cooking-helpers'
BADN=r'fond|würze|bouillon|brühe|pulver|fix\b|basis|sauce|soße|sugo|pesto|instant|cup|5 minuten|terrine|yum yum|ramen nudeln|dressing|eis\b|joghurt|yogurt|fruchtzwerge|skyr|topfen\b|soja natur|aus soja'
out=[]
for p in json.load(open('off_at.json')):
  n=(p.get('product_name_de') or p.get('product_name') or '').strip(); c=' '.join(p.get('categories_tags') or [])
  nu=p.get('nutriments') or {}
  if not n or not p.get('image_front_url') or nu.get('proteins_100g') is None or nu.get('energy-kcal_100g') is None: continue
  if re.search(BADC,c) or re.search(BADN,n,re.I): continue
  if p['code'] in codes or k(n) in names: continue
  names.add(k(n))
  st=(p.get('stores') or '').split(',')[0].strip() or None
  g=p.get('product_quantity')
  try: g=float(g) if g else None
  except: g=None
  out.append(dict(name=n,brand=(p.get('brands') or '').split(',')[0] or None,store=st,price_eur=None,size_g=g,price_per_kg=None,
    url=f"https://world.openfoodfacts.org/product/{p['code']}",image_url=p['image_front_url'],
    kcal_100=nu.get('energy-kcal_100g'),protein_100=nu.get('proteins_100g'),fat_100=nu.get('fat_100g'),satfat_100=nu.get('saturated-fat_100g'),
    carbs_100=nu.get('carbohydrates_100g'),sugar_100=nu.get('sugars_100g'),fiber_100=nu.get('fiber_100g'),salt_100=nu.get('salt_100g'),
    nutriscore=(p.get('nutriscore_grade') or '').upper() if (p.get('nutriscore_grade') or '') in list('abcde') else None,
    producer_id=p.get('emb_codes') or None,category=(p.get('categories_tags') or ['?'])[-1].split(':')[-1],
    price_source=None,price_date=None,price_status='kein Preis (nur Open Food Facts)',offOnly=True,nut_source='Open Food Facts (ODbL)',ean=p['code']))
print(len(out),collections.Counter(x['store'] for x in out).most_common(12))
json.dump(out,open('off_new.json','w'),ensure_ascii=False,indent=1)
import random;random.seed(2)
for x in random.sample(out,30): print(x['name'],'|',x['category'])
