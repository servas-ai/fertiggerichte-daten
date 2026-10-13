import json,re,sys,urllib.request,concurrent.futures as cf
sys.path.insert(0,'classics'); from dishes import dish,LABEL
src=open('ex.py').read().split('with cf.ThreadPoolExecutor(8)')[0]
src=src.replace("C=json.load(open('cand.json'));det=json.load(open('det.json'));det.update(json.load(open('det2.json')))","C=[];det={}")
exec(src)
h=json.load(open('hp_cur.json'))
sc=json.load(open('scored.json'))
norm=lambda s:re.sub(r'\W+',' ',(s or '').lower()).strip()
st=lambda s:'billa' if 'billa' in (s or '').lower() else 'spar' if 'spar' in (s or '').lower() else (s or '').lower()
seen={(st(x['store']),norm(x['name'])) for x in sc}
raw={(x['store'],x['name'].strip().lower()):x.get('id') for x in json.load(open('heisse_preise_raw.json')) if x['store'] in('billa','spar')}
X=re.compile(r'(?<!rinds)(?<!rinder)roulade(?!.*(rind|kraut))|biskuit|risotto\s?-?reis|risottoreis|reis\s(arborio|lose|selezione)|risotto reis|sugo|monat|gläschen|hipp|biokids|sandwich|bratensaft|seasoning|mix\b|blätter|argeta|ciao mamma|geschnetzelt$|rindfleisch geschnetzelt|puten geschnetzeltes|schweinsbraten vom karree|^berger|^messner|trüffel|tafelspitz$|hintere stelze|frikadellen klassisch',re.I)
C=[]
for x in h:
  if x['store'] not in('billa','spar'): continue
  k=dish(x['name'])
  if not k or X.search(x['name']): continue
  if (x['store'],norm(x['name'])) in seen: continue
  d=(x.get('priceHistory') or [{}])[0].get('date','')
  q=x.get('quantity');u=x.get('unit')
  m=re.search(r'(\d{8})$',x.get('url') or '')
  sid=('00-'+m.group(1)[2:]) if x['store']=='billa' and m else None
  sid=raw.get((x['store'],x['name'].strip().lower())) or sid
  C.append(dict(name=x['name'].strip(),store=x['store'],price_eur=x['price'],qty=q,unit=u,price_per_kg=round(x['price']/q*1000,2) if q and u in('g','ml') else None,bio=x.get('bio'),last_price_change=d,price_source='heisse-preise.io latest-canonical 2026-10-12',id=sid,url=x.get('url'),dish_key=k))
print(len(C)); json.dump(C,open('classics/cand.json','w'),ensure_ascii=False)

D=dict(det)
def fb(c):
  try:return c['id'],json.load(urllib.request.urlopen(urllib.request.Request("https://shop.billa.at/api/product-discovery/products/"+c['id'],headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
  except Exception as e:return c['id'],None
with cf.ThreadPoolExecutor(6) as e:
  for i,r in e.map(fb,[c for c in C if c['store']=='billa' and c['id']]): det[i]=r
print('billa det',sum(1 for v in det.values() if v))
def spimg(i):
  u=f"https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/{i}/dt_main.jpg"
  try:
    r=urllib.request.urlopen(urllib.request.Request(u,method='HEAD',headers={'User-Agent':'Mozilla/5.0'}),timeout=20); return u if r.status==200 and 'image' in r.headers.get('Content-Type','') else None
  except Exception: return None
def w2(c):
  r=work(c); r['dish_key']=c['dish_key']; r['dish']=LABEL[c['dish_key']]
  if c['store']=='spar' and c['id']:
    r['url']=f"https://www.interspar.at/shop/lebensmittel/p/{c['id']}"
    r['image_url']=spimg(c['id']) or r.get('image_url')
  if c['store']=='billa' and not r.get('url') and c.get('url'): r['url']='https://shop.billa.at/produkte/'+c['url']
  r['source_url']=r.get('url'); r['source_file']='classics.json'
  return r
with cf.ThreadPoolExecutor(8) as e: out=list(e.map(w2,C))
json.dump(out,open('classics.json','w'),ensure_ascii=False,indent=1)
import collections
print(len(out),'img',sum(1 for o in out if o.get('image_url')),'prot',sum(1 for o in out if o.get('protein_100') is not None))
