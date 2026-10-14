# hourly T07: Penny online assortment — ready meals not yet present
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import penny_shop as P
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
print('penny listing...',flush=True)
rs=P.listing(pages=15, delay=0.8)
ps=[P.to_product(r) for r in rs]
print('listing',len(ps),flush=True)
new=[p for p in ps if p.source_url not in urls and P.is_ready_meal(p)]
print('new ready meals',len(new),flush=True)
out=[]
b=Billa()
for p in new:
    # Penny often lacks nutrition — twin via BILLA 00-<rewe article>
    n=p.nutrition_100g or {}
    twin=None
    sid=str(p.source_id or '')
    # try BILLA twin
    try:
        # REWE/Penny article numbers often map to BILLA 00-<num>
        for cand in [f'00-{sid}', sid]:
            pass
        # search by name+brand
        q=f"{p.brand or ''} {p.name or ''}".strip()[:50]
        if q:
            bs=b.search(q,10)
            for bp in bs:
                if bp.size_g and p.size_g and abs(bp.size_g-p.size_g)<=max(5,0.05*p.size_g):
                    b.enrich(bp); time.sleep(0.3)
                    if (bp.nutrition_100g or {}).get('kcal'):
                        twin=bp; break
    except Exception as e:
        p.extra=p.extra or {}; p.extra['twin_err']=str(e)
    d=p.__dict__.copy()
    if twin:
        d['nutrition_100g']=twin.nutrition_100g
        d['ean']=d.get('ean') or twin.ean
        d['producer']=d.get('producer') or twin.producer
        d['extra']=d.get('extra') or {}
        d['extra']['twin_billa']=twin.source_url
        d['extra']['twin_kcal']=twin.nutrition_100g.get('kcal')
    n=d.get('nutrition_100g') or {}
    print(p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'| img',bool(p.image_url),'| twin',bool(twin),flush=True)
    out.append(d)
    time.sleep(0.2)
json.dump(out,open('/tmp/h07/penny_cand.json','w'),ensure_ascii=False,default=str)
print('PENNY',len(out))
