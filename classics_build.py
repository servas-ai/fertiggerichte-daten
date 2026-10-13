import json,re,urllib.request,urllib.parse,concurrent.futures as cf,hashlib,subprocess,os
from dishes import dish_key,LABEL
C=json.load(open('classics_cand.json'))
KEYS=list(json.load(open('expand.json'))[0].keys())
DENY=re.compile(r'saft\b|würzer|lasagneheber|stempel|hopfen|backmischung|topfenauflauf|cornichon|paprika-chili|mousse|spieße|filetschnitzel|mango curry|lasagneblae?tter|nudeln lasagne|romeo|adult|rettich|saatgut|sülz|oriental cook|port of spices|ciao mamma|veggie chunks|davert bio-thai|curry mittelscharf|mini-ravioli|cannelloni 24|cannelloni all|soja geschnetzeltes|per kg|berger|messner|greisinger|italfino|tann rinds-tafelspitz|grill|bolognese, 55|curry, 55|bowl pasta bolognese, 70|bertagni ragú|barilla bolognese|riso gallo|feiner|bratensaft|knorr feinschmecker|lachs - sahne gratin|eier|cappellacci|stekovics|bitery|tofutown|greenforce|my vay|planted chicken|ravioli 4 formaggi|ravioli tomate-ricotta|schmelzfüllung',re.I)
C=[c for c in C if not DENY.search(c['name']) and (c['src']=='billa' or (c.get('last') or '')>='2023-06')]
print(len(C))
def off(name):
  q=re.sub(r',?\s*\d+\s?(g|kg)\b.*','',name)
  u='https://world.openfoodfacts.org/cgi/search.pl?'+urllib.parse.urlencode(dict(search_terms=q,search_simple=1,json=1,page_size=5,fields='code,product_name,brands,nutriments,image_front_url,countries_tags,manufacturing_places'))
  try:
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'fertiggerichte-vergleich/1.0 (research)'}),timeout=30))
  except Exception as e: return None
  W=lambda s:set(re.findall(r'[a-zäöüß]{4,}',(s or '').lower()))
  qw=W(q)
  for p in d.get('products',[]):
    pw=W((p.get('product_name') or '')+' '+(p.get('brands') or ''))
    n=p.get('nutriments') or {}
    if qw and len(qw&pw)/len(qw)>=0.75 and n.get('proteins_100g') is not None and n.get('energy-kcal_100g'): return p
  return None
def g(c):
  a=str(c.get('amount') or '');u=(c.get('unit') or '').lower()
  try: v=float(a)
  except: v=None
  m=re.search(r'(\d{2,4})\s?g\b',c['name'])
  if m: return float(m.group(1))
  if v and u in('g',): return v
  if v and u=='kg': return v*1000
  return None
with cf.ThreadPoolExecutor(6) as ex: O=list(ex.map(lambda c:off(c['name']),C))
A=json.load(open('hourly/billa_all.json'))
STORE={'billa':'BILLA','spar':'SPAR','hofer':'HOFER','dm':'dm'}
out=[]
for c,o in zip(C,O):
  r={k:None for k in KEYS};sz=g(c);pr=c['price'];s=c['src']
  if s=='billa':
    b=A[c['sku']];url='https://shop.billa.at/produkte/'+b['slug'];img=(b.get('images') or [None])[0];ps='BILLA shop API 2026-10-13';pd='2026-10-13'
  elif s=='spar':
    url=f"https://www.interspar.at/p/{c['sku']}";img=f"https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/{c['sku']}/dt_main.jpg";pd=c['last']
  elif s=='hofer':
    url='https://www.hofer.at/de/'+(c.get('url') or '') if c.get('url') else None;img=None;pd=c['last']
  else:
    url=None;img=None;pd=c['last']
  if s!='billa': ps=f"heisse-preise.io {s} (Preisstand {pd})"+('' if pd>='2026-01-01' else ' – Altpreis, nicht live bestätigt')
  r.update(name=c['name'],brand=c['name'].split()[0] if s!='billa' else (A[c['sku']].get('brand') or {}).get('name'),store=STORE[s],price_eur=pr,size_g=sz,
    price_per_kg=round(pr/sz*1000,2) if sz else None,url=url,image_url=img or (o or {}).get('image_front_url'),price_source=ps,price_date=pd,category='Klassiker',dish_key=dish_key(c['name']))
  if 'fertigstufe' in KEYS or True: r['fertigstufe']='Komponente' if r['dish_key'] in('cevapcici','ripperl','backhendl') else 'Eintopf/Suppe' if re.search(r'suppe|eintopf|topf',c['name'],re.I) else 'Komplettmahlzeit'
  if o:
    n=o['nutriments']
    for k,ok in [('kcal_100','energy-kcal_100g'),('protein_100','proteins_100g'),('fat_100','fat_100g'),('satfat_100','saturated-fat_100g'),('carbs_100','carbohydrates_100g'),('sugar_100','sugars_100g'),('fiber_100','fiber_100g'),('salt_100','salt_100g')]: r[k]=n.get(ok)
    r['nut_source']='Open Food Facts '+o['code']; r['off_url']='https://world.openfoodfacts.org/product/'+o['code']
    r['nutriscore']=None
  if r['protein_100'] is not None and sz: r['protein_pack']=round(r['protein_100']*sz/100,1)
  if r['kcal_100'] is not None and sz: r['kcal_pack']=round(r['kcal_100']*sz/100)
  out.append(r)
# verify spar images
def chk(r):
  if not r['image_url'] or 'interspar' not in r['image_url']: return r
  p=subprocess.run(['curl','-s','-m','20','-A','Mozilla/5.0','-o','/tmp/ci','-w','%{http_code}',r['image_url']],capture_output=True,text=True).stdout
  b=open('/tmp/ci','rb').read() if os.path.exists('/tmp/ci') else b''
  if not(p=='200' and len(b)>3000 and hashlib.md5(b).hexdigest()!='4b6b5503e2ba4542bbc3cf2fbffd72bf'): r['image_url']=None
  return r
out=[chk(r) for r in out]
json.dump(out,open('classics_ext.json','w'),ensure_ascii=False,indent=1)
import collections
print(len(out),'nut',sum(r['protein_100'] is not None for r in out),'img',sum(bool(r['image_url']) for r in out))
print(collections.Counter(r['dish_key'] for r in out))
