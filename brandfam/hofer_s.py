import re,json,sys,urllib.request,urllib.parse,html
def get(u):
  import subprocess;return subprocess.run(["curl","-sL","-m","40",u],capture_output=True).stdout.decode()
res={}
for q in sys.argv[1:]:
  for page in range(1,8):
    h=get('https://www.hofer.at/suchergebnisse?q='+urllib.parse.quote(q)+('&page=%d'%page if page>1 else ''))
    tiles=re.split(r'data-test="product-tile"',h)[1:]
    new=0
    for t in tiles:
      m=re.search(r'href="(/produkt/[^"]+)"',t)
      if not m or m.group(1) in res: continue
      txt=[s.strip() for s in re.sub(r'<[^>]+>','|',t[:6000]).split('|') if s.strip()]
      img=re.search(r'<img[^>]+src="([^"]+)"',t)
      price=next((s for s in txt if s.startswith('€')),None)
      res[m.group(1)]=dict(q=q,txt=txt[:14],img=img.group(1) if img else None,price=price);new+=1
    print(q,page,len(tiles),new,file=sys.stderr)
    if new==0:break
json.dump(res,open('hofer_raw.json','w'),ensure_ascii=False,indent=1)
