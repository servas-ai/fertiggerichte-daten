# hourly T00 (2026-10-14T00): BILLA product-discovery search with brand/dish stems not tried in earlier hours; only items not yet in scored/connectors_new (url or name+store)
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if str(x.get('store') or '').upper()=='BILLA'}
Q=["little lunch","erasco","suppenliebe","zurück zum ursprung suppe","ja natürlich suppe","ja natürlich fertiggericht","billa corso","clever fertiggericht","vegavita","garden gourmet","rügenwalder","like meat","wagner pizza","ristorante pizza","gustavo gusto","toni kaiser","frosta","iglo","inzersdorfer","felix dose","sonnen bassermann","bamboo garden","natsu","yum asia","indian kitchen","stastnik","hink","schmankerl","vegini","simply good","kartoffelpuffer","rösti","cevapcici","schinkenfleckerl","eiernockerl","tiroler gröstl","beuschel","szegediner","fiaker","kohlrouladen","gefüllte paprika","spinatknödel","käsespätzle","flammkuchen","pinsa","quiche","burrito","enchilada","gyoza","frühlingsrollen","dim sum","nasi goreng","bami goreng","pad thai","butter chicken","tikka masala","chili sin carne","gulaschsuppe","erbsensuppe","linsensuppe","kürbissuppe","minestrone","hühnersuppe","pho","ramen","paella","moussaka","cannelloni","tortelloni","bowl","couscous","backhendl","cordon bleu","schlemmerfilet","kabeljau","calamari","palatschinken","topfenknödel","marillenknödel","zwetschkenknödel","dampfnudeln","buchteln","topfenstrudel","milchreis"]
b=Billa(); out=[]; seen=set()
for q in Q:
    try: ps=b.search(q,100)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.3)
json.dump([p.__dict__ for p in out],open('/tmp/h00/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
for p in out: print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category)
