import json,sys,time,signal,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
def h(*a): raise TimeoutError()
signal.signal(signal.SIGALRM,h)
mode=sys.argv[1]
if mode=='pizza':
    P=json.load(open('/tmp/h11/mp_new.json'))
    urls=[p['source_url'] for p in P if 'Pizza' in (p['category'] or '') or 'Fertiggerichte' in (p['category'] or '') and 'Suppen' not in (p['category'] or '')]
else:
    S=json.load(open('/workspace/fertig/connectors_new.json'))
    urls=[x['url'] for x in S if x['store']=='MPreis']
out=[]
for u in urls:
    signal.alarm(25)
    try:
        p=M.product(u)
        if p: out.append(p.__dict__)
    except Exception as e: print('ERR',u,type(e).__name__)
    finally: signal.alarm(0)
    time.sleep(0.5)
json.dump(out,open(f'/tmp/h11/mp2_{mode}.json','w'),ensure_ascii=False,default=str,indent=0)
print(mode,len(urls),len(out))
