import json,sys,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl, MEAL_CATEGORIES
g=Gurkerl()
cats={620:"Tiefkühlprodukte > Pizza, Baguettes & Flammkuchen > Pizza",134312:"Marks & Spencer > Tiefgekühlte Produkte",137493:"Kühlregal > Schnelle Küche > Kochboxen",989:"Kühlregal > Schnelle Küche > Salate & Bowls",137873:"Tiefkühlprodukte > Fisch > Schlemmerfilets & Backfisch",619:"Tiefkühlprodukte > Pizza, Baguettes & Flammkuchen"}
cats.update(MEAL_CATEGORIES)
S=json.load(open('/workspace/fertig/scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}|{x.get('source_url') for x in S}; names={k(x['name']) for x in S}; eans={str(x.get('ean')).lstrip('0') for x in S if x.get('ean')}
seen=set(); out=[]
for cid,label in cats.items():
    try: ids=[i for i in g.category_ids(cid) if i not in seen]
    except Exception as e: print('ERR',cid,e); continue
    seen.update(ids)
    ps=[p for p in g.products(ids,label) if not p.extra.get('archived')]
    new=[p for p in ps if p.source_url not in urls and k(p.name) not in names]
    print(cid,label,len(ids),'new',len(new))
    out+=new
json.dump([p.__dict__ if hasattr(p,'__dict__') else p for p in out],open('/tmp/h11/g_new.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
