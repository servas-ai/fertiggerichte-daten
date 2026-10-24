import json,re,collections
d=json.load(open(''+SRC+''))
rows=d['products'] if isinstance(d,dict) and 'products' in d else (d.get('rows') or list(d.values())[0] if isinstance(d,dict) else d)
print(type(d), list(d.keys()) if isinstance(d,dict) else '')
data=json.load(open('/workspace/fertig-app/public/data.json'))['rows']
eans={str(r.get('ean')) for r in data if r.get('ean')}
names={(r['store'],re.sub(r'\W+',' ',(r.get('name') or '').lower()).strip()) for r in data}
urls={(r.get('url') or '').split('?')[0].rstrip('/') for r in data}
new=[]
for p in rows:
    n=re.sub(r'\W+',' ',p['name'].lower()).strip()
    if (p.get('ean') and str(p['ean']) in eans) or (p['source_url'] or '').split('?')[0].rstrip('/') in urls or (p['store'],n) in names: continue
    new.append(p)
print(collections.Counter(p['store'] for p in rows), 'new', collections.Counter(p['store'] for p in new))
json.dump(new,open('/tmp/pab_new.json','w'),ensure_ascii=False)
for i,p in enumerate(new): print(i,p['store'],p['source_id'],'|',p['name'],'|',p['price_eur'],p['size_g'],'|',(p.get('category') or '')[-35:])
