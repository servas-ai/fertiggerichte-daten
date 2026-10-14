# hourly T07: MPreis sitemap meal-gap — product URLs not yet in scored/connectors_new
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
from food_connectors.http import get
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
# also slug keys
slugs={u.rstrip('/').split('/')[-1] for u in urls if u}
print('sitemap fetch...',flush=True)
try:
    sm=M.sitemap_urls()
except TypeError:
    # maybe needs no args - check
    import inspect
    print('sig',inspect.signature(M.sitemap_urls))
    sm=M.sitemap_urls()
print('sitemap',len(sm),flush=True)
MEAL=re.compile(r'(pizza|baguette|lasagne|gulasch|curry|eintopf|suppe|frikassee|bolognese|ravioli|tortellini|menue|menü|fertig|schnitzel|nugget|fish|fisch|scholle|dorsch|schlemmer|knoedel|knödel|puree|püree|laibchen|cevap|frikadell|geschnetzelt|hendl|haehnchen|hähnchen|chicken|gyros|falafel|gyoza|fruehlings|frühlings|dim-sum|paella|risotto|chili|maultaschen|spaetzle|spätzle|fleckerl|strudel|palatschinken|kaiserschmarrn|germknoedel|planted|mozzarella-sticks|sous-vide|pulled|pinsa|flammkuchen|panzerotti|iglo|frosta|wagner|oetker|inzersdorfer|felix|rana|mamma|bertagni|garofalo|youcook|deforian|leibspeis|leitgeb|stadtkueche|bowl|wrap|burrito|tikka|teriyaki|sweet-sour|suess-sauer|nasi|pad-thai|pommes|kroketten|rösti|roesti|tascherl|tasche|backhendl|cordon|piccolini|ristorante|steinofen|ofenfrische|air-fryer|green-cuisine|ideenkueche)',re.I)
BAD=re.compile(r'(gewuerz|gewürz|sauce|sosse|soße|ketchup|senf|oel|öl|essig|mehl|zucker|salz|broth|bruehe|teig(?!ericht)|chips|knabber|joghurt|milch|butter|kaese-gerieben|aufstrich|schokolade|bonbon|kaffee|tee-|wasser-|bier-|wein-|saft-|smoothie(?!-bowl-meal))',re.I)
cands=[]
for u in sm:
    if not isinstance(u,str): continue
    if '/shop/p/' not in u: continue
    slug=u.rstrip('/').split('/')[-1]
    if u in urls or slug in slugs: continue
    if BAD.search(slug) and not MEAL.search(slug): continue
    if MEAL.search(slug):
        cands.append(u)
print('meal-like new urls',len(cands),flush=True)
# fetch up to 60
out=[]; seen=set()
for u in cands[:80]:
    try:
        p=M.product(u)
    except Exception as e:
        print('ERR',u.split('/')[-1][:40],str(e)[:80],flush=True); time.sleep(0.5); continue
    time.sleep(0.35)
    if not p: print('NONE',u.split('/')[-1][:50],flush=True); continue
    if p.source_url in urls or p.source_id in seen: continue
    seen.add(p.source_id)
    n=p.nutrition_100g or {}
    print(p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',(p.extra or {}).get('availability'),'|',p.ean,flush=True)
    out.append(p.__dict__)
json.dump(out,open('/tmp/h07/mpreis_cand.json','w'),ensure_ascii=False,default=str)
json.dump(cands,open('/tmp/h07/mpreis_urls.json','w'),ensure_ascii=False)
print('FETCHED',len(out),'of',len(cands))
