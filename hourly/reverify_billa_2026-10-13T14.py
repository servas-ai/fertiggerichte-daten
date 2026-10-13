import json,sys,time,re,shutil
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import storage_info
from food_connectors.http import get
cn=json.load(open('connectors_new.json'))
ev=[]
for r in cn:
    u=r.get('url') or ''
    m=re.search(r'shop\.billa\.at/produkte/.*-(\d{2})(\d+)$',u)
    if not m: continue
    sku=f"{m.group(1)}-{m.group(2)}"
    try: d=get(f"https://shop.billa.at/api/product-discovery/products/{sku}")
    except Exception as e: ev.append(dict(url=u,error=str(e))); continue
    time.sleep(0.3)
    si=storage_info(d); pr=d.get('price') or {}; std=(pr.get('standard') or {}).get('value'); reg=(pr.get('regular') or {}).get('value')
    e=dict(name=r['name'],url=u,sku=sku,storage=si['storage'],category_path=si['category_path'],old_price=r.get('price_eur'),regular=reg/100 if reg else None,standard=std/100 if std else None,in_promotion=bool(d.get('inPromotion')),old_pack=r.get('packaging'))
    ch=[]
    if si['storage']=='frozen' and not str(r.get('packaging') or '').startswith('Tiefkühl') and not str(r.get('packaging') or '').startswith('Trocken'):
        r['packaging']=r['packaging_hint']='Tiefkühl (TK)'; ch.append('packaging→TK')
    if d.get('inPromotion') and std and r.get('price_eur') and abs(std/100-r['price_eur'])>0.005:
        r['price_promo_eur']=r['price_eur']; r['price_eur']=std/100
        if r.get('size_g'): r['price_per_kg']=round(r['price_eur']/r['size_g']*1000,2)
        r['price_source']=re.sub(r'\(.*\)','(product-discovery API, Normalpreis; Aktion separat)',r.get('price_source') or 'food-connectors/billa 2026-10-13')+' – reverified 2026-10-13T14'
        ch.append(f"price {e['old_price']}→{r['price_eur']} (Aktion {e['old_price']})")
    e['changes']=ch; ev.append(e)
    if ch: print(r['name'],ch)
shutil.copy('connectors_new.json','connectors_new.json.bak_hourly14')
json.dump(cn,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(ev,open('hourly/billa_reverify_2026-10-13T14.json','w'),ensure_ascii=False,indent=1)
print('checked',len(ev),'changed',sum(1 for e in ev if e.get('changes')))
