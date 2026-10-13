import json,re,collections
A=json.load(open('/workspace/fertig-app/public/data.json'));R=A['rows']
prev=2356+0
new={x['name'] for x in json.load(open('hourly/added_2026-10-13T04.json'))['added']}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
def chk(rows):
  c=collections.Counter((r['store'],k(r['name']),r.get('size')) for r in rows)
  return dict(n=len(rows),nonfood=sum(1 for r in rows if r.get('nonfood')),nonfood_ranked=sum(1 for r in rows if r.get('nonfood') and r.get('rankable')),
   raw_in_rank=[r['name'] for r in rows if r.get('rankable') and r.get('stage') not in ('meal','stew','dessert','soup',None) and r['stage']=='raw'],
   ppk_out=[(r['name'],r['ppk']) for r in rows if r.get('ppk') and not (1<=r['ppk']<=120)],
   kcal_out=[(r['name'],r['kcal']) for r in rows if r.get('kcal') is not None and not (15<=r['kcal']<=600)],
   dups=sum(v-1 for v in c.values() if v>1))
mine=[r for r in R if r['name'] in new and r['store'] in ('Gurkerl','Gurkerl.at')]
out=dict(mine=chk(mine),all=chk(R),stages=collections.Counter(r['stage'] for r in mine))
out['count_before_scored']=2356; out['count_rows_app']=len(R)
json.dump(out,open('hourly/qa_gate_04_data.json','w'),ensure_ascii=False,indent=1,default=str)
print(json.dumps(out['mine'],ensure_ascii=False,default=str)); print('all n',out['all']['n'],'nonfood_ranked',out['all']['nonfood_ranked'],'dups',out['all']['dups'],'stages',out['stages'])
