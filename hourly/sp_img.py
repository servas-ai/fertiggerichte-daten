import json,re,subprocess,hashlib,concurrent.futures as cf,os
S=json.load(open('scored.json'))
BAD='4b6b5503e2ba4542bbc3cf2fbffd72bf'
todo=[p for p in S if not p.get('image_url') and re.search(r'interspar\.at/.*p/(\d{5,14})$',str(p.get('url')))]
print('todo',len(todo))
def chk(p):
  i=re.search(r'p/(\d{5,14})$',p['url']).group(1)
  u=f'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/{i}/dt_main.jpg'
  r=subprocess.run(['curl','-s','-m','25','-A','Mozilla/5.0','-w','%{http_code}|%{content_type}',u,'-o','/tmp/spi_'+i],capture_output=True,text=True).stdout
  try:b=open('/tmp/spi_'+i,'rb').read();os.remove('/tmp/spi_'+i)
  except:b=b''
  ok=r.startswith('200') and 'image' in r and len(b)>3000 and hashlib.md5(b).hexdigest()!=BAD
  return p,u,ok,len(b)
fx=[]
with cf.ThreadPoolExecutor(8) as ex:
  for p,u,ok,n in ex.map(chk,todo):
    if ok:fx.append(dict(url=p['url'],name=p['name'],field='image_url',old=None,new=u,reason='SPAR CDN Produktbild (Artikelnummer aus Produkt-URL, HTTP 200 geprüft, kein Platzhalter) 2026-10-13'))
print('ok',len(fx))
json.dump(fx,open('qa/hourly_spar_img_fixes.json','w'),ensure_ascii=False,indent=1)
