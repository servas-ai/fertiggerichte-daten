import os,re,sys,shutil,subprocess,json
from PIL import Image,ImageChops
import numpy as np
PAD=0.04
def bbox_rgba(im):
  a=np.asarray(im.convert('RGBA')).astype(int)
  alpha=a[...,3]; rgb=a[...,:3]
  opaque=alpha>16
  # white-ish background (when no transparency) -> treat near-white as bg
  nonwhite=(rgb.min(axis=2)<240)|(np.abs(rgb.max(axis=2)-rgb.min(axis=2))>18)
  m=opaque&nonwhite if opaque.mean()>0.97 else opaque
  ys,xs=np.where(m)
  if len(xs)==0: return None,False
  return (xs.min(),ys.min(),xs.max()+1,ys.max()+1), opaque.mean()>0.97
def white_to_alpha(im):
  from PIL import ImageDraw
  im=im.convert('RGBA'); rgb=im.convert('RGB'); W,H=rgb.size
  marker=(255,0,254)
  for pt in [(0,0),(W-1,0),(0,H-1),(W-1,H-1)]:
    if min(rgb.getpixel(pt))>=240: ImageDraw.floodfill(rgb,pt,marker,thresh=24)
  m=np.all(np.asarray(rgb)==marker,axis=2); a=np.asarray(im).copy(); a[m,3]=0
  return Image.fromarray(a)
def crop_raster(p,out):
  im=Image.open(p); im.load(); im=im.convert('RGBA')
  bb,whitebg=bbox_rgba(im)
  if not bb: return 'empty'
  if whitebg:
    try: im=white_to_alpha(im)
    except Exception: pass
  x0,y0,x1,y1=bb; w,h=x1-x0,y1-y0; pd=int(round(max(w,h)*PAD))
  c=im.crop((x0,y0,x1,y1)); n=Image.new('RGBA',(w+2*pd,h+2*pd),(0,0,0,0)); n.paste(c,(pd,pd))
  n.save(out); return f'{im.size}->{n.size}{" wbg" if whitebg else ""}'
def crop_svg(p,out):
  s=open(p,encoding='utf8',errors='ignore').read()
  m=re.search(r'<svg\b[^>]*>',s,re.S); tag=m.group(0)
  vb=re.search(r'viewBox\s*=\s*["\']([^"\']+)',tag)
  def num(attr):
    q=re.search(attr+r'\s*=\s*["\']([\d.]+)',tag); return float(q.group(1)) if q else None
  if vb: X,Y,W,H=[float(v) for v in re.split(r'[ ,]+',vb.group(1).strip())]
  else:
    W,H=num(' width'),num(' height'); X=Y=0
    if not W: return 'no-dims'
  R=2000; t='/tmp/_svgc.png'
  if subprocess.run(['rsvg-convert','-w',str(R),'-o',t,p],capture_output=True).returncode: return 'render-fail'
  im=Image.open(t); bb,_=bbox_rgba(im)
  if not bb: return 'empty'
  sx=W/im.size[0]; sy=H/im.size[1]
  x0,y0,x1,y1=bb; nx,ny,nw,nh=X+x0*sx,Y+y0*sy,(x1-x0)*sx,(y1-y0)*sy
  pd=max(nw,nh)*PAD; nx-=pd;ny-=pd;nw+=2*pd;nh+=2*pd
  newtag=re.sub(r'\s(width|height|viewBox)\s*=\s*["\'][^"\']*["\']','',tag)
  newtag=newtag[:-1].rstrip('/')+f' viewBox="{nx:.3f} {ny:.3f} {nw:.3f} {nh:.3f}" width="{nw:.3f}" height="{nh:.3f}" preserveAspectRatio="xMidYMid meet">'
  if tag.endswith('/>'): return 'selfclosing'
  open(out,'w',encoding='utf8').write(s.replace(tag,newtag,1))
  return f'vb {W:.0f}x{H:.0f}->{nw:.0f}x{nh:.0f}'
for d in sys.argv[1:]:
  pre=os.path.join(d,'precrop'); os.makedirs(pre,exist_ok=True)
  for f in sorted(os.listdir(d)):
    p=os.path.join(d,f)
    if not os.path.isfile(p) or not re.search(r'\.(png|svg|jpg|jpeg|webp)$',f,re.I): continue
    orig=os.path.join(pre,f)
    if not os.path.exists(orig): shutil.copy2(p,orig)
    try:
      r=crop_svg(orig,p) if f.lower().endswith('.svg') else crop_raster(orig,p if f.lower().endswith('.png') else p)
    except Exception as e: r='ERR '+str(e)[:60]
    print(d.split('/')[-1],f,r)
