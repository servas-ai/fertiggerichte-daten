import json,os,re,subprocess,time,fcntl,sys,dv
def polite(host):
  f=open(f'/tmp/host-{host}.lock','a+');fcntl.flock(f,fcntl.LOCK_EX)
  ts=f'/tmp/host-{host}.ts'
  try: last=float(open(ts).read())
  except: last=0
  w=1.1-(time.time()-last)
  if w>0: time.sleep(w)
  open(ts,'w').write(str(time.time()));fcntl.flock(f,fcntl.LOCK_UN);f.close()
def get(u):
  for a in range(30):
    polite('www.hofer.at');r=subprocess.run(["curl","-sL","-m","40",u],capture_output=True)
    h=r.stdout.decode('utf-8','replace')
    if r.returncode==0 and '__NUXT_DATA__' in h: return h
    time.sleep(min(300,30*(a+1)))
  return h
urls=re.findall(r'<loc>([^<]+)',open('sp.xml').read())
if len(sys.argv)>1: urls=[l.strip() for l in open(sys.argv[1]) if l.strip()]
out='products.jsonl';done=set()
if os.path.exists(out): done={json.loads(l)['url'] for l in open(out)}
fo=open(out,'a')
for i,u in enumerate(urls):
  if u in done: continue
  try:
    h=get(u);p=dv.find_product(dv.nuxt(h))
    bc=[]
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
      j=json.loads(m.group(1))
      if j.get('@type')=='BreadcrumbList': bc=[e['name'] for e in j['itemListElement']][2:-1]
    fo.write(json.dumps({'url':u,'p':p,'breadcrumb':bc},ensure_ascii=False)+'\n');fo.flush()
  except Exception as e:
    fo.write(json.dumps({'url':u,'error':str(e)[:200]})+'\n');fo.flush()
  if i%100==0: print(i,file=sys.stderr,flush=True)
