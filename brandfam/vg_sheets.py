import json,hashlib,os,subprocess,concurrent.futures as cf
from PIL import Image,ImageDraw
B=json.load(open('brand_families.json'))
VGP=json.load(open('qa/vision_gate.json'))['products']
items=[];seen=set()
for f in B['families']:
  for s in f['sub_brands']:
    for p in s['products']:
      pass
S=json.load(open('scored.json'))
for x in S:
  u=x.get('image_url')
  if x.get('sub_brand') and u and u not in seen and u not in VGP: seen.add(u);items.append((u,x['sub_brand'],x['name']))
print(len(items))
def dl(t):
  u=t[0];fn='brandfam/vg/'+hashlib.md5(u.encode()).hexdigest()+'.img'
  if not os.path.exists(fn): subprocess.run(['curl','-sL','-m','25','-A','Mozilla/5.0','-o',fn,u])
  return fn
with cf.ThreadPoolExecutor(12) as ex: fns=list(ex.map(dl,items))
idx=[];tiles=[]
for i,((u,sb,n),fn) in enumerate(zip(items,fns)):
  t=Image.new('RGB',(220,230),'white');ok=True
  try: im=Image.open(fn).convert('RGB');w,h=im.size;im.thumbnail((210,170));t.paste(im,(5,5))
  except Exception: ok=False;w=h=0;ImageDraw.Draw(t).text((60,80),'KEIN BILD',fill='red')
  d=ImageDraw.Draw(t);d.text((5,178),f'#{i} {sb}'[:34],fill='blue');d.text((5,195),n[:34],fill='black');d.text((5,211),n[34:68],fill='black')
  tiles.append(t);idx.append(dict(i=i,url=u,sub_brand=sb,name=n,load=ok,w=w,h=h))
json.dump(idx,open('brandfam/vg_index_new.json','w'),ensure_ascii=False,indent=0)
per=40
for k in range(0,len(tiles),per):
  ch=tiles[k:k+per];cols=8;rows=(len(ch)+cols-1)//cols
  s=Image.new('RGB',(cols*220,rows*230),'gray')
  for j,t in enumerate(ch): s.paste(t,((j%cols)*221,(j//cols)*231))
  s.save(f'brandfam/vg/new_sheet_{k//per:02d}.png')
print('sheets',(len(tiles)+per-1)//per, 'loadfail',sum(1 for x in idx if not x['load']))
