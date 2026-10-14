# hourly T03: fuzzy twin candidates (same brand, pack within 3 %, slug/name token Jaccard >= 0.5) for SPAR meal hits; printed for manual review
import json,re,collections
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
nb=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
def norm(w): return w.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
STOP={'g','kg','stk','stueck','portionen','portion','port','tiefgekuehlt','tk','gefroren','x','dose','packung','er','mit','und','in','der','die','das','im','a','la','msc','fangfrisch','blitzgefroren','vorteilspackung','kaeptn','iglo','tiefgefroren'}
def toks(t,brand):
  t=norm((t or '').lower()); t=re.sub(r'\(.*?\)',' ',t); t=re.sub(r'\d+(?:[.,]\d+)?\s*(g|kg|ml|l)\b',' ',t)
  bw={norm(x) for x in re.findall(r'[a-zäöüß]+',(brand or '').lower())}
  return {x for x in re.findall(r'[a-z]+',t) if x not in STOP and x not in bw and len(x)>2}
idx=collections.defaultdict(list)
for x in S:
  if x.get('kcal_100') and x.get('size_g') and 'spar' not in str(x.get('store')).lower(): idx[nb(x.get('brand'))].append(x)
M=re.compile(r'Fertiggerichte|Pizza, Baguette|Suppen|Schnelle Küche|Fleisch, Fisch|Mehlspeis|Menü|Süße Knödel|Strudel|Traditionelle',re.I)
BAD=re.compile(r'instant|cup|snack|suppenwürfel|fond|saucy|noodles|nudel snack|würfel|packerl|hochzeitssuppe|dressing|riegel|jogurt|salat|brot|eis|caramel|naturfilet|filets|garnelen|calamari tiefgek|schollenfilet|heilbutt|kabeljau 2|fries|rösti|baby|hipp|weinblätter',re.I)
d=json.load(open('/tmp/h03/spar_new.json')); out=[]
for p in d:
  c=p.get('category') or ''; g=p.get('size_g')
  if not (M.search(c) and p['extra'].get('stock_status')=='inStock' and g) or BAD.search(p['name']): continue
  slug=p['source_url'].split('/')[-3]
  T=toks(slug.replace('-',' '),p.get('brand'))|toks(p['name'],p.get('brand'))
  cands=[]
  for x in idx.get(nb(p.get('brand')),[]):
    if abs(float(x['size_g'])-g)>0.03*g: continue
    X=toks(x['name'],x.get('brand'))
    if not X: continue
    j=len(T&X)/len(T|X)
    if j>=0.4: cands.append((round(j,2),x))
  cands.sort(key=lambda t:-t[0])
  out.append(dict(spar=p,slug=slug,cands=[dict(j=j,x=x) for j,x in cands[:4]]))
  print(p['source_id'],'|',slug,'|',p['price_eur'],g)
  for j,x in cands[:4]: print('    ',j,x['store'],'|',x['name'],'|',x['size_g'],'|',x['kcal_100'],x.get('protein_100'),'|',x.get('ean'),'|',x.get('url'))
json.dump(out,open('/tmp/h03/spar_fuzzy.json','w'),ensure_ascii=False,default=str)
