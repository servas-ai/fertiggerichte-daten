import re,json,urllib.request,urllib.parse,urllib.robotparser,concurrent.futures as cf,hashlib,os,ssl,html
UA='Mozilla/5.0 (X11; Linux x86_64) servas-fertiggerichte/1.0 logo research'
ctx=ssl.create_default_context()
def get(u,n=3_000_000):
  r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA,'Accept-Language':'de-AT,de;q=0.9'}),timeout=25,context=ctx)
  return r.geturl(),r.headers.get('content-type',''),r.read(n)
S=[l.split('|') for l in (x.strip() for x in open('sites4.txt')) if l]
os.makedirs('cand',exist_ok=True)
def run(t):
  slug,url=t[0].strip(),t[1].strip()
  o={'slug':slug,'url':url,'cands':[]}
  try:
    p=urllib.parse.urlparse(url); rp=urllib.robotparser.RobotFileParser()
    try:
      _,_,rb=get(f'{p.scheme}://{p.netloc}/robots.txt',200000); rp.parse(rb.decode('utf8','ignore').splitlines()); o['robots_ok']=rp.can_fetch(UA,url)
    except Exception as e: o['robots_ok']=True; o['robots']='n/a '+str(e)[:60]
    if not o['robots_ok']: return o
    fu,ct,b=get(url); h=b.decode('utf8','ignore'); o['final']=fu
    c=[]
    for m in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]*>',h,re.I):
      mm=re.search(r'content=["\']([^"\']+)',m.group(0)); 
      if mm: c.append(('og',mm.group(1)))
    for m in re.finditer(r'<img[^>]+>',h,re.I):
      tag=m.group(0)
      if re.search(r'logo',tag,re.I):
        for a in ('src','data-src','data-lazy-src','srcset'):
          mm=re.search(a+r'=["\']([^"\'\s,]+)',tag)
          if mm: c.append(('img',mm.group(1))); break
    for m in re.finditer(r'<link[^>]+rel=["\'](?:apple-touch-icon|icon)[^>]*>',h,re.I):
      mm=re.search(r'href=["\']([^"\']+)',m.group(0))
      if mm: c.append(('icon',mm.group(1)))
    for m in re.finditer(r'["\']([^"\'\s]*logo[^"\'\s]*\.(?:svg|png|webp))["\']',h,re.I): c.append(('ref',m.group(1)))
    seen=set()
    for k,u in c:
      u=urllib.parse.urljoin(fu,html.unescape(u))
      if u in seen or u.startswith('data:'): continue
      seen.add(u)
      if len(o['cands'])>=6: break
      try:
        _,ct2,d=get(u,5_000_000); ext=('svg' if 'svg' in ct2 or u.lower().split('?')[0].endswith('.svg') else (ct2.split('/')[-1].split(';')[0] or 'img'))
        fn=f'cand/{slug}_{len(o["cands"])}.{ext}'; open(fn,'wb').write(d)
        o['cands'].append({'kind':k,'url':u,'file':fn,'bytes':len(d)})
      except Exception as e: pass
  except Exception as e: o['err']=str(e)[:120]
  return o
with cf.ThreadPoolExecutor(4) as ex: R=list(ex.map(run,S))
json.dump(R,open('site_logos4.json','w'),indent=1)
for o in R: print(o['slug'],o.get('robots_ok'),o.get('err',''),[ (c['kind'],c['file'],c['bytes']) for c in o['cands']])
