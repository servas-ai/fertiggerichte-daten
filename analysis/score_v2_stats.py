import json,collections as C,statistics as st,sys
a=json.load(open(sys.argv[1] if len(sys.argv)>1 else '/tmp/data_v1.json'))['rows']; b=json.load(open('/workspace/fertig-app/public/data.json'))['rows']
print('rows',len(a),len(b),'rankable',sum(r['rankable'] for r in a),sum(r['rankable'] for r in b))
def dist(L):
    v=[r['score'] for r in L if r.get('score') is not None]; q=st.quantiles(v,n=4)
    h=C.Counter(min(int(x//10)*10,90) for x in v); return len(v),round(st.mean(v),1),[round(x,1) for x in q],dict(sorted(h.items()))
for t,L in (('v1 all',a),('v2 all',b),('v1 rankable',[r for r in a if r['rankable']]),('v2 rankable',[r for r in b if r['rankable']])): print(t,dist(L))
for f in ('nutrition_basis','meal_class','nova_source','nova','veg_source','portion_source','stage'): print(f,dict(C.Counter(r.get(f) for r in b)))
top=sorted([r for r in b if r['pli'] is not None],key=lambda r:-r['pli'])[:50]
print('top50 non-meal/dry',[(r['name'],r['stage']) for r in top if r['stage'] not in('meal','stew') or r['dry']])
an={(r['name'],r['store']):r for r in a}
print('examples:')
for nm in ['nöm PRO','High Protein Pudding','Clever Lasagne','Stangl Suppe-ABC','Hühnersuppe','Good Choice','Chili con Carne','Linsen']:
    for r in b:
        if nm.lower() in r['name'].lower():
            o=an.get((r['name'],r['store']),{}); print(' ',r['name'][:45],'|',r['store'],'| v1',o.get('score'),'v2',r['score'],r['meal_class'],r['nutrition_basis'],'rank',r['rankable'],r['score_parts']);break
    else:
        o=next((y for y in a if nm.lower() in y['name'].lower()),None)
        if o: print(' ',o['name'][:45],'| v1',o['score'],'-> v2: removed (NONMEAL)')
for r in top[:10]: print('TOP',r['name'][:45],r['store'],r['score'],r['pli'],r['kcal_meal'])
