# hourly T17: Identitätskennzeichen (EMB/oval health mark) lookup via Open Food Facts by EAN for connectors_new rows without producer_id
# only strict codes accepted (food_connectors.schema.find_producer_id); evidence kept in hourly/off_idk_2026-10-13T17.json
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.http import get
from food_connectors.schema import find_producer_id
cn=json.load(open('/workspace/fertig/connectors_new.json'))
eans=sorted({str(x['ean']).strip() for x in cn if x.get('ean') and not x.get('producer_id')})
print('eans',len(eans),flush=True); out={}
for e in eans:
    try: d=get(f"https://world.openfoodfacts.org/api/v2/product/{e}.json?fields=code,product_name,brands,emb_codes,brand_owner,manufacturing_places",timeout=20)
    except Exception as ex: out[e]={'_error':str(ex)[:80]}; time.sleep(1); continue
    p=d.get('product') if d.get('status')==1 else None
    if p: out[e]={k:p.get(k) for k in ('product_name','brands','emb_codes','brand_owner','manufacturing_places')}; out[e]['code_strict']=find_producer_id(p.get('emb_codes'))
    else: out[e]=None
    time.sleep(0.7)
json.dump(out,open('/workspace/fertig/hourly/off_idk_2026-10-13T17.json','w'),ensure_ascii=False,indent=1)
print('found',sum(1 for v in out.values() if v and not v.get('_error')),'codes',sum(1 for v in out.values() if v and v.get('code_strict')),'errors',sum(1 for v in out.values() if v and v.get('_error')))
