"""Gaps overlay: fills missing price/shop only from exact-name matches in heisse-preise raw dump
(heisse_preise_raw.json, fetched 2026-10-12); otherwise flags price_status/shop_status='unknown' with reason.
Never invents. Usage: python3 gaps_overlay.py [--apply public/data.json]"""
import json,re,sys,fcntl,unicodedata
def N(s):
    s=unicodedata.normalize('NFKD',(s or '').lower()).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
SM={'Billa':'billa','Spar':'spar','Hofer':'hofer','MPreis':'mpreis','dm':'dm','Unimarkt':'unimarkt'}
NICE={v:k for k,v in SM.items()}
raw=json.load(open('/workspace/fertig/heisse_preise_raw.json'))
idx={}
for x in raw:
    if x.get('store') not in NICE: continue
    ph=x.get('priceHistory') or [];p=x.get('price');dt=ph[0]['date'] if ph else None
    if p is None: continue
    for k in {N(x['name']),N((x.get('brand') or '')+' '+x['name'])}:
        idx.setdefault(k,{}).setdefault(x['store'],(p,dt,x.get('url')))
path=sys.argv[2] if len(sys.argv)>2 else '/workspace/fertig-app/public/data.json'
D=json.load(open(path));R=D['rows'];ov={}
for r in R:
    o={}
    keys=[N(r['name']),N((r.get('brand') or '')+' '+r['name'])]
    hit=next((idx[k] for k in keys if k in idx),None)
    if r.get('price') in (None,0,''):
        st=SM.get(r['store'])
        if st and hit and st in hit and hit[st][1] and hit[st][1]>='2025-10-01':
            p,dt,u=hit[st];o.update(price=p,price_status='filled',psrc=f'heisse-preise raw exact-name match {r["store"]} {dt}',price_date=dt)
        else:
            why=('Kette ohne offene Preisquelle (Lidl 401 / kein Penny-Feed)' if r['store'] in('Lidl','Penny') else
                 'kein Laden bekannt (OFF)' if r['store'].startswith('unbekannt') else
                 'kein exakter Namenstreffer im heisse-preise-Dump' if not(hit and st and st in hit) else 'nur Preis älter als 12 Monate')
            o.update(price_status='unknown',price_reason=why)
    if r['store'].startswith('unbekannt'):
        if hit:
            sts=sorted(hit);o.update(store=NICE[sts[0]],stores_seen=[NICE[s] for s in sts],shop_status='filled',shop_src='heisse-preise raw exact-name match',availability_level='chain')
            if r.get('price') in (None,0,'') and hit[sts[0]][1] and hit[sts[0]][1]>='2025-10-01':
                p,dt,u=hit[sts[0]];o.update(price=p,price_status='filled',psrc=f'heisse-preise raw exact-name match {NICE[sts[0]]} {dt}',price_date=dt);o.pop('price_reason',None)
        else: o.update(shop_status='unknown',shop_reason='Open Food Facts ohne Händlerangabe; kein exakter Namenstreffer in AT-Händlerdaten')
    o.setdefault('availability_level','chain')
    ov[r['store']+'|'+r['name']]=o
json.dump(ov,open('/workspace/fertig/gaps_overlay.json','w'),ensure_ascii=False)
import collections as C
print('price filled',sum(1 for o in ov.values() if o.get('price_status')=='filled'),'price unknown',sum(1 for o in ov.values() if o.get('price_status')=='unknown'),
 C.Counter(o.get('price_reason') for o in ov.values() if o.get('price_reason')),
 'shop filled',sum(1 for o in ov.values() if o.get('shop_status')=='filled'),'shop unknown',sum(1 for o in ov.values() if o.get('shop_status')=='unknown'))
if '--apply' in sys.argv:
    import os
    def _ancestor_holds(lock='/tmp/fertig-data.lock'):
        # 2026-10-13T14: callers often wrap us in `flock /tmp/fertig-data.lock …`; a second flock on a new fd from
        # this child would wait on our own ancestor forever (seen twice today). Skip locking if an ancestor holds it.
        pid=os.getppid()
        while pid>1:
            try:
                if any(os.path.realpath(f'/proc/{pid}/fd/{fd}')==lock for fd in os.listdir(f'/proc/{pid}/fd')): return True
                pid=int(open(f'/proc/{pid}/stat').read().rsplit(')',1)[1].split()[1])
            except Exception: return False
        return False
    with open('/tmp/fertig-data.lock','w') as L:
        if not _ancestor_holds(): fcntl.flock(L,fcntl.LOCK_EX)
        D=json.load(open(path))
        for r in D['rows']:
            o=ov.get(r['store']+'|'+r['name'])
            if o and r['name']: r.update(o)
        json.dump(D,open(path,'w'),ensure_ascii=False,separators=(',',':'))
        print('applied',path)
