# hourly T03: SPAR twin matching using the interspar URL slug (carries the product line, e.g. 'dr-oetker-ristorante-pizza-salami')
# identical = same brand AND token set of slug (minus brand / pack words) == token set of other-store name AND pack size within 3 %; twins' kcal must agree within 3 %.
import json,re,collections
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
def nb(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())
UML={'ae':'ä','oe':'ö','ue':'ü'}
STOP={'g','kg','ml','l','stk','stück','stueck','portionen','portion','tiefgekühlt','tiefgekuehlt','tk','gefroren','x','dose','packung','er','mit','und','in','der','die','das','im','a','la','à','2','3','4','6','8','9','1','msc','pizza'}
def norm(w):
  w=w.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
  return w
def toks(text,brand):
  t=(text or '').lower().replace('´',"'").replace('’',"'")
  t=re.sub(r'\(.*?\)',' ',t); t=re.sub(r'\d+(?:[.,]\d+)?\s*(g|kg|ml|l|stück|stk)\b',' ',t)
  w=[norm(x) for x in re.findall(r"[a-zäöüß]+",t)]
  bw={norm(x) for x in re.findall(r"[a-zäöüß]+",(brand or '').lower())}|{'dr','oetker'}
  return frozenset(x for x in w if x not in STOP and x not in bw and len(x)>1)
idx=collections.defaultdict(list)
for x in S:
  if x.get('kcal_100') and x.get('size_g') and 'spar' not in str(x.get('store')).lower():
    idx[nb(x.get('brand')).replace('drOetker','droetker')].append(x)
d=json.load(open('/tmp/h03/spar_new.json'))
out=[]
for p in d:
  b=nb(p.get('brand')); g=p.get('size_g')
  if not b or not g or (p.get('extra') or {}).get('stock_status')!='inStock': continue
  slug=(p.get('source_url') or '').split('/')[-3] if '/p/' in (p.get('source_url') or '') else ''
  T=toks(slug.replace('-',' '),p.get('brand'))
  if not T: continue
  m=[x for x in idx.get(b,[]) if toks(x['name'],x.get('brand'))==T and abs(float(x['size_g'])-g)<=0.03*g]
  if m: out.append((p,m,slug))
for p,m,slug in out:
  ks=sorted({float(x['kcal_100']) for x in m})
  print(p['source_id'],'|',slug,'|',p['price_eur'],p['size_g'],'||',ks,[(x['store'],x['name'][:45],x.get('ean')) for x in m][:3])
json.dump([dict(spar=p,twins=m,slug=slug) for p,m,slug in out],open('/tmp/h03/spar_twins.json','w'),ensure_ascii=False,default=str)
print(len(out))
