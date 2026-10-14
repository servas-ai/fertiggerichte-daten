# hourly T02: fetch hand-picked MPreis heat-up meal slugs from sitemap gap
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
SLUGS="""iglo-fischnroesti-msc-809315 iglo-goldschatz-kaese-msc-804484 iglo-goldschatz-kaese-msc-804469 iglo-goldschatz-spinat-msc-804472 iglo-polardorsch-knusperhuelle-msc-805518 iglo-iglo-knusper-abenteuer-809330 jeden-tag-knusperfilet-im-backteig-msc-812196 iglo-msc-fischncrunch-820539 iglo-msc-pazifischer-polardorsch-paniert-808931 knorr-veggie-penne-mit-broccoli-292024""".split()
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
json.dump(out,open('hourly/cand_mpreis2_2026-10-14T02.json','w'),ensure_ascii=False,default=str,indent=0)
print('fetched',len(out))

