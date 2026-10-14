# hourly T03 (2026-10-14T03, copy of T21/T00 twin_spar): match new SPAR search hits to identical products already in the dataset (other chains) to borrow label nutrition/EAN/producer.
# identical = same brand (normalized) AND same product words (name minus brand/pack noise, token-set equal) AND pack size within 3 %.
import json,re,sys,collections
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
def nb(s): return re.sub(r'[^a-z0-9]','',(s or '').lower().replace('’',"'").replace('´',"'"))
STOP={'g','kg','ml','l','stk','stück','portionen','portion','port','tiefgekühlt','tk','gefroren','x','dose','packung','er','mit','und','in','der','die','das','im','&','-','2','4','1'}
def toks(name,brand):
  t=(name or '').lower().replace('´',"'").replace('’',"'")
  for b in filter(None,[brand]): t=t.replace(b.lower(),' ')
  t=re.sub(r'\(.*?\)',' ',t); t=re.sub(r'\d+(?:[.,]\d+)?\s*(g|kg|ml|l)\b',' ',t)
  w=[x for x in re.findall(r'[a-zäöüß]+',t) if x not in STOP and len(x)>1]
  return frozenset(w)
idx=collections.defaultdict(list)
for x in S:
  if x.get('kcal_100') and x.get('size_g') and 'spar' not in str(x.get('store')).lower():
    idx[nb(x.get('brand'))].append(x)
d=json.load(open('/tmp/h03/spar_new.json'))
out=[]
for p in d:
  b=nb(p.get('brand')); g=p.get('size_g')
  if not b or not g: continue
  T=toks(p['name'],p.get('brand'))
  m=[x for x in idx.get(b,[]) if toks(x['name'],x.get('brand'))==T and abs(float(x['size_g'])-g)<=0.03*g]
  if m: out.append((p,m))
for p,m in out:
  print(p['source_id'],'|',p['name'][:55],'|',p['price_eur'],p['size_g'],'|',p['extra'].get('stock_status'),'||',[(x['store'],x['name'][:40],x.get('kcal_100'),x.get('ean')) for x in m][:3])
json.dump([dict(spar=p,twins=m) for p,m in out],open('/tmp/h03/spar_twins_tok.json','w'),ensure_ascii=False,default=str)
print(len(out))
