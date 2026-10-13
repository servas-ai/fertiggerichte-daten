import os,subprocess,sys
from PIL import Image,ImageDraw
d=sys.argv[1]; out=sys.argv[2]
fs=sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d,f)) and f.rsplit('.',1)[-1] in('png','svg'))
def load(p):
  if p.endswith('.svg'):
    subprocess.run(['rsvg-convert','-w','400','-o','/tmp/b.png',p]); return Image.open('/tmp/b.png').convert('RGBA')
  return Image.open(p).convert('RGBA')
W,H,cols=360,120,4; rows=(len(fs)+cols-1)//cols
sh=Image.new('RGB',(W*cols,H*rows),'white'); dr=ImageDraw.Draw(sh)
for i,f in enumerate(fs):
  x,y=(i%cols)*W,(i//cols)*H
  for j,p in enumerate([os.path.join(d,'precrop',f),os.path.join(d,f)]):
    bx=x+j*(W//2)+6; box=(W//2-12,H-30)
    dr.rectangle([bx,y+4,bx+box[0],y+4+box[1]],fill=(205,205,205))
    try: im=load(p); im.thumbnail(box); bg=Image.new('RGBA',box,(205,205,205,255)); bg.alpha_composite(im,((box[0]-im.width)//2,(box[1]-im.height)//2)); sh.paste(bg.convert('RGB'),(bx,y+4))
    except Exception as e: pass
  dr.text((x+6,y+H-22),f[:40]+'   before | after',fill='black')
sh.save(out)
