# hourly T22: producer/manufacturer fill for T23 rows lacking a manufacturer (rows of other workers untouched)
# 1) EAN twin: another row (any store) with the identical EAN carries a label manufacturer (BILLA/Gurkerl/MPreis Pflichtangaben) -> copy
# 2) Brand consensus: >=8 labelled rows of the brand in scored+connectors_new and >=95 % name the same Inverkehrbringer (company head) -> most frequent full label string with postcode
# Retailer names (BILLA/SPAR/HOFER/Lidl/REWE/MPREIS/Verband) are never propagated. Evidence in manufacturer_source.
import json,re,collections
F='/workspace/fertig/connectors_new.json'; cn=json.load(open(F)); S=json.load(open('/workspace/fertig/scored.json'))
RET=re.compile(r'(?i)^\s*(billa|spar|hofer|aldi|lidl|rewe|mpreis|verband|penny|merkur|gurkerl)')
head=lambda m:re.sub(r'\s+',' ',re.split(r'[,\n]',m)[0]).strip().lower().rstrip('.').replace(' gmbh','').replace(' ag','')
byE=collections.defaultdict(collections.Counter)
for x in S+cn:
  m=(x.get('manufacturer') or '').strip()
  if x.get('ean') and m and not RET.match(m): byE[str(x['ean']).lstrip('0')][m]+=1
byB=collections.defaultdict(list)
for x in S+cn:
  m=(x.get('manufacturer') or '').strip(); b=(x.get('brand') or '').strip().lower()
  if m and b and not RET.match(m): byB[b].append(m)
CONS={}
for b,ms in byB.items():
  if len(ms)<8: continue
  h=collections.Counter(head(m) for m in ms); top,n=h.most_common(1)[0]
  if n/len(ms)<0.95: continue
  full=[m for m,_ in collections.Counter(ms).most_common() if head(m)==top and re.search(r'\d{4}',m)]
  if full: CONS[b]=(full[0].replace('\n',', '),n,len(ms))
MINE={r['url'] for r in json.load(open('/workspace/fertig/hourly/added_2026-10-13T23.json'))['added']}  # only rows added by this hourly run
cnt=collections.Counter(); ex=[]
for r in cn:
  if r.get('manufacturer') or r.get('url') not in MINE: continue
  e=str(r.get('ean') or '').lstrip('0'); b=(r.get('brand') or '').strip().lower()
  if e and byE.get(e):
    r['manufacturer']=byE[e].most_common(1)[0][0].replace('\n',', '); r['manufacturer_source']=f'EAN-Zwilling {e}: Etikett-Herstellerangabe einer anderen Zeile/Kette im Datensatz (2026-10-13T23)'; cnt['ean_twin']+=1; ex.append((r['store'],r['name'],r['manufacturer'][:50]))
  elif b in CONS:
    m,n,t=CONS[b]; r['manufacturer']=m; r['manufacturer_source']=f'Marken-Konsens: {n}/{t} Etiketten der Marke {r["brand"]} im Datensatz nennen diesen Inverkehrbringer (2026-10-13T23)'; cnt['brand_consensus']+=1; ex.append((r['store'],r['name'],m[:50]))
json.dump(cn,open(F,'w'),ensure_ascii=False,indent=1)
print(dict(cnt),'| T21 still without manufacturer:',[r['name'] for r in cn if r.get('added_slot')=='2026-10-13T23' and not r.get('manufacturer')])

for x in ex[:25]: print(' ',x)
