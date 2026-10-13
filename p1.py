import json,re,collections
B={}
for f in ['det.json','det2.json']:
  for k,x in json.load(open(f)).items():
    if not x: continue
    r={'sku':k,'name':x.get('name'),'country':x.get('countryOfOrigin')}
    for m in ['meatBorn','meatRaised','meatSlaughtered','meatButchered']: r[m]=x.get(m) or ''
    for ai in x.get('additionalInformation') or []:
      pi=ai.get('productInformation') or {}
      r['mand']=pi.get('mandatoryIndicator'); r['maddr']=pi.get('manufacturersAddress')
      r['ingr']=(ai.get('foodInformation') or {}).get('ingredientsText')
    r['feat']=str(x.get('features'))[:0]
    B[k]=r
json.dump(B,open('billa_det_extract.json','w'),ensure_ascii=False)
c=collections.Counter(bool(r.get('mand')) for r in B.values());print(len(B),c)
print(collections.Counter(r.get('mand') for r in B.values()).most_common(60))
