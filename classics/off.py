import json,re,sys,urllib.request,urllib.parse,time,concurrent.futures as cf
sys.path.insert(0,'classics'); from dishes import dish,LABEL,D
F={'kcal':'energy-kcal_100g','protein':'proteins_100g','fat':'fat_100g','satfat':'saturated-fat_100g','carbs':'carbohydrates_100g','sugar':'sugars_100g','fiber':'fiber_100g','salt':'salt_100g'}
SM={'hofer':'HOFER','aldi':'HOFER','lidl':'LIDL','penny':'Penny','dm':'dm','dm-drogerie':'dm'}
def q(lab):
  for i in range(3):
    try:
      u='https://search.openfoodfacts.org/search?'+urllib.parse.urlencode(dict(q=lab+' countries_tags:"en:austria"',page_size=60,fields='code,product_name,product_name_de,brands,nutriments,emb_codes,image_front_url,stores_tags,stores,quantity,product_quantity,last_modified_t,nutriscore_grade,origins'))
      return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'GrokBot-research/1.0'}),timeout=40)).get('hits',[])
    except Exception: time.sleep(4)
  return []
out={}
labs=[l for k,l,p in D if k not in('chili-andere',)]
with cf.ThreadPoolExecutor(3) as e:
  for lab,hits in zip(labs,e.map(q,labs)):
    for h in hits:
      nm=h.get('product_name_de') or h.get('product_name') or ''
      br=h.get('brands'); br=', '.join(br) if isinstance(br,list) else br
      k=dish(nm)
      if not k: continue
      st=[SM[s] for s in (h.get('stores_tags') or []) if s in SM]
      bl=(br or '').lower()
      if not st:
        if re.search(r'good choice|gut bio|mama mancini|buon gusto|hofer|aldi|cucina|asia green garden|bbq|ein gutes stück',bl): st=['HOFER']
        elif re.search(r'chef select|vitasia|kania|freshona|deluxe|lidl|vemondo|milbona|combino',bl): st=['LIDL']
        elif re.search(r'penny|ich bin österreich|today',bl): st=['Penny']
        elif re.search(r'dmbio|dm bio|^dm\b',bl): st=['dm']
      if not st: continue
      n=h.get('nutriments') or {}
      out[h['code']]=dict(name=nm,brand=br,store=st[0],stores_all=st,price_eur=None,size_g=h.get('product_quantity'),url=f"https://world.openfoodfacts.org/product/{h['code']}",source_url=f"https://world.openfoodfacts.org/product/{h['code']}",ean=h['code'],image_url=h.get('image_front_url'),
        **{kk+'_100':n.get(v) for kk,v in F.items()},nutriscore=(h.get('nutriscore_grade') or '').upper() or None,producer_id=(', '.join(h['emb_codes']) if isinstance(h.get('emb_codes'),list) else h.get('emb_codes')) or None,origin=h.get('origins') or None,
        nut_source='Open Food Facts '+h['code'],price_source=None,price_date=None,dish_key=k,dish=LABEL[k],source_file='classics.json',category='Fertiggericht')
L=list(out.values())
for r in L:
  try: r['size_g']=float(r['size_g']) if r['size_g'] else None
  except: r['size_g']=None
  if r['size_g'] and r['protein_100'] is not None: r['protein_pack']=round(r['protein_100']*r['size_g']/100,1)
  if r['size_g'] and r['kcal_100'] is not None: r['kcal_pack']=round(r['kcal_100']*r['size_g']/100,1)
json.dump(L,open('classics/off_items.json','w'),ensure_ascii=False,indent=1)
import collections;print(len(L),collections.Counter(r['store'] for r in L));[print(r['store'],r['dish_key'],r['brand'],'|',r['name']) for r in L]
