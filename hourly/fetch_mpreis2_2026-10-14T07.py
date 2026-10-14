import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
slugs={u.rstrip('/').split('/')[-1] for u in urls if u}
sm=M.sitemap_urls()
print('sitemap',len(sm),flush=True)
# Strong meal slug patterns (finished products)
MEAL=re.compile(r'(fertiggericht|menue|menüschale|gulasch|chili-con|chili-sin|curry-|eintopf|lasagne|bolognese|carbonara|aglio|ravioli-|tortellini-|tortelloni-|schnitzel-|nuggets-|fish-and-chips|fischstaebchen|scholle-|dorsch-|schlemmerfilet|knoedel-|knödel|kartoffelpuree|kartoffelpüree|laibchen|cevapcici|frikadellen|geschnetzeltes|pulled-|sous-vide|mozzarella-sticks|planted-|pizza-(salami|prosciutto|tonno|funghi|spinaci|vegetale|margherita|diavolo|hawaii|quatro|quattro|speciale|royale|steinofen|ristorante|piccolini|ofenfrische|baguette)|flammkuchen|pinsa-|baguette-(schinken|salami|kaese|käse|pizza|ueberbacken)|kaiserschmarrn|germknoedel|marillenknoedel|topfenknoedel|palatschinken|buchteln|lavakuchen|maultaschen|kaesespaetzle|schinkenfleckerl|youcook-|stadtkueche-|leibspeis-|leitgeb|omi-schmankerl|omisschmankerl|hink-|inzersdorfer-|felix-(gulasch|chili|eintopf)|frosta-|iglo-(ideenkueche|green-cuisine|baguette|schlemmer|fish)|wagner-|dr-oetker-(ristorante|tradizionale|die-ofen|baguette|pizza)|rana-|mamma-emma|bertagni|garofalo-ravioli|vivera-|garden-gourmet|ruegenwalder|billie-green|endori-|heura-|good-catch|vegetarian-butcher|like-meat)',re.I)
BAD=re.compile(r'(backmischung|backaroma|backpulver|backspray|gewuerz|gewürz|sauce|sosse|ketchup|senf|oel-|öl-|mehl|zucker|salz-|bruehe|suppenwuerfel|teig(?!-ericht)|chips|knabber|joghurt|milch-|butter-|aufstrich|schokolade|bonbon|kaffee|tee-|reiniger|spuel|wasch|shampoo|creme(?!e)|seife|papier|tasche|shopper|granatapfel(?!-)|actimel|smoothie(?!-bowl)|pommes(?! )|kroketten|frites|roesti|rösti(?!-tasche)|kraeuter$|8-kraeuter|rosenmischung|babykarotten|fruehlingserbsen)',re.I)
cands=[]
for u in sm:
  if not isinstance(u,str) or '/shop/p/' not in u: continue
  slug=u.rstrip('/').split('/')[-1]
  if u in urls or slug in slugs: continue
  if BAD.search(slug): continue
  if MEAL.search(slug): cands.append(u)
print('strict meal urls',len(cands),flush=True)
out=[]; seen=set()
for u in cands[:70]:
  try: p=M.product(u)
  except Exception as e: print('ERR',slug[:40],str(e)[:60],flush=True); time.sleep(0.4); continue
  time.sleep(0.35)
  if not p or p.source_id in seen: continue
  seen.add(p.source_id)
  n=p.nutrition_100g or {}
  print(p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',(p.extra or {}).get('availability'),'|',p.ean,flush=True)
  out.append(p.__dict__)
json.dump(out,open('/tmp/h07/mpreis_cand.json','w'),ensure_ascii=False,default=str)
print('FETCHED',len(out),'of',len(cands))
