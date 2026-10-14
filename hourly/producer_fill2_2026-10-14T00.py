# hourly T00 (2026-10-14T00): second producer pass for T00 rows still without manufacturer
# (a) brand unanimity: >=5 labelled rows of the brand in scored+connectors_new and 100 % name the same Inverkehrbringer head -> most frequent full label string (evidence in manufacturer_source)
# (b) Allgroo: manufacturer/brand owner documented publicly — USPTO trademark ALLGROO reg. 6452668 owned by GMF Co., Ltd., Namwon-si, Jeollabuk-do (markinton.com/trademark/allgroo-90292890);
#     gmfkorea.com/ourstory.html + gmfkorea.tradekorea.com (GMF = manufacturer of 'Allgroo Vegetable gyoza mandu' 540 g; address 56-34 Simyo-gil, Namwon-si, Jeollabuk-do 55801)
import json,re,collections
F='connectors_new.json'; cn=json.load(open(F)); S=json.load(open('scored.json'))
RET=re.compile(r'(?i)^\s*(billa|spar|hofer|aldi|lidl|rewe|mpreis|verband|penny|merkur|gurkerl)')
head=lambda m:re.sub(r'\s+',' ',re.split(r'[,\n]',m)[0]).strip().lower().rstrip('.').replace(' gmbh','').replace(' ag','')
byB=collections.defaultdict(list)
for x in S+cn:
  m=(x.get('manufacturer') or '').strip(); b=re.sub(r'[^a-z0-9]','',(x.get('brand') or '').lower())
  if m and b and not RET.match(m): byB[b].append(m)
cnt=[]
for r in cn:
  if r.get('added_slot')!='2026-10-14T00' or r.get('manufacturer'): continue
  b=re.sub(r'[^a-z0-9]','',(r.get('brand') or '').lower()); ms=byB.get(b,[])
  if b=='allgroo':
    r['manufacturer']='GMF Co., Ltd. (Good Morning Foods), 56-34 Simyo-gil, Namwon-si, Jeollabuk-do 55801, Südkorea'
    r['manufacturer_source']='Markeninhaber laut USPTO-Marke ALLGROO Reg. 6452668 (GMF Co., Ltd.); Hersteller laut gmfkorea.com / gmfkorea.tradekorea.com (Allgroo Vegetable gyoza mandu 540 g) – 2026-10-14T00'
    cnt.append((r['name'],r['manufacturer'][:40])); continue
  if len(ms)>=5 and len({head(m) for m in ms})==1:
    full=[m for m,_ in collections.Counter(ms).most_common() if re.search(r'\d{4}',m)]
    if full:
      r['manufacturer']=full[0].replace('\n',', '); r['manufacturer_source']=f'Marken-Einstimmigkeit: alle {len(ms)} Etiketten der Marke {r["brand"]} im Datensatz nennen diesen Inverkehrbringer (2026-10-14T00)'
      cnt.append((r['name'],r['manufacturer'][:40]))
json.dump(cn,open(F,'w'),ensure_ascii=False,indent=1)
print(len(cnt),cnt); print('still none:',[r['name'] for r in cn if r.get('added_slot')=='2026-10-14T00' and not r.get('manufacturer')])
