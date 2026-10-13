import json,hashlib,os,subprocess,concurrent.futures as cf
from PIL import Image,ImageDraw,ImageStat
V=json.load(open('expand_v5.json'))
def dl(x):
  u=x['image_url'];fn='qa/vg5/'+hashlib.md5(u.encode()).hexdigest()+'.img'
  if not os.path.exists(fn) or os.path.getsize(fn)==0: subprocess.run(['curl','-sL','-m','25','-A','Mozilla/5.0','-o',fn,u])
  return fn
with cf.ThreadPoolExecutor(4) as ex: fns=list(ex.map(dl,V))
idx=[];tiles=[]
for i,(x,fn) in enumerate(zip(V,fns)):
  t=Image.new('RGB',(180,190),'white');ok=True;w=h=0;flat=False
  try:
    im=Image.open(fn).convert('RGB');w,h=im.size;flat=max(ImageStat.Stat(im).stddev)<6;im.thumbnail((170,140));t.paste(im,(5,5))
  except Exception: ok=False;ImageDraw.Draw(t).text((50,60),'KEIN BILD',fill='red')
  d=ImageDraw.Draw(t);d.text((3,150),f'#{i} '+(x['name'][:28]),fill='black');d.text((3,168),x['name'][28:56],fill='black')
  tiles.append(t);idx.append(dict(i=i,url=x['image_url'],name=x['name'],load=ok,w=w,h=h,flat=flat,small=ok and min(w,h)<120))
json.dump(idx,open('qa/vg5/index.json','w'),ensure_ascii=False,indent=0)
per=60
for k in range(0,len(tiles),per):
  ch=tiles[k:k+per];cols=10;rows=(len(ch)+cols-1)//cols
  s=Image.new('RGB',(cols*181,rows*191),'gray')
  for j,t in enumerate(ch): s.paste(t,((j%cols)*181,(j//cols)*191))
  s.save(f'qa/vg5/sheet_{k//per:02d}.png')
print('load fail',[x['i'] for x in idx if not x['load']],'flat',[x['i'] for x in idx if x['flat']],'small',[x['i'] for x in idx if x['small']])
