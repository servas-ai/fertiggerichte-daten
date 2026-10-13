import json,re,urllib.request,concurrent.futures as cf
H={'User-Agent':'Mozilla/5.0'}
def J(u):return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
A=json.load(open('hourly/billa_all.json'));S=json.load(open('scored.json'))
txt=open('scored.json').read()+open('expand.json').read()+open('expand_unfiltered.json').read()+open('more_meals_norm.json').read()
seen={s.lstrip('0') for s in re.findall(r'-00?(\d{5,7})"',txt)}
names={re.sub(r'[^a-z0-9]','',(p.get('name') or '').lower()) for p in S}
KEEP=re.compile(r'Tiefkühlgerichte > (Asia|Fisch & Fleisch|Gemüse & Käsegerichte|Reis & Pasta)|Fertiggerichte ungekühlt > Gerichte > Dose|Fertiggerichte ungekühlt > Gerichte > Beutel|Fertiggerichte ungekühlt > Suppen|Menüschalen|Fertiggerichte Ungekühlt|Fertiggerichte gekühlt > Suppen')
cand={}
for s,r in A.items():
  path=' > '.join(x['name'] for x in (r.get('parentCategories') or [[]])[0])
  if not KEEP.search(path):continue
  if r['slug'].split('-')[-1].lstrip('0') in seen or re.sub(r'[^a-z0-9]','',r['name'].lower()) in names:continue
  r['_path']=path;cand[s]=r
print(len(cand))
def f(s):
  for i in range(3):
    try:return s,J("https://shop.billa.at/api/product-discovery/products/"+s)
    except Exception as e:err=e
  return s,None
det={}
with cf.ThreadPoolExecutor(8) as ex:
  for s,v in ex.map(f,cand):det[s]=v
json.dump({'cand':cand,'det':det},open('hourly/b_det.json','w'),ensure_ascii=False)
for s,r in cand.items():print(s,'|',r['name'],'|',r['_path'].split(' > ')[-1],'|',r['price']['regular']['value']/100,'|',r.get('amount'),r.get('volumeLabelShort'),'| det' if det[s] else '| NODET')
