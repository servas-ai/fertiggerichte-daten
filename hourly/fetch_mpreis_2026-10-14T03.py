# hourly T03: fetch hand-picked MPreis heat-up meal slugs from sitemap gap
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
SLUGS="""iglo-crispy-chicken-tempura-backteig-820541 wagner-piccolinis-tomate-mozzarella-pizza-802223 inzersdorfer-rindsgulasch-226502 dr-oetker-ristorante-salami-glutenfrei-815053 wagner-steinofen-diavolo-pizza-803234 wagner-air-fryer-salami-814506 dr-oetker-intermezzo-schinken-805702 jeden-tag-schinken-baguette-6er-packung-809410""".split()
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
json.dump(out,open('hourly/cand_mpreis_2026-10-14T03.json','w'),ensure_ascii=False,default=str,indent=0)
print('fetched',len(out))

