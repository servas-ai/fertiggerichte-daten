import json,os,re
src=['expand.json','classics.json','classics_ext.json','brandfam_products.json','billa.json','spar.json','spar_live.json','hofer_lidl.json','hofer_goodchoice.json','dm_live.json','frozen_quick.json','other.json','spar_browser_norm.json','more_meals_norm.json','connectors_new.json','online_mealprep.json','expand_v5.json']
names=set();eans=set();urls=set()
def norm(s): return re.sub(r'[^a-z0-9äöüß]','',(s or '').lower())
for f in src:
  if not os.path.exists(f): continue
  d=json.load(open(f))
  if isinstance(d,dict): d=d.get('rows') or d.get('products') or list(d.values())
  for x in d:
    if not isinstance(x,dict): continue
    names.add(norm(x.get('name')))
    for k in ('ean','gtin','code'):
      if x.get(k): eans.add(str(x[k]))
    for k in ('url','source_url'):
      if x.get(k): urls.add(x[k])
json.dump({'names':sorted(names),'eans':sorted(eans),'urls':sorted(urls)},open('hourly/idx_2026-10-13T02.json','w'))
print(len(names),len(eans),len(urls))
