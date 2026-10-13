# hourly T16 (2026-10-13T16): BILLA product-discovery search with new ready-meal stems; only items not yet in scored/connectors_new (url or name+store)
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if str(x.get('store') or '').upper()=='BILLA'}
Q=["fertiggericht","fertig menü","mikrowelle","dosengericht","linsen mit speck","bohnen mit speck","reisfleisch","krautfleisch","hühnercurry","gefüllte paprika","fleischlaibchen","faschierter braten","rindsgulasch","saftgulasch","kalbsgulasch","hirschragout","wildragout","eierschwammerl","schwammerlsauce","rahmsuppe","knoblauchsuppe","zwiebelsuppe","grießnockerlsuppe","frittatensuppe","erdäpfelgulasch","bohnengulasch","käsnudeln","kasnudeln","schlipfkrapfen","tortelloni gericht","lasagne bolognese","lasagne verdure","spaghetti bolognese","penne arrabbiata","nudelauflauf","kartoffelgratin","erdäpfelgratin","moussaka","pastitsio","chili sin carne","veggie curry","korma","biryani","rendang","teriyaki","sweet sour","kung pao","wan tan suppe","miso","pho","tom kha","laksa","udon","yakisoba","bibimbap","burrito","quesadilla","enchiladas","pinsa","calzone","flammkuchen","pizza salami","pizza margherita","pizza speciale","pizza tonno","pizza funghi","baguette tk","snack pizza","pizza snack","schinkenkipferl","gemüsestrudel","spinatstrudel","krautstrudel","fleischstrudel","blunzengröstl","tiroler gröstl","bauerngröstl","schupfnudeln mit kraut","spätzlepfanne","käsespätzle","eiernockerl","topfennockerl","zwetschkenknödel","mohnnudeln","powidltascherl","buchteln","dampfnudeln","apfelstrudel","topfenstrudel","kaiserschmarrn","palatschinken","milchreis","grießbrei","schokopudding","fischstäbchen","backfisch","lachs gericht","seelachs","paella","risotto","gnocchi gericht","maultaschen","cordon bleu","hühnerschnitzel","backhendl","nuggets","chicken wings","frühlingsrollen","samosa","falafel","gemüselaibchen","kartoffelrösti","rösti","kroketten gefüllt","eintopf","suppe dose","gulaschsuppe dose","erbsensuppe","linseneintopf","kichererbsen eintopf","ready meal","bowl","couscous salat","nudelsalat"]
out=[]; seen=set(); b=Billa()
for q in Q:
    try: ps=b.search(q,100)
    except Exception as e: print('ERR',q,e); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p.__dict__); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.3)
json.dump(out,open('/tmp/h16/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
