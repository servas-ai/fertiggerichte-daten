# hourly T07: enrich hand-picked BILLA heat-up candidates from novel-stem search + Menüschalen/TK searches
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={k(x['name']) for x in S if 'billa' in str(x.get('store') or '').lower()}
IDS=['00-892041','00-901948','00-892049','00-894631','00-868682','00-889480','00-747093',
     '00-284624','00-261892','00-441022','00-280556','00-292483']
# Extra search stems for chilled ready meals / TK not covered earlier
EXTRA=['dean & david','dean david bowl','sous vide pulled','back mozzarella','planted steak',
       'iglo ideenküche','iglo green cuisine','frosta genuss','frosta vegan','simply vegan menü',
       'billa corso menü','billa genusswelt menü','omisschmankerl','omi schmankerl gulasch',
       'inzersdorfer chili','inzersdorfer gulasch','felix gulasch','sonnen bassermann eintopf',
       'erasco eintopf','little lunch bio','zurück zum ursprung menü','ja natürlich menüschale',
       'clever menüschale','gustavo gusto pinsa','toni kaiser steinofen','wagner air fryer',
       'dr oetker tradizionale','dr oetker die ofenfrische','pizza baguette iglo','iglo baguette',
       'leibspeis','leitgebs','stadtküche bowl','youcook','deforian','deforian tortellini',
       'rana sfizi','rana panzerotti','mamma emma','la pasteria','bertagni','garofalo ravioli',
       'al codarosso','buitoni','barilla tortellini','ciriola','dinkelbauer','biotta',
       'chef menü','chef select menü','taste of asia fertiggericht','yam yam','yum yum cup noodles meal']
b=Billa(); seen=set(); cands=[]
for q in EXTRA:
    try: ps=b.search(q,50)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); cands.append(p); n+=1
    if n: print('Q',q,'new',n,flush=True)
    time.sleep(0.2)
# also fetch by id
for i in IDS:
    if i in seen: continue
    try:
        ps=b.search(i.replace('00-',''),5)  # fallback
    except: ps=[]
    # better: enrich via listing id
from food_connectors.http import get
out=[]
# merge IDS into cands by fetching product detail
for sid in IDS:
    if any(p.source_id==sid for p in cands): continue
    try:
        # product discovery by article
        d=get(f'https://shop.billa.at/api/product-discovery/products/{sid}')
        # may 404 — try search by last digits
    except Exception as e:
        pass

# Filter cands to meal-like then enrich
MEAL=re.compile(r'(bowl|menü|menue|fertig|pizza|baguette|gulasch|curry|eintopf|suppe|lasagne|schnitzel|nugget|fish|scholle|dorsch|schlemmer|knödel|knoedel|püree|puree|laibchen|cevap|frikadell|geschnetzelt|hendl|chicken|gyros|falafel|gyoza|frühlings|dim.?sum|paella|risotto|chili|maultasche|spätzle|fleckerl|strudel|palatschinken|kaiserschmarrn|germknödel|planted|mozzarella.?stick|sous.?vide|pulled|pinsa|flammkuchen|tortellini|ravioli|panzerotti|ofen)',re.I)
BAD=re.compile(r'(gewürz|basis für|paste\b|sauce\b|soße|teig\b|böden|chips|knabber|aufschnitt|wurst\b|salami\b(?! pizza)|käse gerieben|aufstrich|öl\b|essig|semmelwürfel|paniermehl|marinade|brühe|suppenwürfel|erdal|nassfutter|smoothie bowl|oatsome|reis arborio|lasagneblätter|suppennudel|eistee|dosenbier|adventuros|snackwürst|tomaten gewürfelt|pizza base|hendl filet$|hendl-innen|hendl-flügerl|faschiertes|unterkeulen)',re.I)
pick=[]
for p in cands:
    nm=p.name or ''; cat=p.category or ''
    if BAD.search(nm): continue
    if MEAL.search(nm) or MEAL.search(cat) or 'Menü' in cat or 'Fertig' in cat or 'Tiefkühl' in cat:
        if p.size_g and p.size_g>=50 and p.size_g<900:
            pick.append(p)
print('to enrich',len(pick),flush=True)
enriched=[]
for p in pick[:80]:
    try:
        b.enrich(p); time.sleep(0.35)
    except Exception as e:
        p.extra=p.extra or {}; p.extra['enrich_err']=str(e)
    n=p.nutrition_100g or {}
    print(p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'| stock',(p.extra or {}).get('in_stock'),'|',(p.producer or '')[:40],'|',p.ean, flush=True)
    enriched.append(p.__dict__)
# Also enrich IDS specifically via search of known products if missing
have={p['source_id'] for p in enriched}
for sid in IDS:
    if sid in have: continue
    # try get product page HTML / discovery
    try:
        d=get(f'https://shop.billa.at/api/product-discovery/products?searchTerm={sid}&pageSize=5')
        rs=d.get('results') or []
        matched=None
        for r in rs:
            if r.get('productId')==sid or r.get('articleId')==sid or str(r.get('productId','')).endswith(sid.replace('00-','')):
                matched=r; break
        if not matched and rs: matched=rs[0]
        if not matched: print('MISS',sid,flush=True); continue
        # convert via search again
        ps=b.search(matched.get('name','')[:40],10)
        for p in ps:
            if p.source_id==sid or sid.endswith(p.source_id.replace('00-','')):
                b.enrich(p); time.sleep(0.35)
                n=p.nutrition_100g or {}
                print('ID',p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'), flush=True)
                enriched.append(p.__dict__); break
    except Exception as e:
        print('ERR id',sid,e,flush=True)
json.dump(enriched,open('/tmp/h07/billa_cand.json','w'),ensure_ascii=False,default=str)
print('ENRICHED',len(enriched))
