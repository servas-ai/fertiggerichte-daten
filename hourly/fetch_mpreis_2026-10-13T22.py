# hourly T22: re-fetch hand-picked MPreis leftovers of the T20 walk (robots-allowed product pages: JSON-LD offer + Nährwerte tab) for fresh price/stock/nutrition
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
P={p['source_id']:p for f in ('/tmp/h20/mpreis_new.json','/tmp/h20/mpreis_new2.json') for p in json.load(open(f))}
SEL="770161 738005 606526 239216 239217 239199 805259 850446 804318 810227 813710 850411 815070 804347 804483 611613 812012 812013 803726 803725 802246 802284 802223 803234 815059 803176 585629 226115 367104 585630 812042".split()
out=[]
for sid in SEL:
    d=P.get(sid)
    if not d: print('MISSING',sid); continue
    try: p=M.product(d['source_url'])
    except Exception as e: print('ERR',sid,e); continue
    time.sleep(0.5)
    if not p: print('NONE',sid); continue
    out.append(p.__dict__)
    print(sid,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:40],'|',(p.extra or {}).get('availability'),flush=True)
json.dump(out,open('hourly/cand_mpreis_2026-10-13T22.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
