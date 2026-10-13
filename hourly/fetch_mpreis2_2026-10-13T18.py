# hourly T18 (part 2: candidate URLs beyond the first 300)
# hourly T18 (2026-10-13T18): MPreis ready-meal categories + sitemap stem search (robots-allowed pages only); only urls/names not yet present
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}|{x.get('source_url') for x in S}
slug=lambda u:re.sub(r'-\d+$','',(u or '').rstrip('/').rsplit('/',1)[-1])
slugs={slug(u) for u in urls if u and 'mpreis' in u}
names={k(x['name']) for x in S if 'mpreis' in str(x.get('store','')).lower()}
cand=[]
for c in M.READY_MEAL_CATEGORIES:
    try: us=M.category_urls(c)
    except Exception as e: print('ERR',c,e); continue
    n=[u for u in us if u not in urls and slug(u) not in slugs and u not in cand]; cand+=n
    print(c,len(us),'new',len(n),flush=True); time.sleep(0.5)
STEMS=["gulasch","eintopf","suppe","lasagne","knoedel","strudel","schmarrn","curry","risotto","gnocchi","spaetzle","ravioli","tortellini","chili","reisfleisch","krautfleisch","fleckerl","menue","pizza","auflauf","laibchen","groestl","nockerl","palatschinken","moussaka","paella","bowl","cannelloni","ragout","frikassee","geschnetzeltes","braten","schnitzel","cordon","fischstaebchen","backfisch","schlemmerfilet","nuggets","fruehlingsrolle","pinsa","flammkuchen","quiche","burrito","wrap","tortelloni","maultaschen","kasnocken","schlutzkrapfen","kaspressknoedel","germknoedel","buchteln","milchreis","pudding","tiramisu","dal","korma","masala","nasi","bami","pad-thai","ramen","pho","tom-kha","tom-yum","gazpacho","bolognese","carbonara","gratin","linsen","bohnen","erbsen","kichererbsen"]
sm=M.sitemap_urls()
for s in STEMS:
    n=[u for u in sm if s in u.rsplit('/',1)[-1] and u not in urls and slug(u) not in slugs and u not in cand]
    cand+=n; print('stem',s,len(n),flush=True)
print('cand urls',len(cand),flush=True)
done={p['source_url'] for p in json.load(open('/tmp/h18/mpreis_new.json'))}
cand=[u for u in cand if u not in done][:420]
out=[]
for u in cand:
    try: p=M.product(u)
    except Exception as e: print('ERR',u,e); continue
    time.sleep(0.4)
    if not p or k(p.name) in names: continue
    out.append(p.__dict__)
json.dump(out,open('/tmp/h18/mpreis_new2.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
