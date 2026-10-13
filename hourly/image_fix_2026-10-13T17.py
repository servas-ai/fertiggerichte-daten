# hourly T17: MPreis placeholder images (/assets/noImage_detail-*.webp, site-relative -> 404 in app) removed;
# replaced by an EAN-twin product photo from another shop row when available, else left empty (never invented)
import json,re,collections
S=json.load(open('/workspace/fertig/scored.json'))
n=collections.Counter()
for F in ['/workspace/fertig/connectors_new.json','/workspace/fertig/mpreis_new_2026-10-13.json']:
  D=json.load(open(F)); L=D if isinstance(D,list) else D.get('products') or D.get('items')
  pool=S+L
  img={}
  for x in pool:
    u=x.get('image_url') or x.get('image') or x.get('img')
    if x.get('ean') and u and str(u).startswith('http') and 'noimage' not in str(u).lower(): img.setdefault(str(x['ean']).lstrip('0'),u)
  for x in L:
    for f in ('image_url','image','img'):
      if f in x and x[f] and 'noimage' in str(x[f]).lower():
        tw=img.get(str(x.get('ean') or '').lstrip('0'))
        x[f]=tw; x['image_source']=('EAN-Zwilling (anderes Shop-Foto) 2026-10-13' if tw else None); n['twin' if tw else 'cleared']+=1
        print(F.rsplit('/',1)[-1],x.get('name'),'->',tw)
  json.dump(D,open(F,'w'),ensure_ascii=False,indent=1)
print(dict(n))
