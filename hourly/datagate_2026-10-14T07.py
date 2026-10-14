# hourly T07 data gate
import json,re,collections,os
A=json.load(open('/workspace/fertig-app/public/data.json'));R=A['rows']
BEFORE=3542
add=json.load(open('hourly/added_2026-10-14T07.json'))['added']; urls={x['url'] for x in add}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
NONMEALRAW=re.compile(r'\b(mehl|zucker|reis roh|teig|fond|würfel|bouillon|gewürz|öl)\b',re.I)
def chk(rows):
  c=collections.Counter((r['store'],k(r['name']),r.get('size')) for r in rows)
  return dict(n=len(rows),nonfood=sum(1 for r in rows if r.get('nonfood')),nonfood_ranked=sum(1 for r in rows if r.get('nonfood') and r.get('rankable')),
   raw_in_meal_rank=[r['name'] for r in rows if r.get('rankable') and r.get('stage') in ('meal','stew') and NONMEALRAW.search(r['name'])],
   ppk_out=[(r['name'],r['ppk']) for r in rows if r.get('ppk') and not (1<=r['ppk']<=120)],
   kcal_out=[(r['name'],r['kcal']) for r in rows if r.get('kcal') is not None and not ((5 if re.search(r'suppe|brühe',r['name'],re.I) else 15)<=r['kcal']<=600)],
   p100_gt_kcal=[(r['name'],r['p100'],r['kcal']) for r in rows if r.get('p100') and r.get('kcal') and r['p100']*4>r['kcal']*1.05],
   price_out=[(r['name'],r['price']) for r in rows if r.get('price') is not None and not (0.3<=r['price']<=60)],
   dups=sum(v-1 for v in c.values() if v>1),dup_keys=[k_ for k_,v in c.items() if v>1][:10])
mine=[r for r in R if r['url'] in urls]
out=dict(mine=chk(mine),all=chk(R),stages_new=collections.Counter(r['stage'] for r in mine),stores_new=collections.Counter(r['store'] for r in mine))
out['rows_before']=BEFORE; out['rows_after']=len(R); out['drop_pct']=round((BEFORE-len(R))/BEFORE*100,2)
out['iss_mich']=sum(1 for r in R if r.get('store')=='iss mich!')
out['alfies']=sum(1 for r in R if r.get('store')=='Alfies')
m=out['mine']; out['PASS']=bool(m['nonfood']==0 and not m['raw_in_meal_rank'] and not m['ppk_out'] and not m['kcal_out'] and not m['p100_gt_kcal'] and not m['price_out'] and m['dups']==0 and out['all']['nonfood_ranked']==0 and len(R)>=BEFORE*0.98)
json.dump(out,open('hourly/qa_gate_2026-10-14T07_data.json','w'),ensure_ascii=False,indent=1,default=str)
print(json.dumps(out['mine'],ensure_ascii=False,default=str)[:2000]); print('ALL',{x:(out['all'][x] if isinstance(out['all'][x],int) else len(out['all'][x])) for x in out['all'] if x!='dup_keys'}, out['all']['dup_keys'][:5]); print('stages',dict(out['stages_new']),'stores',dict(out['stores_new']),'rows',BEFORE,'->',len(R),'iss',out['iss_mich'],'alfies',out['alfies'],'PASS',out['PASS'])
E=json.load(open('/workspace/fertig-app/public/embeddings.json'))
print('embed ids',len(E['ids']),'rows',len(R),'match',E['ids']==[r['id'] for r in R])
for r in mine:
  print('  T07',r['store'],'|',r['name'][:55],'|',r['stage'],r.get('gang'),'|',r.get('pack'),'| rankable',r['rankable'],'| kcal',r['kcal'],'| img',bool(r.get('img')))
