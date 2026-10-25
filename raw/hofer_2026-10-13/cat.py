import re,json,dv
from hf import get
def tc(o):
  st=[o]
  while st:
    x=st.pop()
    if isinstance(x,dict):
      if isinstance(x.get('pagination'),dict) and 'totalCount' in x['pagination']: return x['pagination']['totalCount']
      st.extend(x.values())
    elif isinstance(x,list): st.extend(x)
if __name__=='__main__':
  cats=sorted(set(re.findall(r'href="(/produkte/[^"]+/k/[0-9]+)"',open('produkte.html').read())))
  res={}
  for c in cats:
    urls=set();pg=1;tot=None
    while True:
      h=get('https://www.hofer.at'+c+('?page=%d'%pg if pg>1 else ''))
      try: tot=tc(dv.nuxt(h))
      except Exception: pass
      new=set(re.findall(r'href="(/produkt/[^"]+)"',h))-urls
      urls|=new
      if not new or (tot and len(urls)>=tot) or pg>60: break
      pg+=1
    res[c]={'total':tot,'urls':sorted(urls)};print(c,tot,len(urls),flush=True)
  json.dump(res,open('cats.json','w'),ensure_ascii=False,indent=1)
