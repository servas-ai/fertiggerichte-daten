# hourly T23: BILLA product-discovery search with brand/product stems found at MPreis/Gurkerl this hour; only items not yet in scored/connectors_new (url or name+store), then detail-API enrich
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if str(x.get('store') or '').upper()=='BILLA'}
Q=["costa ofen","costa garnelen","alnatura bowl","street food noodles","stritzinger","chicken fries","ofengarnelen","crispy chicken","hühnerflügerl","nuggets backteig","express risotto","lasagne al forno","rindsgulasch","chili cheese nuggets","pierre baguette","banoffee","backfisch","schlemmerfilet","fischstäbchen","kaiserschmarrn tk","germknödel","marillenknödel","mohnnudeln","topfenknödel","bowl","curry reis","gulasch dose","eintopf dose","linseneintopf","erbseneintopf","chili con carne dose","ravioli dose","tortellini dose","nudeln in sauce"]
b=Billa(); out=[]; seen=set()
for q in Q:
    try: ps=b.search(q,60)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.3)
json.dump([p.__dict__ for p in out],open('/tmp/h23/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
for p in out: print(p.source_id,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category)
