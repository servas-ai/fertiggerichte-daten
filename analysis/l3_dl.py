import json,re,os,io,base64,requests,shutil,subprocess,urllib3
from PIL import Image
urllib3.disable_warnings()
U={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/129 Safari/537.36"}
WH={"User-Agent":"fertig-research/1.0 (logo research)"}
S=json.load(open('l3_spec.json')); L='logos/'
def wm(fn):
  j=requests.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',titles='File:'+fn,prop='imageinfo',iiprop='url',format='json'),headers=WH,timeout=20).json()
  return list(j['query']['pages'].values())[0]['imageinfo'][0]['url']
done={};res={}
for name,s in S.items():
  sl=s['slug']; r=dict(name=name,slug=sl,cat=s['cat'],note=s['note'],file=None,source=None,w=None,h=None)
  if sl in done: r.update(done[sl]); res[name]=r; continue
  try:
    if s['src'] is None: raise Exception('nosrc')
    kind=s['src'][0]
    if kind=='file':
      f=L+s['src'][1]; assert os.path.exists(f),f; out=f; src='existing'
      j=json.load(open('logos.json')); src=j.get(sl,{}).get('source') or j.get(s['src'][1].split('.')[0],{}).get('source') or 'existing'
    else:
      u=wm(s['src'][1]) if kind=='wm' else s['src'][1]
      if not u: raise Exception('no url')
      x=requests.get(u,headers=WH if kind=='wm' else U,timeout=30,verify=False); x.raise_for_status(); b=x.content
      src=u
      if b.lstrip()[:5] in (b'<?xml',b'<svg ') or b'<svg' in b[:500]:
        t=b.decode('utf8','ignore')
        emb=re.findall(r'data:img/png;base64,([A-Za-z0-9+/=]+)',t)
        if len(s['src'])>2 and s['src'][2]=='extract' and emb:
          Image.open(io.BytesIO(base64.b64decode(emb[-1]))).save(L+sl+'.png'); out=L+sl+'.png'
        else:
          for e in ('png',): 
            if os.path.exists(L+sl+'.'+e): shutil.move(L+sl+'.'+e,'logos/old/'+sl+'.'+e)
          open(L+sl+'.svg','wb').write(b); out=L+sl+'.svg'
      else:
        im=Image.open(io.BytesIO(b)); im.load()
        if getattr(im,'n_frames',1)>1: im.seek(0)
        im=im.convert('RGBA')
        if os.path.exists(L+sl+'.svg'): shutil.move(L+sl+'.svg','logos/old/'+sl+'.svg')
        im.save(L+sl+'.png'); out=L+sl+'.png'
    if out.endswith('.svg'):
      p=subprocess.run(['rsvg-convert','-w','512','-o','/tmp/chk.png',out],capture_output=True)
      if p.returncode: raise Exception('svg render fail')
      r.update(w='svg',h='svg')
    else:
      im=Image.open(out); r.update(w=im.size[0],h=im.size[1])
    r.update(file=out,source=src)
  except Exception as e:
    r['error']=str(e)[:80]
  done[sl]={k:r[k] for k in ('file','source','w','h')}; res[name]=r
  print(name,'|',r.get('file'),r.get('w'),r.get('h'),r.get('error',''))
json.dump(res,open('l3_res.json','w'),indent=1,ensure_ascii=False)
