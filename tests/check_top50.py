"""Deploy gate: Top 50 (pli and eur10p) contain only stage meal/stew, no dry, no dessert, meal-sized rows."""
import json,sys
R=json.load(open(sys.argv[1] if len(sys.argv)>1 else '/workspace/fertig-app/public/data.json'))['rows']
bad=[]
for key,rev in (('pli',True),('eur10p',False)):
    L=sorted([r for r in R if r.get(key) is not None and r.get('rankable')],key=lambda r:r[key],reverse=rev)[:50]
    for r in L:
        if r.get('stage') not in ('meal','stew') or r.get('dry') or r.get('nutrition_basis')=='dry' or r.get('gang')=='dessert' or r.get('meal_class') not in ('meal','multi_portion'):
            bad.append((key,r['name'],r.get('stage'),r.get('dry'),r.get('meal_class')))
if bad:
    print('TOP50 GATE FAILED',len(bad)); [print(' ',b) for b in bad[:20]]; sys.exit(1)
print('top50 gate ok')
