import requests,re,json,urllib3,concurrent.futures as cf
from urllib.parse import urljoin
urllib3.disable_warnings()
U={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36"}
S={"gms-gourmet":"https://www.gourmet.at/","graninger":"https://graninger-lebensmittel.at/","hochreiter":"https://www.hochreiter-gruppe.at/","karnerta":"https://www.karnerta.at/","wiesbauer":"https://www.wiesbauer.at/","greisinger":"https://greisinger.at/","heiploeg":"https://www.heiploeg.com/","radatz":"https://www.radatz.at/","inzersdorfer":"https://www.inzersdorfer.at/","fit-to-go":"https://fittogo.at/","rana":"https://www.giovannirana.at/","rana2":"https://www.rana.com/at/de/","planted":"https://eatplanted.com/","hofstaedter":"https://www.hofstaedter.at/","landena":"https://www.landena.at/de/","blasko":"https://www.blasko.at/","hink":"https://hink.wien/","hubers-landhendl":"https://huberslandhendl.at/","wech":"https://www.wech.at/"}
def f(k):
  try: r=requests.get(S[k],headers=U,timeout=20,verify=False)
  except Exception as e: return k,{'err':str(e)[:80]}
  h=r.text
  imgs=[]
  for m in re.finditer(r'<img[^>]+>',h,re.I):
    t=m.group(0)
    if re.search(r'logo',t,re.I):
      s=re.search(r'(?:src|data-src)=["\']([^"\']+)',t)
      if s: imgs.append(urljoin(r.url,s.group(1)))
  imgs+=[urljoin(r.url,x) for x in re.findall(r'["\(]([^"\'\s\(\)]*logo[^"\'\s\(\)]*\.(?:svg|png|webp))',h,re.I)]
  inl=[m.group(0) for m in re.finditer(r'<svg[^>]*>.*?</svg>',h[:200000],re.S) if re.search(r'logo',m.group(0)[:300],re.I)]
  og=[urljoin(r.url,x) for x in re.findall(r'og:image["\'][^>]*content=["\']([^"\']+)',h)]
  return k,{'status':r.status_code,'imgs':list(dict.fromkeys(imgs))[:10],'inline_svg':[len(x) for x in inl][:3],'og':og[:1]}
R=dict(cf.ThreadPoolExecutor(10).map(f,S))
json.dump(R,open('logo_v2_probe.json','w'),indent=1)
for k,v in R.items(): print(k,json.dumps(v)[:700])
