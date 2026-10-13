import sys,json,re,dataclasses
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa
idx=json.load(open('idx_2026-10-13T02.json'));N=set(idx['names']);E=set(idx['eans']);U=set(idx['urls'])
norm=lambda s: re.sub(r'[^a-z0-9äöüß]','',(s or '').lower())
which=sys.argv[1]
out=[]
if which=='gurkerl':
  g=Gurkerl();seen=set()
  for q in ['fertiggericht','gulasch','eintopf','suppe','lasagne','risotto','curry','chili con carne','knödel','gnocchi','bowl','pasta fertig','schnitzel fertig','linsen','dal','paella','moussaka','tortellini','kaiserschmarrn','germknödel','strudel','pudding','milchreis','grießbrei','tiramisu','panna cotta','cannelloni','spätzle','ravioli','gefüllte paprika','krautfleckerl','szegediner','beuschel','eierspeis','tikka masala','frikassee','ragout','minestrone','gulaschsuppe','kürbissuppe','tomatensuppe','rindsuppe','nudelsuppe','frittaten','leberknödel','wok','nasi goreng','burrito','enchilada','falafel','couscous','bulgur','quiche','pizza','flammkuchen']:
    try: res=g.search(q,limit=60)
    except Exception as e: print('ERR',q,e,file=sys.stderr);continue
    for p in res:
      if p.source_id in seen: continue
      seen.add(p.source_id)
      if norm(p.name) in N or p.source_url in U: continue
      out.append(dataclasses.asdict(p))
elif which=='billa':
  b=Billa()
  for p in b.fetch(limit=2000):
    if norm(p.name) in N or p.source_url in U: continue
    out.append(dataclasses.asdict(p))
json.dump(out,open(f'cand_{which}_2026-10-13T02.json','w'),ensure_ascii=False,indent=1)
print(which,len(out))
for p in out: print(' |',p['name'],'|',p.get('brand'),'|',p.get('category'),'|',p.get('price_eur'))
