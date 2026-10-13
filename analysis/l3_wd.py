import json,requests,concurrent.futures as cf
H={"User-Agent":"fertig-research/1.0 (logo research; contact martin)"}
B=json.load(open('l3_brands.json'))
def q(name):
  try:
    j=requests.get('https://www.wikidata.org/w/api.php',params=dict(action='wbsearchentities',search=name,language='de',uselang='de',format='json',limit=5),headers=H,timeout=20).json()
    ids=[x['id'] for x in j.get('search',[])]
    if not ids: return name,[]
    e=requests.get('https://www.wikidata.org/w/api.php',params=dict(action='wbgetentities',ids='|'.join(ids),props='claims|descriptions|labels',languages='de|en',format='json'),headers=H,timeout=20).json()['entities']
    out=[]
    for i in ids:
      c=e[i].get('claims',{})
      logo=[x['mainsnak'].get('datavalue',{}).get('value') for x in c.get('P154',[])]
      web=[x['mainsnak'].get('datavalue',{}).get('value') for x in c.get('P856',[])]
      ds=e[i].get('descriptions',{}); desc=(ds.get('de') or ds.get('en') or {}).get('value')
      lb=(e[i].get('labels',{}).get('de') or e[i].get('labels',{}).get('en') or {}).get('value')
      out.append(dict(id=i,label=lb,desc=desc,logo=logo,web=web))
    return name,out
  except Exception as ex: return name,[{'err':str(ex)}]
R=dict(cf.ThreadPoolExecutor(6).map(q,B))
json.dump(R,open('l3_wd.json','w'),indent=1,ensure_ascii=False)
for k,v in R.items():
  hits=[f"{x.get('id')}:{x.get('label')}|{(x.get('desc') or '')[:40]}|L={x.get('logo')}|W={x.get('web')[:1] if x.get('web') else ''}" for x in v if x.get('logo') or x.get('web')]
  print(k,'=>',hits[:2])
