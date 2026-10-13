import json,requests,re,concurrent.futures as cf,urllib3
urllib3.disable_warnings()
U={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"de-AT,de"}
B=json.load(open('l3_brands.json'))
skip={'Billa','Spar','Hofer','Lidl','Penny','dm','SPAR','Knorr','Maggi','iglo','Felix','Inzersdorfer','Rana','Radatz','Planted','Fit to Go','Barilla','Alnatura','Frosta',"Ben's Original",'Hipp','Kikkoman','Recheis','Mowi','Ströck','Ja! Natürlich','GMS Gourmet','Greisinger','Hink Wien'}
def bases(n):
  s=n.lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('í','i').replace('&','und')
  a=re.sub(r"[^a-z0-9]","",s); b=re.sub(r"[^a-z0-9]+","-",s).strip('-')
  return list(dict.fromkeys([a,b]))
def chk(n):
  res=[]
  for b in bases(n):
    for tld in ['at','com','de','eu','it']:
      u=f'https://www.{b}.{tld}/'
      try:
        r=requests.get(u,headers=U,timeout=8,verify=False)
        t=re.search(r'<title[^>]*>(.*?)</title>',r.text,re.S|re.I)
        res.append((u,r.status_code,r.url,(t.group(1).strip()[:70] if t else '')))
      except Exception: pass
  return n,res
todo=[k for k in B if k not in skip]
R=dict(cf.ThreadPoolExecutor(24).map(chk,todo))
json.dump(R,open('l3_dom.json','w'),indent=1,ensure_ascii=False)
for k,v in R.items(): print(k,'=>',[f"{x[2]} [{x[1]}] {x[3]}" for x in v if x[1]<400])
