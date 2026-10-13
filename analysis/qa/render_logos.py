from PIL import Image,ImageDraw;import json,subprocess,os
c=json.load(open('companies.json'));os.makedirs('/tmp/lr',exist_ok=True)
cells=[]
for o in sorted(c,key=lambda o:(o['type'],o['slug'])):
  p=o['logo_path'];img=None;sz=None
  if p:
    if p.endswith('.svg'):
      t=f"/tmp/lr/{o['slug']}.png";subprocess.run(['rsvg-convert','-w','400','-o',t,p]);img=Image.open(t);sz='svg'
    else: img=Image.open(p);sz=img.size
  cells.append((o,img,sz))
W,H,cols=320,200,6;rows=(len(cells)+cols-1)//cols
sh=Image.new('RGB',(W*cols,H*rows),'white');d=ImageDraw.Draw(sh)
for i,(o,img,sz) in enumerate(cells):
  x,y=(i%cols)*W,(i//cols)*H
  d.rectangle([x,y,x+W-1,y+H-1],outline=(200,200,200),fill='white' if img else (235,235,235))
  if img:
    img=img.convert('RGBA');img.thumbnail((W-30,H-55));bg=Image.new('RGBA',img.size,(255,255,255,255));bg.alpha_composite(img);sh.paste(bg.convert('RGB'),(x+(W-img.width)//2,y+10))
  else: d.text((x+120,y+70),'NO LOGO',fill='red')
  d.text((x+6,y+H-38),f"{o['slug']} [{o['type']}]",fill='black');d.text((x+6,y+H-22),str(sz),fill=(90,90,90))
sh.save('qa/render/logos_v2.png')
