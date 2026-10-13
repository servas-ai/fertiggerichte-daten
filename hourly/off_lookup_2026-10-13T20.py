# hourly T20: Open Food Facts lookup by EAN for T20 MPreis candidates (brand/brand_owner/emb_codes/nutriments per 100 g);
# used only (a) to fill brand / Identitätskennzeichen and (b) nutrition when the shop page has none — evidence kept in hourly/off_t20_2026-10-13T20.json
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.http import get
from food_connectors.schema import find_producer_id
eans=sys.argv[1].split(',')
out={}
F='/workspace/fertig/hourly/off_t20_2026-10-13T20.json'
try: out=json.load(open(F))
except Exception: pass
for e in eans:
    if e in out and out[e] and not out[e].get('_error'): continue
    try: d=get(f"https://world.openfoodfacts.org/api/v2/product/{e}.json?fields=code,product_name,brands,brand_owner,emb_codes,quantity,nutriments,nutrition_data_per,last_modified_t",timeout=25)
    except Exception as ex: out[e]={'_error':str(ex)[:80]}; time.sleep(1); continue
    p=d.get('product') if d.get('status')==1 else None
    if p:
        n=p.get('nutriments') or {}
        out[e]={k:p.get(k) for k in ('product_name','brands','brand_owner','emb_codes','quantity','nutrition_data_per','last_modified_t')}
        out[e]['code_strict']=find_producer_id(p.get('emb_codes'))
        out[e]['n100']={k:n.get(f'{o}_100g') for k,o in (('kcal','energy-kcal'),('fat','fat'),('satfat','saturated-fat'),('carbs','carbohydrates'),('sugar','sugars'),('fiber','fiber'),('protein','proteins'),('salt','salt'))}
    else: out[e]=None
    print(e,json.dumps(out[e],ensure_ascii=False)[:300],flush=True); time.sleep(0.8)
json.dump(out,open(F,'w'),ensure_ascii=False,indent=1)
