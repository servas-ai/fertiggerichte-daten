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
if __name__=='__main__':
  print(get(sys.argv[1]))
