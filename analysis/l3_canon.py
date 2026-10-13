import json,re,collections
d=json.load(open('/workspace/fertig-app/dist/data.json'))
def slug(s):
  s=s.lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('í','i')
  return re.sub(r'[^a-z0-9]+','-',s).strip('-')
ALIAS={'fit2go.meals (Fit2go GmbH)':'Fit to Go','Good Choice (Hofer Eigenmarke)':'Good Choice','GOOD CHOICE':'Good Choice','PRIMANA':'Primana','Iglo':'iglo','Maggi, Nestlé':'Maggi','BILLA':'Billa','BILLA immer gut':'BILLA Immer Gut','Simply good':'Simply Good','Spar Veggie':'SPAR Veggie','Spar Premium':'SPAR PREMIUM','Spar':'SPAR','Original Greisinger':'Greisinger','CHEF SELECT':'Chef Select','Leibspeis':"Leibspeis'","Uncle Ben's":"Ben's Original",'Uncle Bens':"Ben's Original",'inzersdorfer':'Inzersdorfer','Omis':'Omis Schmankerl','Knorr, Kaiser Teller':'Knorr','Knorr Kaiser Teller':'Knorr','Clever':'CLEVER','DM':'dm','Gourmet':'GMS Gourmet','GOURMET FINEST CUISINE':'GMS Gourmet','Lidl, Trattoria Alfredo':'Trattoria Alfredo','Aldi, Wonnemeyer Feinkost, Kühlmann':'Wonnemeyer','Cucina, Girone & Sohn Nahrungsmittel':'Cucina','Aldi, Natur Aktiv':'Natur Aktiv','Food for Future, Penny':'Food for Future'}
B=collections.Counter()
for r in d['rows']:
  b=(r.get('brand') or '').strip()
  if b: B[ALIAS.get(b,b)]+=1
for s in ['Billa','Spar','Hofer','Lidl','Penny','dm','Fit to Go']: B[s]+=0
json.dump({k:{'slug':slug(k),'n':v} for k,v in B.items()},open('l3_brands.json','w'),indent=1,ensure_ascii=False)
print(len(B))
