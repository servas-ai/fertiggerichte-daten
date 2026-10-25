import re,json,subprocess,dv
from hf import polite
def raw(u):
  polite('www.hofer.at');return subprocess.run(["curl","-sL","-m","60",u],capture_output=True).stdout.decode('utf-8','replace')
sm=raw('https://www.hofer.at/sitemap.xml');open('sm.xml','w').write(sm)
brands=sorted(set(re.findall(r'<loc>(https://www.hofer.at/marken/[^<]+)',sm)));print('brands',len(brands),flush=True)
from cat import tc
res={}
for b in brands:
  urls=set();pg=1;tot=None
  while pg<40:
    h=raw(b+('?page=%d'%pg if pg>1 else ''))
    try: tot=tc(dv.nuxt(h))
    except Exception: pass
    new=set(re.findall(r'href="(/produkt/[^"]+)"',h))-urls;urls|=new
    if not new or (tot and len(urls)>=tot): break
    pg+=1
  res[b]={'total':tot,'urls':sorted(urls)};print(b,tot,len(urls),flush=True)
  json.dump(res,open('marken.json','w'),indent=1)
