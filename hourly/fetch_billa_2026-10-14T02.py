# hourly T02: BILLA search with stems less used in T00 / focus on heat-up meals not yet present
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if str(x.get('store') or '').upper()=='BILLA'}
Q=['hühner sticks', 'blockhouse', 'garnelen knusper', 'minestrone', 'gefüllte paprika', 'backhendlfilet', 'cheeseburger', 'protein burger', 'fleischlaibchen', 'cevapcici', 'grillhendl', 'schweinsbraten', 'zwiebelrostbraten', 'rindsroulade', 'spinatlasagne', 'gemüselasagne', 'lasagne bolognese', 'nudelauflauf', 'kartoffelauflauf', 'fleischstrudel', 'krautstrudel', 'spinatstrudel', 'gemüsestrudel', 'topfenknödel', 'marillenknödel', 'zwetschkenknödel', 'buchteln', 'palatschinken', 'cordon bleu', 'chicken nuggets', 'putenschnitzel paniert', 'fischburger', 'lachs gratin', 'schlemmerfilet bordelaise', 'frittatensuppe', 'leberknödelsuppe', 'nudelsuppe', 'linsensuppe', 'bohnensuppe', 'kürbissuppe', 'tomatensuppe', 'gemüsesuppe', 'rindsuppe', 'hühnerfrikassee', 'ofengemüse', 'kartoffelgratin', 'semmelknödel mit', 'schwammerlsauce', 'eierschwammerl', 'rahmgeschnetzeltes', 'züricher geschnetzeltes', 'hühnercurry', 'rotes curry', 'grünes curry', 'linsen dal', 'falafel', 'gemüselaibchen', 'spinatlaibchen', 'käsenockerl', 'schinkenfleckerl', 'flammkuchen', 'quiche', 'pinsa', 'pizza salami', 'pizza prosciutto', 'pizza tonno', 'pizza spinaci', 'pizza funghi', 'pizza vegetale', 'flammkuchen elsässer', 'burrito', 'wrap hähnchen', 'hot dog', 'toast hawaii', 'baguette pizza', 'ofenkartoffel', 'rösti mit', 'bratkartoffel mit', 'gnocchi pfanne', 'tortellini', 'spätzle pfanne', 'asia pfanne', 'wok', 'teriyaki', 'sushi', 'dim sum', 'wan tan', 'samosa', 'empanada', 'frühlingsrolle', 'pierogi', 'pelmeni']
b=Billa(); out=[]; seen=set()
for q in Q:
    try: ps=b.search(q,80)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.25)
json.dump([p.__dict__ for p in out],open('/tmp/h02/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('TOTAL',len(out))
for p in out: print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category)
