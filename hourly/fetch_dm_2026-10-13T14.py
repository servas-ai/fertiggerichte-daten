import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import dm_shop as dm
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have=set()
for x in S:
    for f in ('url','source_url'):
        m=re.search(r'dm\.at/p/d/(\d+)/',str(x.get(f) or ''))
        if m: have.add(m.group(1))
eans={str(x.get('ean')).lstrip('0') for x in S if x.get('ean') and 'dm' in str(x.get('store')).lower()}
W=re.compile(r'suppe|eintopf|fertiggericht|curry|chili|gulasch|linsen|dal-|risotto|lasagne|ravioli|gericht|menue|ragout|tikka|korma|masala|tortellini|gnocchi|spaetzle|knoedel|paella|couscous|bulgur|kichererbsen|bohnen-eintopf|stew|ramen|pho-|laksa|nudel-pfanne|reispfanne|pfanne')
urls=[u for u in dm.sitemap_urls() if W.search(u.rsplit('/',1)[1]) and not dm.SLUG_NOT.search(u.rsplit('/',1)[1]) and re.search(r'/p/d/(\d+)/',u).group(1) not in have]
print('candidate urls',len(urls),'have dm ids',len(have))
out=[]
for u in urls:
    dan=int(re.search(r'/p/d/(\d+)/',u).group(1))
    try: p=dm.product(dan,u)
    except Exception as e: print('ERR',u,e); time.sleep(1); continue
    time.sleep(0.8)
    if not dm.is_ready_meal(p): continue
    if p.ean and p.ean.lstrip('0') in eans: continue
    out.append(p.__dict__); print(p.source_id,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.extra.get('nutrition_basis'),'|',p.category.split(' > ',2)[-1],flush=True)
json.dump(out,open('hourly/cand_dm_2026-10-13T14.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
