import json,urllib.request,urllib.parse,time,concurrent.futures as cf
UA={'User-Agent':'servas-fertiggerichte/1.0 (https://github.com/servas-ai/fertiggerichte-daten; logo research)'}
def j(u):
  for i in range(3):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
    except Exception as e: time.sleep(2+i*3); err=e
  raise err
Q=[l.strip() for l in open('cm_queries.txt') if l.strip()]
def run(q):
  s=j('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','list':'search','srsearch':q+' logo','srnamespace':6,'srlimit':8,'format':'json'}))
  time.sleep(0.4)
  return q,[h['title'] for h in s['query']['search']]
res={}
with cf.ThreadPoolExecutor(4) as ex:
  for q,t in ex.map(run,Q): res[q]=t; print('##',q,'|',' ; '.join(t))
json.dump(res,open('cm_search.json','w'),ensure_ascii=False,indent=1)
