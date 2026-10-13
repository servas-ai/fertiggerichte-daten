import json,collections,re
o=json.load(open('_prod_tmp.json'))
LIG={'ﬀ':'ff','ﬂ':'fl','ﬁ':'fi'}
for r in o:
  for k,v in list(r.items()):
    if isinstance(v,str):
      for a,b in LIG.items(): v=v.replace(a,b)
      r[k]=v
  if r.get('note'): r['note']=re.sub(r' ?weitere Codes:.*$','',r['note']).strip() or None
  if r['plant_town'] and not r.get('plant_state') and r['confidence']=='label-address': pass
  r['store']=r['store'] or 'unbekannt (OFF)'
prof={}
for r in o:
  if not r['producer_company'] or r['confidence']=='unknown': continue
  key=r['producer_company']
  p=prof.setdefault(key,dict(company=key,owner_group=r.get('owner_group'),plant_codes=set(),towns=set(),states=set(),country=r['country'],products=[],retail_brands=set(),chains=set(),confidence_levels=set()))
  if r['plant_code']: p['plant_codes'].add(r['plant_code'])
  if r['plant_town']: p['towns'].add(r['plant_town'])
  if r['plant_state']: p['states'].add(r['plant_state'])
  p['products'].append(r['name']); p['chains'].add(str(r['store']).upper().replace('INTERSPAR/SPAR ONLINE','SPAR'))
  if r['brand']: p['retail_brands'].add(r['brand'])
  else:
    b=r['name'].split()[0]; p['retail_brands'].add(' '.join(r['name'].split()[:2]) if b.lower() in('omis','ja!','simply','billa','die') else b)
  p['confidence_levels'].add(r['confidence'])
P=[]
for p in prof.values():
  for k in ['plant_codes','towns','states','retail_brands','chains','confidence_levels']: p[k]=sorted(p[k])
  p['n_products']=len(p['products']); P.append(p)
P.sort(key=lambda p:(-('confirmed-code' in p['confidence_levels']),-p['n_products']))
cov=collections.Counter(r['confidence'] for r in o)
bystore=collections.defaultdict(collections.Counter)
for r in o:
  s=str(r['store']).upper()
  s='SPAR' if 'SPAR' in s else ('BILLA' if 'BILLA' in s else ('HOFER' if 'HOFER' in s or 'ALDI' in s else ('LIDL' if 'LIDL' in s else s)))
  bystore[s]['total']+=1; bystore[s][r['confidence']]+=1
coverage=dict(total_products=len(o),by_confidence=dict(cov),with_producer=sum(1 for r in o if r['confidence']!='unknown'),with_plant_code=sum(1 for r in o if r['plant_code']),with_meat_origin=sum(1 for r in o if r['meat_origin']),by_store={k:dict(v) for k,v in bystore.items()})
json.dump(dict(generated='2026-10-12',method=['BILLA Shop-API Pflichtangaben (mandatoryIndicator = Identitätskennzeichen, manufacturersAddress)','Open Food Facts emb_codes per EAN + Marken-Suche','Auflösung AT-Codes gegen VIS/ÖVIS-Liste (vis.statistik.at, Stand 12.10.2026)','DE/IT-Codes über das-ist-drin.de / supermarktcheck.de / blia.it','Web: VKI/AGES-Rückrufe, REWE-Presse'],confidence_legend={'confirmed-code':'Identitätskennzeichen auf Etikett, aufgelöst in amtlicher Liste (= Werk, das zuletzt verpackt/verarbeitet hat)','label-address':'Hersteller-/Inverkehrbringer-Adresse auf dem Etikett (Firmensitz, bei Markenware i.d.R. Markeninhaber; Werk nicht belegt)','recall/press':'Rückruf-/Presse-/Medienquelle','inferred':'nicht verwendet – keine Raten','unknown':'kein belastbarer Beleg gefunden'},coverage=coverage,products=o,producer_profiles=P),open('producers_v2.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(coverage,ensure_ascii=False,indent=1))
for p in P[:30]: print(p['n_products'],p['company'],p['plant_codes'],p['towns'],p['chains'],p['retail_brands'][:8])
