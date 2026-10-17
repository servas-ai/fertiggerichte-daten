import sys,re,html,json,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.polite import polite_urlopen
import urllib.request
U={'deflorian-srl':'https://deflorian.tirol/policies/legal-notice','bs-gastro-event-services-gmbh':'https://xn--brtchen-boutique-nwb.at/policies/legal-notice','caro-fratello-gmbh':'https://www.fratelli-barbaro.at/impressum','morgentau-biogemuese-gmbh':'https://morgentau.at/impressum','amlacher-nudeln':'https://amlachernudel.com/impressum/','recheis-teigwaren-gmbh':'https://www.recheis.com/impressum','wech-gefluegel-gmbh':'https://www.wech.at/impressum','dm-drogerie-markt-gmbh':'https://www.dm.at/impressum-218894','hartls-kulinarikum':'https://www.hartls-kulinarikum.at/impressum'}
out={}
for s,u in U.items():
    try:
        req=urllib.request.Request(u,headers={'User-Agent':'servas-fertiggerichte-daten/1.0 (https://github.com/servas-ai/fertiggerichte-daten; data squad)'})
        t=polite_urlopen(req,timeout=40).read().decode('utf-8','replace')
    except Exception as e:
        out[s]={'url':u,'error':repr(e)};print(s,'ERR',e);continue
    txt=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>','',t))))
    fns=re.findall(r'(?i)(?:FN|Firmenbuch(?:nummer)?|FBN)[^0-9]{0,40}?(\d{3,6}\s?[a-z])\b',txt)
    ctx=[txt[max(0,m.start()-80):m.end()+80] for m in re.finditer(r'(?i)firmenbuch|\bFN\b',txt)][:4]
    out[s]={'url':u,'len':len(t),'fn_candidates':sorted(set(f.replace(' ','') for f in fns)),'ctx':ctx}
    print(s,out[s]['fn_candidates'],'|',ctx[:2])
json.dump(out,open('/tmp/t0440/imp_out.json','w'),ensure_ascii=False,indent=1)
