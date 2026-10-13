import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa, Penny
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={(k(x['name']),(x.get('store') or '').upper()) for x in S}
Q=["knödel","germknödel","kaiserschmarrn","nudelpfanne","paella","nasi goreng","bami goreng","linsen","dal","ramen","pho","tortellini","gnocchi","chili sin carne","tiefkühl pizza","pizza","flammkuchen","lasagne","moussaka","cannelloni","schnitzel","cordon bleu","gemüsepfanne","wok","teriyaki","tikka masala","korma","butter chicken","eintopf","linseneintopf","erbseneintopf","gulaschsuppe","minestrone","cremesuppe","rindsuppe","frittatensuppe","leberknödel","spätzle","käsespätzle","schinkenfleckerl","krautfleckerl","strudel","palatschinken","marillenknödel","topfenknödel","burrito","enchilada","quiche","auflauf","gratin","fischstäbchen","backfisch","frühlingsrolle","dumplings","gyoza","bowl","couscous","risotto","maultaschen","ravioli","penne","spaghetti","mac and cheese","chili con carne","curry","fertiggericht","menü","suppe"]
b=Billa(); seen=set(); out=[]
for q in Q:
    try: ps=b.search(q,100)
    except Exception as e: print('ERR',q,e); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or (k(p.name),'BILLA') in names: continue
        seen.add(p.source_id); out.append(p.__dict__); n+=1
    print(q,len(ps),'new',n); time.sleep(0.3)
json.dump(out,open('/tmp/h12/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
