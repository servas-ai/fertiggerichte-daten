# hourly T01: Gurkerl search walk — new stems + prior missed stock targets
import json,sys,re,time,glob
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
insp=set()
for f in glob.glob('/workspace/fertig/hourly/cand_gurkerl*.json'):
  try: insp|={str(p.get('source_id')) for p in json.load(open(f))}
  except Exception: pass
CAT=re.compile(r'Fertiggericht|Schnelle Küche|Suppen|Pizza|Fischstäbchen|Backfisch|Schlemmerfilet|Mehlspeisen|Menüs|Dosengericht|Tiefkühl.*(Fleisch|Geflügel|Snack|Fisch|Mehlspeis|Süß)|Feinkost|Marks|Nugget|Hendl|Pizza|Pasta|Eintopf|Bowl',re.I)
Q="backhendlstreifen kaiserschmarrn germknödel mohnnudeln spaghetteria ristorante steinofen seelachs-schnitzel dorsch-paniert scholle polardorsch cornflakesstäbchen leitschwendt streetfood air-fryer heura-burger udon eierspätzle mozzarella-sticks linsenburger tortelloni pizza-minis rindsgulasch karottensuppe gemüsenudelsuppe tomatencreme risotto-funghi wagner-diavolo frosta-fisch iglo-scholle iglo-dorsch chicken-wings schlemmerfilet ofengarnelen knusperfilet fischfrikadellen thunfisch-pasta putengeschnetzeltes kohlrouladen gefüllte-paprika spinatknödel käsespätzle tiroler-gröstl krautfleckerl pelmeni pierogi gyoza frühlingsrollen nasi-goreng bami-goreng pad-thai butter-chicken tikka-masala massaman tom-kha pho ramen jambalaya paella moussaka cannelloni enchilada chili-sin-carne ratatouille minestrone hühnersuppe gulaschsuppe erbsensuppe linseneintopf kartoffelsuppe kürbiscremesuppe broccolicreme little-lunch erasco sonnen-bassermann inzersdorfer-gulasch felix-chili followfood rebel-meat hubers vegavita garden-gourmet planted yuu-n-mee bedford apetito costa".split()
g=Gurkerl(); seen=set(); new=[]
for q in Q:
    q=q.replace('-',' ')
    try: ps=g.search(q,100)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in have or p.source_id in insp or p.source_id in seen or not CAT.search(p.category or ''): continue
        seen.add(p.source_id); new.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.25)
print('cands',len(new),flush=True)
json.dump([p.__dict__ for p in new],open('/tmp/h01/g_cands.json','w'),ensure_ascii=False,default=str)
for p in new: print('C',p.source_id,'|',p.category,'|',p.name,flush=True)
