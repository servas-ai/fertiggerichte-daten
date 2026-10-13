import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
g=Gurkerl()
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}|{x.get('source_url') for x in S}; names={k(x['name']) for x in S}
Q=["eintopf","linseneintopf","erbseneintopf","bohneneintopf","gulaschsuppe","kürbissuppe","tomatensuppe","hühnersuppe","rindsuppe","minestrone","erdäpfelsuppe","kartoffelsuppe","cremesuppe","frittatensuppe","leberknödelsuppe","ramen","pho","laksa","chili con carne","chili sin carne","curry","dal","tikka masala","butter chicken","risotto","paella","nasi goreng","bami goreng","pad thai","gnocchi","lasagne","cannelloni","moussaka","auflauf","gratin","käsespätzle","krautfleckerl","schinkenfleckerl","kasnocken","schlutzkrapfen","maultaschen","tortellini","ravioli","germknödel","marillenknödel","topfenknödel","kaiserschmarrn","palatschinken","strudel","milchreis","grießschmarrn","buchteln","pizza","flammkuchen","burrito","enchilada","quiche","cordon bleu","schnitzel","backhendl","fischstäbchen","schlemmerfilet","gyoza","dumplings","frühlingsrollen","bao","wok","gemüsepfanne","bratkartoffeln","rösti","knödel","gulasch","ragout","geschnetzeltes","rouladen","sauerkraut","beuschel","szegediner","stroganoff","fertiggericht","menü","mikrowelle","tiefkühl gericht","couscous","bulgur","falafel","kichererbsen curry","teriyaki","sushi","onigiri","tteokbokki","mac and cheese","spaghetti bolognese","penne","nudelpfanne","reispfanne","polenta","hirse","eierspeis","omelett","shakshuka","ofengemüse","kohlrouladen","fleischlaibchen","faschierte laibchen","leberkäse","würstel","hot dog","burger","toast","baguette","calzone","pide","börek","pierogi","pelmeni","wareniki","borschtsch","soljanka","gazpacho","misosuppe","wan tan"]
seen=set(); out=[]
for q in Q:
    try: ps=g.search(q,100)
    except Exception as e: print('ERR',q,e); time.sleep(2); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p.__dict__); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.25)
json.dump(out,open('/tmp/h14/g_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
