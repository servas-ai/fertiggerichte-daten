# hourly T17 (2026-10-13T17): Gurkerl category walk (all MEAL_CATEGORIES) + extra search stems; only ids not yet in scored/connectors_new
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
Q=["fertiggericht","eintopf","suppe","gulasch","curry","risotto","lasagne","knödel","strudel","schmarrn","pizza","auflauf","chili","ramen","dal","paella","gnocchi","tortellini","ravioli","maultaschen","spätzle","nockerl","frühlingsrolle","gyoza","burrito","bowl","menü","dose gericht","mikrowelle","sugo fertig","fleischbällchen","hühnerfrikassee","rindsgulasch","szegediner","tafelspitz","schweinsbraten","geschnetzeltes","cevapcici","sarma","pljeskavica","musaka","djuvec","cremespinat mit","erdäpfelpüree","kaiserschmarrn","milchreis","grießbrei","pudding fertig","tiramisu","panna cotta","mousse au chocolat","topfencreme","germknödel","palatschinken","pofesen","dampfnudel","linseneintopf","bohneneintopf","erbseneintopf","kartoffelsuppe","kürbissuppe","tomatensuppe","gulaschsuppe","minestrone","hühnersuppe","rindsuppe mit","frittaten","nudelsuppe","pasta fertig","mac and cheese","käsespätzle","krautfleckerl","schinkenfleckerl","blunzengröstl","gröstl","hascheeknödel","grammelknödel","speckknödel","semmelknödel mit","kaspressknödel","schupfnudeln","stroganoff","ragout","rahmgeschnetzeltes","hendl curry","butter chicken","tikka masala","korma","biryani","nasi goreng","bami goreng","pad thai","teriyaki","bibimbap","enchilada","quesadilla","moussaka","lasagne verdure","cannelloni","flammkuchen","quiche","strudel gemüse","fischstäbchen","schlemmerfilet","backfisch","cordon bleu","schnitzel fertig","fleischlaibchen","faschierte laibchen","beuschel","gefüllte paprika","kohlrouladen","krautrouladen","chili con carne","dal makhani","shakshuka","polenta","couscous gericht","bulgur gericht","risotto fertig","vegan gericht","protein bowl","dean david","youcook","hello fresh","marley spoon"]
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
json.dump(out,open('/tmp/h17/g_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total in-stock new',len(out))
