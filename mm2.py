import json,urllib.request,re,glob,concurrent.futures as cf
H={'User-Agent':'Mozilla/5.0'}
def J(u):return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
src=open('ex.py').read();exec(src[src.index('NM='):src.index('KEYS=')]);exec(src[src.index('def billa'):src.index('W=lambda')])
cats='menueschalen-15395 fertiggerichte-gekuehlt-15390 fertiggerichte-ungekuehlt-15391 fertiggerichte-gekuehlt-15232 fertiggerichte-ungekuehlt-15233 gerichte-15401 dose-15403 dose-15405 tiefkuehlgerichte-15474 tiefkuehlgerichte-15492 internationale-kueche-15129 asia-15494 gemuese-und-kaesegerichte-15497 sandwiches-und-co-15392 suppen-15394 suppen-15400 schnell-und-rein-pflanzlich-15231 reis-und-pasta-15496'.split()
cand={}
for c in cats:
  for p in range(6):
    try:d=J(f"https://shop.billa.at/api/product-discovery/categories/{c}/products?page={p}&pageSize=100")
    except Exception as e:print(c,e);break
    for r in d.get('results',[]):r['_cat']=c;cand[r['sku']]=r
    if len(d.get('results',[]))<100:break
print('cand',len(cand))
seen=set()
for f in glob.glob('*.json'):
  if f.startswith('mm'):continue
  t=open(f).read();seen|=set(re.findall(r'00-?(\d{6})',t))
new=[s for s in cand if s.replace('00-','') not in seen]
print('new',len(new))
def f(s):
  try:return s,J("https://shop.billa.at/api/product-discovery/products/"+s)
  except:return s,None
det={}
with cf.ThreadPoolExecutor(8) as ex:
  for s,r in ex.map(f,new):det[s]=r
json.dump({'cand':cand,'det':det},open('mm_raw.json','w'),ensure_ascii=False)
