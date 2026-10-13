import requests,re,json,concurrent.futures as cf
from urllib.parse import urljoin
C={"gms-gourmet":"https://www.gmsgourmet.at","rewe-group":"https://www.rewe-group.at","wiesbauer":"https://www.wiesbauer.at","blasko":"https://www.blasko.at","karnerta":"https://www.karnerta.at","landena":"https://www.landena.at","hink":"https://www.hink.at","greisinger":"https://www.greisinger.at","hochreiter":"https://www.hochreiter.at","hubers-landhendl":"https://www.hubers.at","graninger":"https://www.graninger.at","radatz":"https://www.radatz.at","wech":"https://www.wech.at","heiploeg":"https://www.heiploeg.com","billa":"https://www.billa.at","spar":"https://www.spar.at","hofer":"https://www.hofer.at","lidl":"https://www.lidl.at","penny":"https://www.penny.at","dm":"https://www.dm.at","fit-to-go":"https://fittogo.at","knorr":"https://www.knorr.com/at","maggi":"https://www.maggi.at","inzersdorfer":"https://www.inzersdorfer.at","felix":"https://www.felix.at","iglo":"https://www.iglo.at","rana":"https://www.rana.com","planted":"https://www.eatplanted.com","vegavita":"https://www.spar.at"}
H={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36"}
def f(k):
  u=C[k]
  try:
    r=requests.get(u,headers=H,timeout=20)
    h=r.text
    t=re.search(r'<title[^>]*>(.*?)</title>',h,re.S|re.I)
    og=re.findall(r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]*content=["\']([^"\']+)',h,re.I)+re.findall(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*property=["\']og:image',h,re.I)
    ic=[urljoin(r.url,x) for x in re.findall(r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]*href=["\']([^"\']+)',h,re.I)]
    svg=[urljoin(r.url,x) for x in re.findall(r'(?:src|href)=["\']([^"\']*logo[^"\']*\.(?:svg|png))',h,re.I)][:5]
    return k,dict(final=r.url,status=r.status_code,title=(t.group(1).strip()[:80] if t else None),og=[urljoin(r.url,x) for x in og][:2],icons=ic[:4],logos=svg)
  except Exception as e: return k,dict(error=str(e)[:100])
res=dict(cf.ThreadPoolExecutor(15).map(f,C))
json.dump(res,open('comp_probe.json','w'),indent=1,ensure_ascii=False)
for k,v in res.items(): print(k,v.get('status'),v.get('final'),v.get('title'),v.get('error',''),'|L',v.get('logos',[])[:2],'|O',v.get('og'))
