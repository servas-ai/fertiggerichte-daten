# hourly T21 (2026-10-13T21): SPAR public search API (food-connectors spar-shop) — ready-meal stems; keep only Fertiggerichte/Suppen/TK-Fertiggerichte/Pizza hits not yet present (article number in url)
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import spar_shop as SP
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have=set()
for x in S:
  for u in (x.get('url'),x.get('source_url')):
    m=re.search(r'(?:interspar|spar)\.at/.*?/p/(\d+)|/(\d{6,})(?:$|[/?#])',str(u or ''))
    if m and 'spar' in str(u): have.add(m.group(1) or m.group(2))
  if x.get('spar_article'): have.add(str(x['spar_article']))
print('have spar ids',len(have))
Q=["Fertiggericht","Eintopf","Gulasch","Suppe","Lasagne","Risotto","Curry","Chili","Knödel","Strudel","Kaiserschmarrn","Gnocchi","Tortelloni","Ravioli","Pizza","Reisfleisch","Krautfleisch","Schinkenfleckerl","Spätzle","Nockerl","Moussaka","Cannelloni","Auflauf","Paella","Nasi Goreng","Bami Goreng","Tikka Masala","Bowl","Menü","Geschnetzeltes","Ragout","Frikassee","Cordon Bleu","Schnitzel","Fischstäbchen","Schlemmerfilet","Backfisch","Nuggets","Burger","Wrap","Flammkuchen","Pinsa","Quiche","Maultaschen","Kasnudeln","Schlutzkrapfen","Germknödel","Marillenknödel","Topfenknödel","Mohnnudeln","Palatschinken","Milchreis","Gratin","Linseneintopf","Bohneneintopf","Erbseneintopf","Gemüsesuppe","Rindsuppe","Gulaschsuppe","Tomatensuppe","Kürbissuppe","Erdäpfelsuppe","Ramen","Pho","Dal","Korma","Butter Chicken","Pad Thai","Teriyaki","Sushi","Gyoza","Dim Sum","Frühlingsrollen","Burrito","Enchilada","Tacos","Falafel","Hummus Bowl","Spar Natur pur","Spar Veggie","SPAR Premium","S-Budget Fertiggericht","Inzersdorfer","Felix","Iglo","Frosta","Dr. Oetker","Wagner","Knorr","Maggi","Bürger","Hofmann","Gourmet","Toni Kaiser","Ackerl","Greisinger","Wiesbauer","Radatz","Mama Mancini","Youcook","Gustavo Gusto","Rana","Garden Gourmet","Planted","Like Meat","Rügenwalder","Vegini","Ben's Original","Uncle Ben","Erasco","Sonnen Bassermann","Hengstenberg","Kühne","Alnatura","Natur Compagnie","Ja! Natürlich"]
out={}
for q in Q:
  for page in (1,2):
    try: d=SP._q(q,n=100,page=page)
    except Exception as e: print('ERR',q,e); time.sleep(2); break
    hits=d.get('hits') or []
    n=0
    for h in hits:
      p=SP.to_product(h)
      if p.source_id in have or p.source_id in out: continue
      c=p.category or ''
      if not re.search(r'Fertiggerichte|Suppen|Pizza|Tiefkühl',c): continue
      out[p.source_id]=p.__dict__; n+=1
    print(q,page,len(hits),'new',n,flush=True); time.sleep(0.4)
    if len(hits)<100: break
json.dump(list(out.values()),open('/tmp/h21/spar_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
