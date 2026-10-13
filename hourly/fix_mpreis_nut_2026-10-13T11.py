"""Correct MPreis rows whose nutrition was parsed from the per-portion block (adapter bug fixed in food-connectors 2026-10-13T11)."""
import json,os
os.chdir('/workspace/fertig')
V={p['source_url']:p for p in json.load(open('hourly/mpreis_reverify_2026-10-13T11.json'))}
cn=json.load(open('connectors_new.json')); K=('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')
fixed,emptied=[],[]
for x in cn:
  if x['store']!='MPreis' or x['url'] not in V: continue
  n=V[x['url']]['nutrition_100g'] or {}
  old={k:x.get(k+'_100') for k in K}
  if not n:
    continue  # page now shows no per-100 g block -> keep but report
  if any(n.get(k) is not None and old.get(k) is not None and abs(float(n[k])-float(old[k]))>0.051 for k in K):
    for k in K: x[k+'_100']=None if n.get(k) is None else float(n[k])
    g=x['size_g']; x['protein_pack']=round(n['protein']*g/100,1) if n.get('protein') is not None and g else None
    x['kcal_pack']=round(n['kcal']*g/100) if n.get('kcal') and g else None
    x['nut_source']='MPreis Webshop (Nährwerte je 100 g, re-verified 2026-10-13T11)'
    fixed.append((x['name'],old['kcal'],n.get('kcal'),old['protein'],n.get('protein')))
json.dump(cn,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(fixed=fixed),open('hourly/mpreis_nutfix_2026-10-13T11.json','w'),ensure_ascii=False,indent=1)
print('fixed',len(fixed)); [print(' ',*f) for f in fixed]
