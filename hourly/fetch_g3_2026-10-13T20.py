# hourly T20: Gurkerl search with dish stems not used in T16-T18 (Austrian/international dishes); only ids not yet present, in-stock
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
g=Gurkerl()
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
ids_have=set()
for x in S:
  for u in (x.get('url'),x.get('source_url')):
    m=re.search(r'gurkerl\.at/(\d+)-',u or '')
    if m: ids_have.add(int(m.group(1)))
for f in ('/tmp/h20/g_new.json','/tmp/h20/g2_new.json'):
  ids_have|={int(p['source_id']) for p in json.load(open(f))}
names={k(x['name']) for x in S if 'gurkerl' in str(x.get('store','')).lower()}
Q=["kasnudel","käsnudel","maultaschen","pfannen gnocchi","gefüllte","germknödel","eiernockerl","krautfleckerl","schinkenfleckerl","spinatknödel","kaspressknödel","rahmgeschnetzeltes","zürcher","cordon bleu","putengeschnetzeltes","risi bisi","nasi goreng","bami goreng","biryani","tikka masala","butter chicken","dal","korma","jambalaya","lecso","musaka","pierogi","piroggen","pelmeni","dumplings","gyoza","dim sum","empanada","enchilada","quesadilla","tacos","fajita","chili con carne","linseneintopf","bohneneintopf","kartoffelsuppe","kürbissuppe","tomatensuppe","minestrone","nudelsuppe","gemüsesuppe","rindsuppe","gulasch","rahmspinat","beuschel","stelze","schweinsbraten","tafelspitz","zwiebelrostbraten","faschierter braten","fleischlaibchen","krautrouladen","paprikahuhn","hühnerkeule","coq au vin","bourguignon","stroganoff","lasagne","cannelloni","moussaka","auflauf","ofengericht","pfannengericht","wok","curry","risotto","paella","couscous","bulgur","quinoa bowl","buddha bowl","eintopf","suppe","kaiserschmarrn","germknödel","marillenknödel","mohnnudeln","milchrahmstrudel","apfelstrudel","topfenstrudel","scheiterhaufen","reisauflauf","grießschmarrn","palatschinken","pofesen"]
cand={}
for q in Q:
  try: ps=g.search(q,100)
  except Exception as e: print('ERR',q,e); time.sleep(2); continue
  n=0
  for p in ps:
    i=int(p.source_id)
    if i in ids_have or i in cand or k(p.name) in names: continue
    cand[i]=p.category; n+=1
  print('q',q,len(ps),'new',n,flush=True); time.sleep(0.25)
out=[]
for p in g.products(list(cand),None):
  p.category=cand.get(int(p.source_id)) or p.category
  if p.extra.get('archived') or not p.extra.get('in_stock') or k(p.name) in names: continue
  out.append(p.__dict__)
json.dump(out,open('/tmp/h20/g3_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
