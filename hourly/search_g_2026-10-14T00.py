# hourly T00 (2026-10-14T00): Gurkerl search-metadata walk with brand + dish stems -> ids not yet in scored/connectors_new and not inspected in earlier hourly candidate files; ready-meal/frozen/soup/fish shelves; then fresh stock + composition enrich
import json,sys,re,time,glob
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
insp=set()
for f in glob.glob('/workspace/fertig/hourly/cand_gurkerl*.json'):
  try: insp|={str(p.get('source_id')) for p in json.load(open(f))}
  except Exception: pass
CAT=re.compile(r'Fertiggericht|Schnelle Küche|Suppen|Pizza|Fischstäbchen|Backfisch|Schlemmerfilet|Mehlspeisen|Menüs|Dosengericht|Tiefkühl.*(Fleisch|Geflügel|Snack|Fisch|Mehlspeis|Süß)|Feinkost|Marks',re.I)
Q="erasco little-lunch frosta iglo wagner ristorante gustavo toni-kaiser garden-gourmet rügenwalder like-meat planted vegini inzersdorfer felix sonnen-bassermann bamboo natsu yum-asia stastnik hink spitz tikka butter-chicken korma biryani jambalaya chili-sin-carne shakshuka ratatouille stroganoff fajita enchilada tacos quesadilla pierogi pelmeni piroggen wareniki kohlrouladen sarma gefüllte-paprika krautfleckerl schinkenfleckerl eiernockerl kaiserschmarrn topfenknödel marillenknödel zwetschkenknödel dampfnudel buchteln milchreis grießschmarrn strudel apfelstrudel cordon-bleu backhendl hühnerkeule wings chicken-nuggets kabeljau lachs-filet seelachs calamari garnelen thai-curry massaman pho tom-kha kichererbsen-curry linseneintopf erbsensuppe gulaschsuppe rindsuppe hühnersuppe tomatensuppe kartoffelsuppe".split()
g=Gurkerl(); seen=set(); new=[]
for q in Q:
    q=q.replace('-',' ')
    try: ps=g.search(q,100)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in have or p.source_id in insp or p.source_id in seen or not CAT.search(p.category or ''): continue
        seen.add(p.source_id); new.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.3)
print('cands',len(new),flush=True)
json.dump([p.__dict__ for p in new],open('/tmp/h00/g_cands.json','w'),ensure_ascii=False,default=str)
for p in new: print('C',p.source_id,'|',p.category,'|',p.name,flush=True)
