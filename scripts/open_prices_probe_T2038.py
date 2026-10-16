import json,time,urllib.request
T=json.load(open('/tmp/op_targets.json'));res={}
for t in T:
  u=f"https://prices.openfoodfacts.org/api/v1/prices?product_code={t['ean']}&size=100&order_by=-date"
  for a in range(3):
    try:
      req=urllib.request.Request(u,headers={'User-Agent':'servas-food-connectors/1.0 (fertiggerichte research; contact via github servas-ai)'})
      res[t['ean']]=json.load(urllib.request.urlopen(req,timeout=30)); break
    except Exception as e:
      res[t['ean']]={'error':str(e)}; time.sleep(3)
  time.sleep(0.8)
json.dump(res,open('/tmp/op_res.json','w'))
print('done',sum(1 for v in res.values() if v.get('total')))
