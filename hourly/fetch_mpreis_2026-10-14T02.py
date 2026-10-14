# hourly T02: fetch hand-picked MPreis heat-up meal slugs from sitemap gap
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
SLUGS="""felix-gefuellte-paprika-226902 inzersdorfer-gefuellte-paprika-140063 inzersdorfer-gefuellte-paprika-226800 iglo-huehner-sticks-804317 yuun-mee-garnelen-knusperpanade-667658 iglo-minestrone-810460 blockhouse-cheese-burger-813763 blockhouse-protein-burger-810590 blasko-backhendl-filet-10er-packung-32141 blasko-backhendlfilet-80362 pinsami-la-pinsa-114304 pinsami-mini-pinsa-klassisch-114479""".split()
out=[]
for s in SLUGS:
    u='https://www.mpreis.at/shop/p/'+s
    try: p=M.product(u)
    except Exception as e: print('ERR',s,str(e)[:100],flush=True); continue
    time.sleep(0.4)
    if not p: print('NONE',s,flush=True); continue
    out.append(p.__dict__)
    n=p.nutrition_100g or {}
    print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',p.ean,'|',(p.extra or {}).get('availability'),flush=True)
json.dump(out,open('hourly/cand_mpreis_2026-10-14T02.json','w'),ensure_ascii=False,default=str,indent=0)
print('fetched',len(out))

