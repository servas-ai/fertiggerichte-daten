"""Deploy gate: Top 50 (pli and eur10p) contain only stage meal/stew, no dry, no dessert, meal-sized rows."""
import json,sys,re
R=json.load(open(sys.argv[1] if len(sys.argv)>1 else '/workspace/fertig-app/public/data.json'))['rows']
bad=[]
for key,rev in (('pli',True),('eur10p',False)):
    L=sorted([r for r in R if r.get(key) is not None and r.get('rankable')],key=lambda r:r[key],reverse=rev)[:50]
    for r in L:
        if r.get('stage') not in ('meal','stew') or r.get('dry') or r.get('nutrition_basis')=='dry' or r.get('gang')=='dessert' or r.get('meal_class') not in ('meal','multi_portion'):
            bad.append((key,r['name'],r.get('stage'),r.get('dry'),r.get('meal_class')))
    for r in L:
        mc=r.get('meal_check') or {}
        if not mc.get('ok') or not (400<=(mc.get('kcal') or 0)<=900) or (mc.get('protein') or 0)<20: bad.append((key,r['name'],'meal_check',mc.get('kcal'),mc.get('protein')))
        if r.get('segment') in ('grocery','meal_kit') or r.get('meal_class')=='snack_side' or r.get('component'): bad.append((key,r['name'],'not a ready meal'))
        if key=='pli':
            if (r.get('score') or 0)<30 or not r.get('price') or not r.get('store'): bad.append((key,r['name'],'score<30/no price/shop'))
            mc=r.get('meal_check') or {}; ep=r['price']*mc['portion']/r['size'] if r.get('size') and mc.get('portion') else r['price']
            exp=round(0.5*r['score']+0.5*min((mc['protein']/ep)/20,1)*100,1)
            if abs(exp-r['pli'])>0.15: bad.append((key,r['name'],'pli formula',r['pli'],exp))
# regress_top50.mjs parity: same NONMEAL list
NM=re.compile(r'^\S+ lasagne$|lasagne (hartweizen)?$|lasagneblätter|lasagne ?teig|suppe-(abc|gerstl|sternderl|hörnchen)|suppennudeln|suppeneinlage|backerbsen|suppenpulver|pesto|\bsugo\b|topfencreme|mousse|pudding|cheesecake|strudel|dessert|götterspeise',re.I)
for r in sorted([r for r in R if r.get('pli') is not None],key=lambda r:-r['pli'])[:50]:
    if NM.search(r['name']): bad.append(('pli',r['name'],'regress_top50 NONMEAL'))
import re
DES=re.compile(r'dessert|brûlée|lavakuchen|mousse|pudding|tiramisu|panna cotta|cheesecake|topfencreme|kaiserschmarr|germknödel|milchreis',re.I)
GRO=re.compile(r'toastkäse|protein ?brot|eiweißbrot|wurstsalat|ramyun|aufstrich',re.I)
for r in R:
    if (r.get('gang')=='dessert' or DES.search(r['name'])) and (r.get('rankable') or r.get('pli') is not None): bad.append(('any',r['name'],'dessert ranked'))
    if DES.search(r['name']) and r.get('gang')!='dessert' and r.get('segment') not in ('grocery',) and not re.search(r'gemüse|spinat',r['name'],re.I): bad.append(('label',r['name'],'dessert not labelled gang=dessert'))
    if GRO.search(r['name']) and (r.get('rankable') or r.get('pli') is not None): bad.append(('any',r['name'],'grocery ranked'))
if bad:
    print('TOP50 GATE FAILED',len(bad)); [print(' ',b) for b in bad[:20]]; sys.exit(1)
print('top50 gate ok')
