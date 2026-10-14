# hourly T00 (2026-10-14T00): MPreis sitemap gap (mp_gap_2026-10-14T00.py) — hand-picked heat-up meal slugs not yet in scored/connectors_new; robots-allowed product pages (JSON-LD offer + Nährwerte tab)
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
SLUGS="""felix-chili-con-carne-227512 allgroo-dumpling-mit-gemuese-gyoza-mandu-812506 toni-kaiser-mohnnudeln-810162 iglo-mohnnudeln-806031 dr-oetker-pietro-pizzi-margherita-1er-803527
jeden-tag-ravioli-in-tomatensauce-200073 alnatura-bio-falafel-366236 ahg-indian-tikka-masala-186778 ahg-thai-red-curry-186799 kaspressknoedel-233119 roberto-hot-dogs-4-stk-850745
omuer-boereklik-60-dose-242793 bens-original-express-sticky-bowl-reis-296776 planted-kebab-original-611577 capricci-tortelloni-formaggi-602996""".split()
out=[]
for s in SLUGS:
    u='https://www.mpreis.at/shop/p/'+s
    try: p=M.product(u)
    except Exception as e: print('ERR',s,str(e)[:80],flush=True); continue
    time.sleep(0.5)
    if not p: print('NONE',s,flush=True); continue
    out.append(p.__dict__)
    print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:40].replace('\n',' '),'|',(p.extra or {}).get('availability'),flush=True)
json.dump(out,open('hourly/cand_mpreis_2026-10-14T00.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
