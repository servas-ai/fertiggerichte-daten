import json,re,os,shutil,urllib.request,concurrent.futures as cf
os.chdir('/workspace/fertig')
new=json.load(open('hourly/added_2026-10-13T02.json'))
CO=json.load(open('hourly/enrich_comp_2026-10-13T02.json')); OFF=json.load(open('hourly/enrich_off_2026-10-13T02.json'))
mm0=json.load(open('hourly/../more_meals.json'))
D='2026-10-13'; NK=['kcal','protein','fat','satfat','carbs','sugar','fiber','salt']
F={'kcal':'energy-kcal_100g','protein':'proteins_100g','fat':'fat_100g','satfat':'saturated-fat_100g','carbs':'carbohydrates_100g','sugar':'sugars_100g','fiber':'fiber_100g','salt':'salt_100g'}
def consistent(n):
  k=n.get('kcal');f,p,c=n.get('fat'),n.get('protein'),n.get('carbs')
  if k is None or not (20<=k<=600): return False
  if None in (f,p,c): return True
  if c>100 or f>100 or p>100 or (n.get('sugar') or 0)>c+0.5 or (n.get('satfat') or 0)>f+0.5: return False
  calc=9*f+4*p+4*c+2*(n.get('fiber') or 0)
  return abs(calc-k)<=max(25,0.25*k)
def setnut(r,n,src):
  for k in NK: r[k+'_100']=None if n.get(k) is None else round(float(n[k]),2)
  r['nut_source']=src
  g=r.get('size_g')
  r['protein_pack']=round(r['protein_100']*g/100,1) if g and r['protein_100'] is not None else None
  r['kcal_pack']=round(r['kcal_100']*g/100) if g and r['kcal_100'] is not None else None
  if 'protein_per_eur' in r: r['protein_per_eur']=round(r['protein_pack']/r['price_eur'],1) if r.get('protein_pack') and r.get('price_eur') else None
def clearnut(r,why):
  for k in NK: r[k+'_100']=None
  r['protein_pack']=r['kcal_pack']=r['protein_per_eur']=None; r['nut_source']=None; r['nut_note']=why
cnt=dict(nut_filled=0,ean_filled=0,pid_filled=0,manuf_filled=0,img_filled=0,nut_rejected=0)
def offnut(o):
  n=(o or {}).get('nutriments') or {}
  return {k:n.get(v) for k,v in F.items() if n.get(v) is not None}
def emb(o):
  e=(o or {}).get('emb_codes'); e=', '.join(e) if isinstance(e,list) else e
  return e or None
fills={}
for r,c in zip(mm0+new,CO):
  isnew=r in new
  f={}
  if c:
    n,ing,prod,pid,ean=c
    if ean and not r.get('ean'): f['ean']=ean
    if prod and not r.get('manufacturer'): f['manufacturer']=prod
    if pid and not r.get('producer_id'): f['producer_id']=pid
    if r.get('kcal_100') is None and n and consistent(n): f['_nut']=(n,f'Gurkerl.at API (composition) {D}')
  e=str(r.get('ean') or f.get('ean') or '')
  o=OFF.get(e) if e else None
  if o:
    if r.get('kcal_100') is None and '_nut' not in f:
      on=offnut(o)
      if on and consistent(on): f['_nut']=(on,f'Open Food Facts {e} (EAN match) {D}')
    em=emb(o)
    if em and not r.get('producer_id') and 'producer_id' not in f: f['producer_id']=em
    if not r.get('image_url') and o.get('image_front_url'): f['image_url']=o['image_front_url']
  fills[(r['name'],r['store'],r.get('size_g'))]=f
# new rows: validate nutrition from Gurkerl
for r in new:
  n={k:r.get(k+'_100') for k in NK if r.get(k+'_100') is not None}
  if n and not consistent(n): clearnut(r,'Gurkerl-Nährwerte inkonsistent (kcal≠Makros) – verworfen'); cnt['nut_rejected']+=1
def apply(r):
  f=fills.get((r['name'],r['store'],r.get('size_g'))) or {}
  for k,v in f.items():
    if k=='_nut':
      if r.get('kcal_100') is None: setnut(r,*v); cnt['nut_filled']+=1
    elif not r.get(k):
      r[k]=v; cnt[{'ean':'ean_filled','producer_id':'pid_filled','manufacturer':'manuf_filled','image_url':'img_filled'}[k]]+=1
for r in new: apply(r)
cn=dict(cnt); cnt.update({k:0 for k in cnt if k!='nut_rejected'})
# re-read latest file (concurrency) and apply fills to existing
mm=json.load(open('more_meals.json'))
for r in mm: apply(r)
ce=dict(cnt)
# verify images of new rows
def ok(u):
  try:
    q=urllib.request.Request(u,method='GET',headers={'User-Agent':'Mozilla/5.0','Range':'bytes=0-1023'})
    with urllib.request.urlopen(q,timeout=20) as x: return x.status in (200,206) and 'image' in x.headers.get('Content-Type','')
  except Exception: return False
with cf.ThreadPoolExecutor(10) as ex: OK=list(ex.map(lambda r: ok(r['image_url']) if r.get('image_url') else False,new))
for r,k in zip(new,OK):
  r['image_ok']=k
  if not k: r['image_url']=None
have={(x['name'],x['store'],x.get('size_g')) for x in mm}; haveE={str(x['ean']) for x in mm if x.get('ean')}
add=[r for r in new if (r['name'],r['store'],r.get('size_g')) not in have and not (r.get('ean') and r['ean'] in haveE)]
for r in add: r.pop('image_ok',None)
keys=list(mm[0].keys())
for r in add:
  for k in keys: r.setdefault(k,None)
shutil.copy('more_meals.json','hourly/more_meals.before_2026-10-13T02.json')
mm+=add
json.dump(mm,open('more_meals.json','w'),ensure_ascii=False,indent=1)
json.dump(mm,open('more_meals_norm.json','w'),ensure_ascii=False,indent=1)
json.dump(add,open('hourly/added_2026-10-13T02.json','w'),ensure_ascii=False,indent=1)
rep=dict(added=len(add),total_more_meals=len(mm),images_ok_new=sum(OK),new_counts=cn,existing_fills=ce)
json.dump(rep,open('hourly/enrich_report_2026-10-13T02.json','w'),indent=1)
print(rep)
