import json,urllib.request,concurrent.futures as cf
items=[]
for f in ['../scored.json','../expand.json']:
  for x in json.load(open(f)):
    if x.get('store')=='BILLA': items.append(x)
urls=sorted({x['url'] for x in items if x.get('url')})
imgs=sorted({x['image_url'] for x in items if x.get('image_url')})
def g(u):
  d=u.rsplit('-',1)[1]; s=d[:2]+'-'+d[2:]
  for t in range(3):
    try:return u,json.load(urllib.request.urlopen(urllib.request.Request("https://shop.billa.at/api/product-discovery/products/"+s,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
    except urllib.error.HTTPError as e:
      if e.code==404:return u,{'_err':404}
    except Exception as e: err=str(e)
  return u,{'_err':err}
def h(u):
  try:
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30);b=r.read();return u,[r.status,r.headers.get('content-type'),len(b)]
  except Exception as e:return u,[getattr(e,'code',str(e)),None,0]
with cf.ThreadPoolExecutor(24) as ex:
  src=dict(ex.map(g,urls)); im=json.load(open('billa_img.json'))
json.dump(src,open('billa_src.json','w'),ensure_ascii=False);json.dump(im,open('billa_img.json','w'))
print(len(items),len(urls),len(imgs),sum('_err' in v for v in src.values()),sum(v[0]!=200 for v in im.values()))
