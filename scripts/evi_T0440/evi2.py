import re,html,json,time,datetime,sys,urllib.request
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.polite import polite_urlopen
UA={'User-Agent':'servas-fertiggerichte-daten/1.0 (https://github.com/servas-ai/fertiggerichte-daten; data squad)'}
T={'hofer-kg':'600h','mars-austria-og':'213022v','kernbeisser-og':'622470y','recheis-teigwaren-gmbh':'47864p','wech-gefluegel-gmbh':'118996w'}
def dd(t,label):
    m=re.search(r'<dt[^>]*>'+re.escape(label)+r'</dt><dd[^>]*>(.*?)</dd>',t,re.S)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',m.group(1)))).strip() if m else None
out={}
for s,fn in T.items():
    u=f'https://www.evi.gv.at/f/{fn}'
    t=polite_urlopen(urllib.request.Request(u,headers=UA),timeout=40).read().decode('utf-8','replace')
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',t,re.S)
    secs={}
    for m in re.finditer(r'<h3 class="text-base font-semibold">([^<]+)</h3><p class="text-sm text-gray-600">([^<]*)</p>.*?<ul[^>]*>(.*?)</ul></details>',t,re.S):
        items=[]
        for li in re.findall(r'<li[^>]*>(.*?)</li>',m.group(3),re.S):
            a=re.search(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',li,re.S)
            pn=re.search(r'<p class="text-lg[^"]*">(.*?)</p>',li,re.S)
            nm=a.group(2) if a else (pn.group(1) if pn else '')
            ein=re.search(r'Eingetragen am ([0-9.]+)',li)
            items.append({'href':a.group(1) if a else None,'name':html.unescape(re.sub(r'<[^>]+>','',nm)).strip(),'eingetragen':ein.group(1) if ein else None})
        secs[html.unescape(m.group(1))]={'count':m.group(2),'items':items}
    out[s]={'url':u,'fetched_at':datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),'name':html.unescape(re.sub(r'<[^>]+>','',h1.group(1))).strip() if h1 else None,
      'status':dd(t,'Status'),'eintragungsdatum':dd(t,'Eintragungsdatum'),'rechtsform':dd(t,'Rechtsform'),'stammkapital':dd(t,'Stammkapital'),'geschaeftszweig':dd(t,'Geschäftszweig'),'sitz':dd(t,'Sitz'),'sections':secs}
    o=out[s];print(s,'|',o['name'],'|',o['status'],'|',o['eintragungsdatum'],'|',o['rechtsform'],'|',o['sitz'],'|',{k:(v['count'],[(i['href'],i['name']) for i in v['items']]) for k,v in secs.items() if 'Geschäftsf' not in k and 'Prokur' not in k})
json.dump(out,open('evi2_out.json','w'),ensure_ascii=False,indent=1)
