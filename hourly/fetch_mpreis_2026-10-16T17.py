import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
slugs={u.rstrip('/').split('/')[-1] for u in urls if u}
print('sitemap...',flush=True)
sm=M.sitemap_urls()
print('sitemap',len(sm),flush=True)
MEAL=re.compile(r'(pizza|baguette|lasagne|gulasch|curry|eintopf|suppe|frikassee|bolognese|ravioli|tortellini|menue|menü|fertig|schnitzel|nugget|fisch|scholle|dorsch|schlemmer|knoedel|knödel|puree|püree|laibchen|cevap|frikadell|geschnetzelt|hendl|hähnchen|chicken|gyros|falafel|gyoza|fruehlings|frühlings|paella|risotto|chili|maultaschen|spaetzle|spätzle|fleckerl|strudel|palatschinken|kaiserschmarrn|germknoedel|planted|mozzarella|sous-vide|pulled|pinsa|flammkuchen|iglo|frosta|wagner|oetker|inzersdorfer|felix|rana|youcook|leibspeis|stadtkueche|bowl|wrap|burrito|tikka|teriyaki|nasi|pad-thai|cordon|piccolini|ristorante|steinofen|green-cuisine|leitschwendt|ablinger|kaspress|leberknoedel|faschierte)',re.I)
BAD=re.compile(r'(gewuerz|gewürz|sauce|sosse|soße|ketchup|senf|oel|öl|essig|mehl|zucker|salz|bruehe|teig(?!ericht)|chips|knabber|joghurt|milch|butter(?!-chicken)|kaese-gerieben|aufstrich|schokolade|bonbon|kaffee|tee-|wasser-|bier-|wein-|saft-|smoothie|hummus|wurst(?!el)|schinken(?!-)|salami)',re.I)
cands=[]
for u in sm:
  if not isinstance(u,str) or '/shop/p/' not in u: continue
  slug=u.rstrip('/').split('/')[-1]
  if u in urls or slug in slugs: continue
  if BAD.search(slug) and not MEAL.search(slug): continue
  if MEAL.search(slug): cands.append(u)
print('meal-like new urls',len(cands),flush=True)
out=[]; seen=set()
for u in cands[:100]:
  try: p=M.product(u)
  except Exception as e:
    print('ERR',u.split('/')[-1][:40],str(e)[:80],flush=True); time.sleep(0.4); continue
  time.sleep(0.3)
  if not p: continue
  if p.source_url in urls or p.source_id in seen: continue
  seen.add(p.source_id)
  n=p.nutrition_100g or {}
  print(p.source_id,'|',p.brand,'|',(p.name or '')[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',(p.extra or {}).get('availability'),flush=True)
  out.append(p.__dict__)
json.dump(out,open('/tmp/h17/mpreis_sitemap.json','w'),ensure_ascii=False,default=str)
print('FETCHED',len(out))
