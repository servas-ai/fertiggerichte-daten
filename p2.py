import re,json,glob
codes={}
for f in sorted(glob.glob('ovis/*.txt')):
  L=open(f).read().split('\n'); i=0
  starts=[i for i,l in enumerate(L) if re.match(r'\s*AT \d{4,5} E[UG]\b',l)]
  for j,s in enumerate(starts):
    e=starts[j+1] if j+1<len(starts) else min(s+6,len(L))
    blk=L[s:min(e,s+6)]
    m=re.match(r'\s*AT (\d{4,5}) E[UG]\s+(\S+)\s+(.*)',blk[0])
    num,vis,rest=m.groups()
    parts=re.split(r'\s{2,}',rest.strip())
    name=parts[0]; street=parts[1] if len(parts)>1 else ''
    town='';pc=''
    for l in blk[1:]:
      mm=re.search(r'\b(\d{4}) ([A-ZÄÖÜa-zäöüß][^\s].*?)(\s{2,}|$)',l)
      if mm and not town: pc,town=mm.group(1),mm.group(2).strip()
      elif not town:
        seg=l.strip()
        if seg and len(re.split(r'\s{2,}',seg))>=1 and l.find(seg)<60: name+=' '+re.split(r'\s{2,}',seg)[0]
    if num not in codes: codes[num]={'code':f'AT {num} EU','company':name,'street':street,'postcode':pc,'town':town,'list':f.split('/')[-1][:-4]}
def state(pc):
  if not pc: return None
  p=int(pc)
  if p<2000: return 'Wien'
  if 2400<=p<2500 and p>=2410 and p in range(2421,2492): return 'Burgenland'
  if p<4000: return 'Niederösterreich'
  if p<5000: return 'Oberösterreich'
  if 5230<=p<=5290 or 5310<=p<=5360: return 'Oberösterreich'
  if p<6000: return 'Salzburg'
  if p>=6700 and p<7000: return 'Vorarlberg'
  if p<7000: return 'Tirol'
  if p<8000: return 'Burgenland'
  if p<9000: return 'Steiermark'
  return 'Kärnten'
for c in codes.values(): c['state']=state(c['postcode'])
json.dump(codes,open('ovis_codes.json','w'),ensure_ascii=False,indent=0)
print(len(codes))
for k in ['32629','32522','30733','31538','20271','61904','31353','41586','62028','40698','92526','42152']: print(codes.get(k))
