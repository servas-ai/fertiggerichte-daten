import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.spar_shop import SparShop
from food_connectors.adapters.alfies import Alfies

cands=json.load(open('/tmp/h17/spar_alfies.json'))
# Select complete heat-up meals with size
WANT=re.compile(
  r'(Rindsgulasch|Schweinsgulasch|Leberknödel(?! Suppe)|Leberknödelsuppe|'
  r'Chili con Carne(?! Mix|Fix|Basis|Seasoning)|'
  r'Butter-Chicken|Butter Chicken|Tikka Masala mit Reis|'
  r'Kaiserschmarrn (mit|ohne)|'
  r'Piccolinis |Wagner Pizza Margherita|'
  r'Schlemmerfilet|'
  r'Erdäpfelgulasch|Riesenbohnengulasch|Würstel in Gulaschsaft|'
  r'Gulaschsuppe(?! 12)|'
  r'Faschierte Laibchen mit|'
  r'Kaspressknödel|'
  r'Butter Chicken mit Reis|'
  r'Piccolinis (Wednesday|Mexiko|Brezel)|'
  r'Dean & David.*(Suppe|Karotten|Tomaten|Mango))',
  re.I)
BAD=re.compile(r'(Fix für|Basis für|Basis One|Seasoning|Mix 50g|Nachfüll|12 Portionen|Natur Protein Kick|Faschierte Laibchen$)',re.I)
pick=[]
for p in cands:
  nm=p.get('name') or ''
  if BAD.search(nm): continue
  if not WANT.search(nm): continue
  sg=p.get('size_g')
  if sg is None: continue
  try: sg=float(sg)
  except: continue
  if sg<80 or sg>=900: continue
  pick.append(p)
print('pick',len(pick))
for p in pick: print(p['_src'],p['source_id'],'|',p.get('brand'),'|',p['name'][:55],'|',p.get('price_eur'),p.get('size_g'))

sp,al=SparShop(),Alfies()
out=[]
for p0 in pick:
  src=p0['_src']
  try:
    if src=='spar':
      # search again and enrich match
      hits=sp.search(p0['name'][:40],20)
      p=next((x for x in hits if str(x.source_id)==str(p0['source_id'])),None)
      if p is None:
        # use cand data, try enrich by reconstructing
        from food_connectors.schema import Product
        p=Product(**{k:v for k,v in p0.items() if k!='_src' and k in Product.__dataclass_fields__}) if hasattr(Product,'__dataclass_fields__') else None
        # fallback: use raw dict via adapter enrich if possible
      if p and hasattr(sp,'enrich'):
        try: sp.enrich(p); time.sleep(0.35)
        except Exception as e: print('enr-err spar',e)
      if p is None:
        # fetch via URL if available
        p0['_failed']=True
        print('NONE spar',p0['source_id'],p0['name'][:40]); continue
    else:
      hits=al.search(p0['name'][:40],20)
      p=next((x for x in hits if str(x.source_id)==str(p0['source_id'])),None)
      if p and hasattr(al,'enrich'):
        try: al.enrich(p); time.sleep(0.35)
        except Exception as e: print('enr-err alf',e)
      if p is None:
        print('NONE alf',p0['source_id']); continue
  except Exception as e:
    print('ERR',src,p0['source_id'],e,flush=True); continue
  n=p.nutrition_100g or {}
  print(src,p.source_id,'|',p.brand,'|',p.name[:50],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'| img',bool(p.image_url),'| ean',p.ean,'|',(p.producer or '')[:35].replace('\n',' '),flush=True)
  d=p.__dict__; d['_src']=src; out.append(d)

json.dump(out,open('/tmp/h17/enriched_sa.json','w'),ensure_ascii=False,default=str)
print('ENRICHED SA',len(out))
