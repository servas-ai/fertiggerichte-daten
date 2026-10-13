import glob,io,os,sys,json
from PIL import Image,ImageDraw
import cairosvg
fs=sorted(f for f in glob.glob('cand/*') if not f.endswith(('.html','.x-icon')))
tiles=[];idx=[]
def load(f):
  if f.endswith('.svg'):
    png=cairosvg.svg2png(url=f,output_width=400); return Image.open(io.BytesIO(png))
  return Image.open(f)
for f in fs:
  t=Image.new('RGB',(260,170),(235,235,235));d=ImageDraw.Draw(t)
  try:
    im=load(f); w,h=im.size; im=im.convert('RGBA'); bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); im=bg.convert('RGB'); im.thumbnail((250,140)); t.paste(im,(5,5))
    cap=f'{len(idx)} {os.path.basename(f)[:28]} {w}x{h}'
  except Exception as e: cap=f'{len(idx)} {os.path.basename(f)[:28]} ERR'; w=h=0
  d.text((4,152),cap,fill='blue'); tiles.append(t); idx.append({'i':len(idx),'file':f,'w':w,'h':h})
json.dump(idx,open('sheet_idx.json','w'),indent=0)
per=30;cols=6
for k in range(0,len(tiles),per):
  ch=tiles[k:k+per];rows=(len(ch)+cols-1)//cols;s=Image.new('RGB',(cols*262,rows*172),'gray')
  for j,t in enumerate(ch): s.paste(t,((j%cols)*262,(j//cols)*172))
  s.save(f'sheet_{k//per:02d}.png')
print(len(tiles))
