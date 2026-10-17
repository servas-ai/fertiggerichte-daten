import json, sys, time, re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import spar_shop as S
D='/workspace/fertiggerichte-daten/'
pr={r['product_id']:r for r in json.load(open(D+'data/products.json'))}
rows=json.load(open(D+'data/prices.json'))
sp=[r for r in rows if r['chain']=='Spar' and r.get('price_status')!='live 2026']
out=[]
for r in sp:
    p=pr[r['product_id']]; url=p.get('url') or ''
    m=re.search(r'/p/(\d+)',url); res={'product_id':r['product_id'],'name':p['name'],'old':r}
    try:
        if m:
            a=S.article(m.group(1)); res['mode']='article'; res['article']=m.group(1)
            res['hit']=a.__dict__ if a else None
        else:
            d=S._q(p['name'],n=5); res['mode']='name'
            res['hits']=[S.to_product(h).__dict__ for h in (d.get('hits') or [])[:5]]
    except Exception as e: res['err']=repr(e)
    out.append(res); time.sleep(1)
json.dump(out,open(D+'raw/spar_reprice_probe_2026-10-17T2340.json','w'),ensure_ascii=False,indent=1,default=str)
for o in out:
    if o.get('mode')=='article':
        h=o['hit']; print('A',o['article'],o['name'][:45],'->',(h['name'][:45],h['price_eur'],h['size_g'],h['extra'].get('item_type'),h['extra'].get('stock_status')) if h else None, o.get('err',''))
    else:
        print('N',o['name'][:45],'->',[(h['name'][:40],h['price_eur'],h['size_g'],h['source_id']) for h in o.get('hits',[])[:3]], o.get('err',''))
