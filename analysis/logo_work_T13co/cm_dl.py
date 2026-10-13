import json,urllib.request,urllib.parse,time,os
UA={'User-Agent':'servas-fertiggerichte/1.0 (https://github.com/servas-ai/fertiggerichte-daten; logo research)'}
F={'rewe-group':'REWE GROUP Logo 10-2026–.svg','rewe-group2':'Rewe-group.svg','mars':'Mars Incorporated 2019 logo.svg'}
meta={}
for s,f in F.items():
  t='File:'+f
  q=json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','titles':t,'prop':'imageinfo','iiprop':'url|size|mime|extmetadata','format':'json'}),headers=UA),timeout=30))
  pg=next(iter(q['query']['pages'].values())); ii=pg['imageinfo'][0]; em=ii.get('extmetadata',{})
  ext=f.rsplit('.',1)[-1].lower(); fn=f'cand/cm_{s}.{ext}'
  open(fn,'wb').write(urllib.request.urlopen(urllib.request.Request(ii['url'],headers=UA),timeout=60).read())
  meta[s]={'file':fn,'url':ii['url'],'page':'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(t.replace(' ','_')),'size':[ii.get('width'),ii.get('height')],'license':em.get('LicenseShortName',{}).get('value'),'artist':em.get('Artist',{}).get('value','')[:80]}
  print(s,meta[s]['license'],meta[s]['size']); time.sleep(0.7)
json.dump(meta,open('cm_meta.json','w'),indent=1)
