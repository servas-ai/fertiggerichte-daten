import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa, Penny
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={(k(x['name']),(x.get('store') or '').upper()) for x in S}
Q=["suppe","eintopf","gulaschsuppe","linsensuppe","erbsensuppe","bohnensuppe","hühnersuppe","nudelsuppe","tomatensuppe","kürbissuppe","rindsuppe","leberknödelsuppe","minestrone","chili","gulasch","fiakergulasch","szegediner","beuschel","ragout","geschnetzeltes","rindsrouladen","schweinsbraten","stelze","backhendl","cordon bleu","grammelknödel","fleischknödel","selchfleischknödel","speckknödel","kasnocken","käsespätzle","schlutzkrapfen","kärntner kasnudeln","germknödel","topfenknödel","marillenknödel","mohnnudeln","buchteln","strudel","topfenstrudel","apfelstrudel","scheiterhaufen","palatschinken","kaiserschmarrn","grießschmarrn","milchreis","lasagne","cannelloni","moussaka","auflauf","risotto","paella","curry","tikka","butter chicken","nasi goreng","bami goreng","pad thai","ramen","gyoza","dumplings","frühlingsrolle","wan tan","pizza","flammkuchen","baguette","burrito","quiche","fischstäbchen","schlemmerfilet","backfisch","nuggets","gemüselaibchen","erdäpfeltascherl","gebackene champignons","camembert gebacken","mozzarella sticks","menü","fertiggericht","tiefkühl","dose","konserve","linsen","bohnen in tomatensauce","ravioli dose","eintopf dose","schinkenfleckerl","krautfleckerl","nockerl","spätzle","gnocchi pfanne","pfanne"]
out=[]; seen=set()
for S_,st in ((Billa(),'BILLA'),):
  for q in Q:
    try: ps=S_.search(q,100)
    except Exception as e: print('ERR',q,e); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or (k(p.name),st) in names: continue
        seen.add(p.source_id); out.append(p.__dict__); n+=1
    print(st,q,len(ps),'new',n,flush=True); time.sleep(0.3)
json.dump(out,open('/tmp/h14/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
