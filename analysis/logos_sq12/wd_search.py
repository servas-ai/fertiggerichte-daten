import json,urllib.request,urllib.parse,time,sys,concurrent.futures as cf
UA={'User-Agent':'servas-fertiggerichte/1.0 (https://github.com/servas-ai/fertiggerichte-daten; logo research)'}
def j(u):
  for i in range(3):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
    except Exception as e: time.sleep(2+i*3); err=e
  raise err
Q=[l.strip() for l in open('queries.txt') if l.strip()]
def run(q):
  out=[]
  for lang in ('de','en'):
    s=j('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode({'action':'wbsearchentities','search':q,'language':lang,'uselang':lang,'format':'json','limit':6}))
    for e in s.get('search',[]):
      if any(o['id']==e['id'] for o in out): continue
      out.append({'id':e['id'],'label':e.get('label'),'desc':e.get('description','')})
  ids='|'.join(o['id'] for o in out)
  if ids:
    ents=j('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode({'action':'wbgetentities','ids':ids,'props':'claims|sitelinks','format':'json'}))['entities']
    for o in out:
      c=ents[o['id']].get('claims',{})
      o['logo']=[x['mainsnak'].get('datavalue',{}).get('value') for x in c.get('P154',[])]
      o['web']=[x['mainsnak'].get('datavalue',{}).get('value') for x in c.get('P856',[])][:1]
      o['country']=[x['mainsnak'].get('datavalue',{}).get('value',{}).get('id') for x in c.get('P17',[])][:1]
  time.sleep(0.5)
  return q,out
res={}
with cf.ThreadPoolExecutor(4) as ex:
  for q,out in ex.map(run,Q): res[q]=out
json.dump(res,open('wd_search.json','w'),ensure_ascii=False,indent=1)
for q,out in res.items():
  print('##',q)
  for o in out:
    if o.get('logo'): print('  ',o['id'],o['label'],'|',o['desc'][:60],'|',o['logo'],o['web'])
