# hourly T18 (2026-10-13T18): Gurkerl category walk (all MEAL_CATEGORIES) + extra search stems; only ids not yet in scored/connectors_new
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl, MEAL_CATEGORIES
g=Gurkerl()
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
urls={x.get('url') for x in S}|{x.get('source_url') for x in S}
ids_have=set()
for u in urls:
    m=re.search(r'gurkerl\.at/(\d+)-',u or '')
    if m: ids_have.add(int(m.group(1)))
names={k(x['name']) for x in S if 'gurkerl' in str(x.get('store','')).lower()}
cand={}
for cid,label in MEAL_CATEGORIES.items():
    try: ids=g.category_ids(cid)
    except Exception as e: print('ERR',cid,e); continue
    n=0
    for i in ids:
        if i in ids_have or i in cand: continue
        cand[i]=label; n+=1
    print(cid,label,len(ids),'new',n,flush=True)
Q=["fertiggericht tk","tiefkühlgericht","mikrowellengericht","nudelgericht","reisgericht","asia gericht","indisches gericht","thai curry","green curry","red curry","massaman","sukiyaki","katsu","donburi","onigiri","sushi","wonton","bao","baozi","frühlingsrollen tk","samosa","pakora","falafel bowl","hummus bowl","poke","burrito bowl","chili sin carne","bolognese fertig","lasagne tk","cannelloni tk","moussaka tk","pastitsio","gratin","kartoffelgratin","auflauf tk","nudelauflauf","fleischstrudel","gemüsestrudel","spinatstrudel","topfenstrudel","apfelstrudel tk","mohnnudeln","marillenknödel","zwetschkenknödel","topfenknödel","buchteln","powidltascherl","kasnocken","kasnudeln","schlutzkrapfen","tiroler","gröstl tk","erdäpfelgulasch","fiakergulasch","kalbsgulasch","hirschragout","wildgulasch","reisfleisch","krautfleisch","bohnengulasch","linsen mit","fisolen","erbsen eintopf","gemüseeintopf","kichererbsen","hühnerfrikassee","ragout fin","königsberger","rouladen","braten fertig","pulled pork","spare ribs","chicken wings","hendl","grillhendl","backhendl","schnitzel","nuggets","fischlaibchen","lachs","garnelen","paella tk","risotto tk","gnocchi pfanne","tortelloni","agnolotti","pasta fresca","suppentopf","ramen nudelsuppe","pho","miso suppe","tom kha","gazpacho","borschtsch","gulaschsuppe","leberknödelsuppe","grießnockerlsuppe","frittatensuppe","erdäpfelsuppe","schwammerlsuppe","knoblauchsuppe","zwiebelsuppe","rahmsuppe","cremesuppe","brokkolisuppe","karottensuppe","süßkartoffel","linsensuppe","bohnensuppe","erbsensuppe","hühnersuppe","dessert","pudding","creme brulee","mousse","tiramisu","panna cotta","grießschmarrn","kaiserschmarrn tk","palatschinken tk","crepes","waffeln","pancakes","milchreis","kaiserschöberl","dean david","youcook","hello fresh","nanu","prepmymeal","freshfood","mama mancini","wagner","dr oetker","iglo","frosta","bürger","maggi","knorr","erasco","felix","inzersdorfer","hengstenberg","sonnen bassermann","natur aktiv","gurkerl gericht","miil","rewe beste wahl","vegavita","garden gourmet","like meat","rügenwalder","planted","beyond","vegini"]
for q in Q:
    try: ps=g.search(q,100)
    except Exception as e: print('ERR',q,e); time.sleep(2); continue
    n=0
    for p in ps:
        i=int(p.source_id)
        if i in ids_have or i in cand or k(p.name) in names: continue
        cand[i]=p.category; n+=1
    print('q',q,len(ps),'new',n,flush=True); time.sleep(0.25)
ps=g.products(list(cand),None)
out=[]
for p in ps:
    p.category=cand.get(int(p.source_id)) or p.category
    if p.extra.get('archived') or not p.extra.get('in_stock'): continue
    if k(p.name) in names: continue
    out.append(p.__dict__)
json.dump(out,open('/tmp/h18/g_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total in-stock new',len(out))
