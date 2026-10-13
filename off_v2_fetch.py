# OFF fetch for score v2: nova, ingredients, fvl estimate, serving size. 1 req/s (lock /tmp/off-host.ts)
import json,re,time,urllib.request,os,sys
d=json.load(open('scored.json'))
eans=sorted({str(x['ean']) for x in d if x.get('ean') and re.fullmatch(r'\d{8,14}',str(x['ean']))})
C='off_v2_cache.json'; c=json.load(open(C)) if os.path.exists(C) else {}
F='code,product_name,nova_group,nova_groups_tags,ingredients_text,ingredients_text_de,ingredients,serving_size,serving_quantity,product_quantity,nutriments,additives_tags,nutriscore_grade,preparation,nutrition_data_prepared_per'
for i,e in enumerate(eans):
    if e in c: continue
    time.sleep(1.1)
    try:
        req=urllib.request.Request(f'https://world.openfoodfacts.org/api/v2/product/{e}.json?fields={F}',headers={'User-Agent':'GoodChoice-score/2.0 (servas-ai; research)'})
        j=json.load(urllib.request.urlopen(req,timeout=20))
        p=j.get('product') if j.get('status')==1 else None
        if p:
            ing=p.get('ingredients') or []
            p['ingredients']=[{k:g.get(k) for k in ('text','percent_estimate','percent','vegetable','id')} for g in ing[:25]]
            nm=p.get('nutriments') or {}
            p['nutriments']={k:v for k,v in nm.items() if k.endswith('_100g') or k.endswith('_prepared_100g')}
        c[e]=p or {'_missing':True}
    except Exception as ex: c[e]={'_error':str(ex)[:100]}
    if i%25==0: json.dump(c,open(C,'w')); print(i,len(eans),flush=True)
json.dump(c,open(C,'w')); print('done',len(c))
