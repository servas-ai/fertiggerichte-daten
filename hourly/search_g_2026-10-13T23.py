# hourly T23: Gurkerl search-metadata walk with heat-up meal stems -> ids not yet in scored/connectors_new, category in ready-meal/frozen-meal/soup/pizza/fish shelves, then fresh stock + composition enrich
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.schema import Product
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
CAT=re.compile(r'Fertiggericht|Schnelle Küche|Suppen|Pizza|Fischstäbchen|Backfisch|Schlemmerfilet|Mehlspeisen|Menüs|Dosengericht|Tiefkühl.*(Fleisch|Geflügel|Snack|Gemüse|Kartoffel|Fisch)|Feinkost|Marks',re.I)
Q="lasagne gulasch curry risotto eintopf suppe auflauf gratin knödel strudel pizza chili paella moussaka cannelloni tortelloni ravioli gnocchi spätzle nockerl schnitzel nuggets cordon backfisch bowl menü ragout geschnetzeltes frikassee bolognese carbonara schmarrn palatschinken germknödel flammkuchen quiche burrito laibchen cevapcici börek tikka masala dal wok bami nasi pad-thai ramen pho gyoza dumplings frühlingsrolle kroketten baguette tarte pie hotpot eintopf linsen bohnen erbsensuppe gulaschsuppe kürbissuppe minestrone".split()
g=Gurkerl(); seen=set(); new=[]
for q in Q:
    try: ps=g.search(q,100)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in have or p.source_id in seen or not CAT.search(p.category or ''): continue
        seen.add(p.source_id); new.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.3)
print('cands',len(new),flush=True)
ids=[int(p.source_id) for p in new]; cat={p.source_id:p.category for p in new}
fr=g.products(ids)
out=[]
for p in fr:
    if not p.extra.get('in_stock') or p.extra.get('archived'): continue
    p.category=cat.get(p.source_id)
    try: g.enrich(p)
    except Exception as e: print('ENRICH-ERR',p.source_id,e)
    time.sleep(0.3); out.append(p.__dict__)
    print(p.source_id,'|',p.category,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:40].replace('\n',' '),'|',p.producer_id,flush=True)
json.dump(out,open('hourly/cand_gurkerl_search_2026-10-13T23.json','w'),ensure_ascii=False,default=str,indent=0)
print('instock',len(out))
