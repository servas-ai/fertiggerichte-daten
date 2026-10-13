import json,sys,re,time,signal
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}|{x.get('source_url') for x in S}
eans={str(x.get('ean')).lstrip('0') for x in S if x.get('ean') and x.get('store')=='MPreis'}
cands=[]
for c in ["/shop/c/lebensmittel/tiefkuehl/pizza-baguette-26319064","/shop/c/lebensmittel/konserven-fertiggerichte-suppen/suppen-45429089","/shop/c/lebensmittel/tiefkuehl/fertiggerichte-24125257","/shop/c/lebensmittel/konserven-fertiggerichte-suppen/fertiggerichte-5812424"]:
    try: us=M.category_urls(c)
    except Exception as e: print('ERR',c,e); continue
    nu=[u for u in us if u not in urls and u not in cands]; print(c,len(us),'new',len(nu)); cands+=nu; time.sleep(0.5)
def h(*a): raise TimeoutError()
signal.signal(signal.SIGALRM,h)
out=[]
for u in cands:
    signal.alarm(25)
    try:
        p=M.product(u)
        if p: out.append(p.__dict__); print(p.name,'|',p.brand,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.category)
    except Exception as e: print('ERR',u,type(e).__name__)
    finally: signal.alarm(0)
    time.sleep(0.5)
json.dump(out,open('/tmp/h11/mp_new.json','w'),ensure_ascii=False,default=str,indent=0)
