import json,re
exec(open('build.py').read().split('E=html.escape')[0])
src={(x.get('name') or '').strip():x for x in d}
SRCU={x.get('url'):x for x in d if x.get('url')}
# sensecheck 13: several scored rows can share one shop URL (heisse-preise canonical keeps old pack sizes, e.g. BILLA Lasagne
#  Bolognese 700 g + 400 g on …-00697017). A URL-only lookup gave every twin the attributes (price_date, meal_check, component…)
#  of whichever row came last, so look up by (url, name, size) first and only then fall back to url / name.
SRCUNS={(x.get('url'),(x.get('name') or '').strip(),f(x.get('size_g'))):x for x in d if x.get('url') and x.get('is_meal')}
def _srcx(r): return SRCUNS.get((r.get('url'),r.get('name'),r.get('size'))) or SRCU.get(r.get('url')) or src.get(r['name'],{})
for i,r in enumerate(R):
    x=_srcx(r); r['id']=i
    r['bio']=bool(x.get('bio')) or bool(re.search(r'\bbio\b',r['name']+' '+r['brand'],re.I))
    r['vegan']=bool(re.search(r'vegan',r['name']+' '+str(x.get('veg') or ''),re.I))
    r['sugar']=f(x.get('sugar_100')); r['fat']=f(x.get('fat_100')); r['carbs']=f(x.get('carbs_100')); r['ns']=x.get('nutriscore'); r['ns_st']=x.get('nutriscore_status'); r['nova']=x.get('nova'); r['additives']=x.get('additives'); r['eco']=x.get('ecoscore')
    r['manuf']=x.get('manufacturer'); r['origin']=x.get('origin'); r['psrc']=x.get('price_source'); r['src']=x.get('source_file'); r['state']=x.get('producer_state'); r['nutrition_source']=x.get('nutrition_source') or x.get('nut_source')
    r['prep']=x.get('prep')
    r['segment']=x.get('segment') or 'ready_meal'; r['delivers_4020']=x.get('delivers_4020'); r['delivery_source']=x.get('delivery_source'); r['allergens']=x.get('allergens'); r['availability_level']=x.get('availability_level') or 'chain'; r['price_date']=x.get('price_date'); r['ownbrand']=bool(x.get('ownbrand')); r['rankable_mealkit']=bool(x.get('rankable_mealkit')); r['price_kind']=x.get('price_kind'); r['ean']=x.get('ean') or x.get('barcode')
    if r.get('ns') is None and x.get('nutriscore_computed'): r['ns']=x['nutriscore_computed']; r['ns_st']='computed'
    r['qa']=x.get('qa_fixes')
    r['priceOnly']=r['p100'] is None and r['kcal'] is None
    r['eur10p']=round(r['price']/r['protpack']*10,2) if r['price'] and r['protpack'] else None
    r['eur100k']=round(r['price']/r['kcalpack']*100,2) if r['price'] and r['kcalpack'] else None
    r['pli']=round(0.5*r['score']+0.5*min((r['ppe'] or 0)/20,1)*100,1) if r['score'] is not None and r['ppe'] and r['pstat']=='live 2026' and r['rankable'] else None
LOGO=json.load(open('/workspace/fertig-app/public/logos/index.json'))
NORM=[(r'good choice','Good Choice'),(r'fit2go|fit to go','Fit to Go'),(r'^clever','Clever'),(r'billa immer gut','BILLA Immer Gut'),(r'ja! ?nat','Ja! Natürlich'),(r'^iglo','iglo'),(r'natur\*?pur','SPAR Natur*pur'),(r's-budget','S-Budget'),(r'vier diamanten|4 diamanten','Vier Diamanten'),(r'^knorr','Knorr'),(r'^maggi','Maggi')]
PARENT=[(r'billa|clever|ja! nat|vegavita|omis schmankerl|simply good|pure\b','Billa'),(r'spar|s-budget|despar','Spar'),(r'good choice|primana|cucina nobile|le gusto|hofer','Hofer'),(r'lidl|chef select|vemondo|combino|kania','Lidl'),(r'dmbio|^dm','dm')]
LK={k.lower():v for k,v in LOGO.items()}
import os
if os.path.exists('analysis/logos.json'):
    for k,v in json.load(open('analysis/logos.json')).items():
        if not v.get('file'): continue
        LK.setdefault(k.replace('-',' ').replace('ja natuerlich','ja! natürlich').replace('ben s original',"ben's original"),'analysis/'+v['file'])
        for _b in v.get('brands') or []: LK.setdefault(_b.lower(),'analysis/'+v['file'])
# 6c11fb6 regression fix: store-less OFF rows get their shop from gaps_overlay.json (heisse-preise exact-name match,
#  normally applied after export by `gaps_overlay.py --apply`); applying it here keeps the known store even if that step is skipped.
_GO=json.load(open('gaps_overlay.json')) if os.path.exists('gaps_overlay.json') else {}
_n_go=0
for r in R:
    if str(r.get('store') or '').startswith('unbekannt'):
        _o=_GO.get(str(r['store'])+'|'+r['name']) or {}
        if _o.get('shop_status')=='filled' and _o.get('store'): r['store']=_o['store']; r['stores_seen']=_o.get('stores_seen'); r['shop_src']=_o.get('shop_src'); _n_go+=1
print('gaps_overlay store restored',_n_go)
for r in R:
    b=(r['brand'] or '').split(',')[0].strip()
    for pat,nm in NORM:
        if re.search(pat,b,re.I): b=nm;break
    r['brandN']=b or '(ohne Marke)'
    r['noBrand']=not b
    bl=b.lower(); logo=LK.get(bl)
    if not logo:
        for k,v in LK.items():
            if bl.startswith(k) and len(k)>2: logo=v;break
    if not logo:
        for pat,par in PARENT:
            if re.search(pat,bl): logo=LK.get(par.lower()); r['brandParent']=par; break
    r['logo']=logo
# --- v3.3 data fixes (UI-QA) ---
for r in R:
    t=(r['name']+' '+(r['brand'] or '')).lower()
    r['nonfood']=bool(re.search(r'tupper|likör|cognac|bowl ?set|wonderlier|hobel|presse|löffel|kelomat|fackelmann|\bgefu\b|riess\b|vodka|whisky|\bwein\b|sekt',t))
    if r.get('size')==1000 and r.get('price') and r.get('ppk')==r['price']:
        m=re.search(r'(?:ca\.?\s*)?(\d{2,4})\s?g\b',r['name'].lower())
        if m and int(m.group(1))!=1000 and 'x' not in r['name'].lower()[max(0,m.start()-4):m.start()]:
            w=int(m.group(1));fct=w/1000
            r['price']=round(r['ppk']*fct,2);r['size']=w
            for k in ('protpack','kcalpack'):
                if r.get(k) is not None: r[k]=round(r[k]*fct,1)
            r['flags']=(r.get('flags') or [])+['Kilopreis → Packungspreis aus Gewicht umgerechnet']
        elif r['price']>=12 and re.search(r'gulasch|roastbeef|sous|braten|hendl|fleisch|rind|schwein',t):
            r['kiloErr']=True;r['rankable']=False;r['flags']=(r.get('flags') or [])+['Preis ist vermutlich €/kg (Packungsgewicht unbekannt)']
    if re.search(r'soja ?geschnetzel|sojagranulat|soja-?schnetzel|textured',t) or (r.get('p100') or 0)>=40 and (r.get('kcal') or 0)>=300: r['dry']=True;r['rankable']=False
    if (r['store'] or '').startswith('unbekannt'): r['rankable']=False
    r['eur10p']=round(r['price']/r['protpack']*10,2) if r.get('price') and r.get('protpack') else None
    r['eur100k']=round(r['price']/r['kcalpack']*100,2) if r.get('price') and r.get('kcalpack') else None
    r['ppe']=round(r['protpack']/r['price'],1) if r.get('price') and r.get('protpack') else r.get('ppe')
    r['pli']=round(0.5*r['score']+0.5*min((r['ppe'] or 0)/20,1)*100,1) if r.get('score') is not None and r.get('ppe') and r['pstat'] in('live 2026','aktuell') and r['rankable'] else None
PROT=[('Ripperl/Spareribs','🍖',r'ripperl|spare ?ribs|rippchen'),('Huhn','🐔',r'huhn|hühn|hähn|chicken|hendl|pollo|geflügel'),('Pute','🦃',r'pute|truthahn|turkey'),('Rind','🐄',r'rind|beef|kalb|tafelspitz|roastbeef'),('Schwein','🐖',r'schwein|schinken|speck|leberk|wurst|würst|knacker|cevapcici|grammel|kassler|selch|bratwurst|carne|bolognese|faschiert|fleischlaib|frankfurter|hot dog|leber'),('Lamm','🐑',r'lamm'),('Wild','🦌',r'wild|hirsch|reh'),('Fisch','🐟',r'fisch|lachs|seelachs|thunfisch|forelle|kabeljau|dorsch|schlemmerfilet|hering|makrele|pangasius|zander|tuna'),('Meeresfrüchte','🦐',r'garnele|shrimp|scampi|meeresfr|muschel|tintenfisch|calamar'),('Ei','🥚',r'\bei\b|eier(?!spätzle|nudel)|omelett|frittata'),('Käse/Milch','🧀',r'käse|kas|mozzarella|ricotta|topfen|feta|parmesan|cheese|gorgonzola|rahm'),('Tofu/Soja','🫘',r'tofu|soja|tempeh|edamame'),('Hülsenfrüchte','🥜',r'linsen|kichererb|bohnen|erbsen|dal\b|falafel|hummus'),('Seitan/Fleischersatz','🌱',r'seitan|vegavita|planted|like meat|veggie|fleischersatz|vegan.*(burger|nugget|schnitzel|cordon|wurst)|beyond')]
DISH=[('Gulasch','🥘',r'gulasch|goulash|paprikash|letscho'),('Curry','🍛',r'curry|tikka|masala|korma|dal\b'),('Lasagne','🍝',r'lasagne'),('Pasta','🍝',r'pasta|nudel|spaghetti|penne|tortell|ravioli|maccaroni|makkaroni|linguin|gnocchi|cappellet|fusilli|tagliatelle|spätzle|spirelli|hörnli|fleckerl|kasnudel'),('Risotto','🍚',r'risotto'),('Knödel','🥟',r'knödel|nockerl|dumpling'),('Suppe','🍲',r'suppe|soup|bouillon|brühe|consommé|ramen|pho\b'),('Eintopf','🫕',r'eintopf|topf|ragout|chili|stew|schmorr|geschnetzel'),('Bowl','🥗',r'bowl|salat'),('Asia','🥢',r'asia|teriyaki|thai|wok|süß ?sauer|sweet|nasi|bami|noodle|sushi|gyoza|pad\b|chinese|japan|korea|indisch|ente'),('Mexikanisch','🌮',r'mexi|burrito|tortilla|wrap|chili con|enchilada|taco|quesadilla'),('Österreichisch','🇦🇹',r'schmankerl|omis|wiener|tiroler|kärntner|steir|pinzgauer|schwammerl|kaiserschmarr|grammel|beuschel|tafelspitz|leberkäs|eiernockerl|krautfleckerl|serviettenknödel|alt.?wiener|backhendl|schweinsbraten|stelze|bauernschmaus|erdäpfel'),('Paniert','🍗',r'panier|cordon|schnitzel|nugget|backhendl|backfisch|knusper|crispy|bordelaise|stäbchen|sticks'),('Grill/mariniert','🔥',r'grill|marinier|bbq|spieß|spiess|steak|ripperl|spare|pulled|sous ?vide'),('Pizza/Snack','🍕',r'pizza|flammkuchen|burger|hot dog|sandwich|toast|strudel|baguette')]
PLAIN_PASTA=re.compile(r"\b(tagliatelle|tagliolini|pappardelle|linguine|fettuccine|bandnudeln|eiernudeln|spaghetti|spaghettini|rigatoni|tortiglioni|penne|fusilli|farfalle|orecchiette|trofie|strozzapreti|paccheri|bucatini|maccheroni|makkaroni)(\s+(all.?uovo|fresche?|frisch|nester|nidi))?\s*(\((frische )?pasta\)|\(frisch\))?\s*$",re.I)
# review 13 G: verified pack corrections (mpreis.at 16.10.: Nettofüllmenge 710 g = 2 × 355 g) and app-only price labels
SIZE_FIX={('MPreis','Jeden Tag Steinofenpizza Thunfisch 2er-Packung'):(700,710)}
import os
# review 13 G: app-only price notes, re-checked by price_condition_check.py (robots.txt, ≥1 s/host); inactive → dropped
PRICE_COND={}
if os.path.exists('price_conditions.json'):
    for _c in json.load(open('price_conditions.json')).get('conditions',[]):
        if _c.get('active'): PRICE_COND[(_c['store'],_c['name'])]=_c
for r in R:
    _k=(r.get('store'),r.get('name'))
    if _k in SIZE_FIX and r.get('size')==SIZE_FIX[_k][0]:
        r['size']=float(SIZE_FIX[_k][1])
        if r.get('p100') is not None: r['protpack']=round(r['p100']*r['size']/100,1)
        if r.get('kcal') is not None: r['kcalpack']=round(r['kcal']*r['size']/100)
        if r.get('price'): r['ppk']=round(r['price']/r['size']*1000,2); r['ppe']=round(r['protpack']/r['price'],1) if r.get('protpack') else r.get('ppe')
    _txt=' '.join([str(r.get('name') or ''),str(r.get('price_kind') or '')]+[str(f) for f in (r.get('flags') or [])])
    if _k in PRICE_COND:
        _c=PRICE_COND[_k]; r['price_condition']=_c['text']; r['price_condition_info']=dict(text=_c['text'],source_url=_c['source_url'],checked=_c['checked'])
    elif re.search(r'nur mit (der )?app',_txt,re.I): r['price_condition']='NUR MIT APP'; r['price_condition_info']=dict(text='NUR MIT APP',source_url=r.get('url'),checked=None)
# review 13 F(b): delivery services → shipping per box of 6 dishes on top of the portion price (online_mealprep.json shipping_eur)
SHIP_BOX=6
SHIP={}
try:
    for _o in json.load(open('online_mealprep.json')):
        _s=str(_o.get('store') or '').replace('Online: ','').replace('bofrost*','bofrost')
        if _o.get('shipping_eur') is not None: SHIP.setdefault(_s,float(_o['shipping_eur']))
except Exception as _e: print('shipping load failed',_e)
SHIP.setdefault('PrepMyMeal',5.99)
_NOSHIP=set()
MEALPREP_ONLY={'PrepMyMeal','Juit','every.','LiveFresh','FitTaste','Fit to Go','Löwenanteil','Kernbeißer','Goldblatt','iss mich!'}
for r in R:
    t=(r['name']+' '+r['brand']).lower()
    ps=[n for n,i,p in PROT if re.search(p,t)]
    if r['vegan'] or 'vegan' in t: ps.append('vegan')
    elif not any(p in ps for p in ['Ripperl/Spareribs','Huhn','Pute','Rind','Schwein','Lamm','Wild','Fisch','Meeresfrüchte']) and (ps or re.search(r'veget|gemüse|spinat|pilz|schwammerl',t)): ps.append('vegetarisch')
    ds=[n for n,i,p in DISH if re.search(p,t)]
    if r['pack']=='Tiefkühl (TK)' and not ds and re.search(r'gemüse|brokkoli|spinat|erbsen',t): ds.append('Beilage/Gemüse')
    r['cprot']=list(dict.fromkeys(ps)); r['cdish']=list(dict.fromkeys(ds))
    hasMit=re.search(r'\bmit\b|&| und |menü|teller|pfanne|bowl|lasagne|curry|gulasch|risotto',t)
    t=re.sub(r'mit haut|ohne haut|mit knochen|ohne knochen','',t)
    raw=re.search(r'faschiert|hackfleisch|\bhack\b|filet|brust|keule|unterkeul|oberkeul|flügel|wings|steak|schnitzel|leber|gulaschfleisch|geschnetzeltes|würfel|minute|ganzes|ganzer|hendl\b|hähnchen|kotelett|karree|schopf|bauch|lachs|forelle|garnelen|shrimps|kabeljau|seelachs|zander|saibling|thunfisch.*steak',t) and not re.search(r'gegart|gebraten|gebacken|schlemmerfilet|bordelaise|backfisch|backteig|paniert|gegrillt|mariniert|sous|knusper|nugget|backhendl|cordon|fertig|gekocht|geräuchert|räucher|mit |sauce|soße|in |menü|curry|gulasch\b|suppe|topf|salat|knödel|reis|bowl|wrap|sandwich|pizza|burger|stäbchen|sticks|chili|bbq|grill|pulled|rahm|natur\*pur bio hendl mini|pasta|spaghetti|penne|tagliatelle|pappardelle|linguine|fusilli|rigatoni|makkaroni|nudel|gnocchi|tortell|ravioli',t) and not r['pack'].startswith('Dose')
    if raw or ((r.get('kcal') or 0)>=300 and re.search(r'suppe|nudel|pulver|teigwar|einlage|abc|sternderl|gerstl|hörnchen|fadennudel|buchstaben|instant|terrine|cup|reis\b|couscous|bulgur|polenta|grieß',t) and (r.get('fat') or 0)<15) or re.search(r'barilla lasagne|collezione lasagne|recheis lasagne|lasagne hartweizen|glutenfreie lasagne|lasagneblätter|lasagne-?platten',t) or ('lasagne' in t and (r.get('kcal') or 0)>=300): stg='base'
    elif re.search(r'erdbeer|marillen|zwetschk|nougat|germknödel|topfenknödel|mehlspeis|kaiserschmarr|powidl|mohn|vanille|schoko',t): stg='base'
    elif r.get('dry') or re.search(r'sauce|soße|fix\b|fix |pesto|gewürz|würfel|pulver|bouillon|fond|dressing|mehl|paniermehl|brühe(?!.*einlage)',t) and not re.search(r'suppe|topf|\bin \w*(sauce|soße)|mit \w*(sauce|soße)|\bpizza\b|ristorante|intermezzo|tradizionale|ravioli|tortell|nudel|spaghetti|cannelloni|gnocchi|reis|fleisch|würstel|huhn|hendl|rind',t): stg='base'
    elif re.search(r'suppe|eintopf|\\btopf|topf\\b|chili con|gulasch.*dose|linsen|bohnen.*eintopf|ragout|consommé|ramen',t): stg='stew'
    elif not hasMit and re.search(r'lachs|thunfisch|huhn|hühn|hähn|chicken|garnel|shrimp|scampi|rind|schinken|speck|lamm|pute',t) and re.search(r'\b(spaghetti\w*|penne|tagliatelle|pappardelle|linguine|fusilli|rigatoni|makkaroni|pasta)\b|nudeln?\b',t) and not re.search(r'salat',t): stg='meal'  # sensecheck 12-verify: protein + pasta in one name is a dish (Frosta Tagliatelle Wildlachs), not a raw cut/component
    elif not hasMit and re.search(r'ripperl|spare ?rib|spie(ß|ss)|schnitzel|cordon|nugget|stäbchen|sticks|filet|laibchen|cevap|burger|frikadell|fleischlaibchen|leberkäs|steak|hendl(?!.*mit)|chicken wings|drumstick|keule|grillwurst|bratwurst|kebab|gyros|pulled|tofu|tempeh|falafel|fischburger|backfisch|lachs',t): stg='prot'
    elif not hasMit and re.search(r'knödel|reis\b|basmati|püree|kroketten|pommes|frites|rösti|gnocchi|spätzle|nockerl|kartoffel|erdäpfel|couscous|bulgur|polenta|nudeln',t): stg='side'
    elif not hasMit and re.search(r'gemüse|brokkoli|spinat|erbsen|karotte|fisolen|rahmspinat|kohl|bohnen|mais|kaiserschoten|zucchini|blattspinat|salat',t): stg='veg'
    else: stg='meal'
    if r.get('nonfood') or r.get('dry'): stg='base'
    elif re.search(r'backerbsen|fertigmischung|nockerlgrieß|pastina|naturreis|spätzlekäse|kartoffelpüree|sugo|party-spies|suppengemüse|suppeneinlage',t): stg='base'
    # sensecheck 12-verify: plain fresh egg pasta (name ends in the pasta shape, raw ~270 kcal/100 g, e.g. Alfies 'Bertagni Tagliatelle (frische Pasta)', 'Rana Tagliatelle') is an ingredient, not a ready meal;
    #  ready pasta dishes are 90-200 kcal/100 g, so the kcal floor keeps 'Pumpkin Rigatoni' / 'Wildlachs Spaghetti' as meals
    elif PLAIN_PASTA.search(r['name']) and (r.get('kcal') or 0)>=230 and stg in('side','veg','meal'): stg='base'
    elif re.search(r'\b(fusilli|makkaroni|penne|spaghetti|farfalle)\b',t) and not re.search(r'sauce|bolognese|carbonara|mit|fertig',t) and stg in('side','veg','meal') and (r.get('kcal') or 300)>=300: stg='base'
    elif stg in('veg','side','prot') and re.search(r'strudel|pinsa|pizza|brot\b|pastasalat|nudelsalat|eiersalat|bbq salat|wrap|burger|pasta fertig|fertiggericht|gebratene nudeln|magic asia|kasnudel|käsnudel|tomaten-mozzarella-nudeln|kürbis-nudeln|meeresküche|airfryer snack|goldschatz|cashew taschen|baguette|piccolini|big sensation|steinofen|ofenfrische|backfrische|flammkuchen|intermezzo',t): stg='meal'  # T18: Dr. Oetker Intermezzo (TK Baguette-Snack, Thunfisch/Pesto variants) → meal; T16: TK snack pizzas/baguettes & Goldschatz fillets are meals; T17: Wagner Piccolinis/Big Sensation/Steinofen, Dr. Oetker Ofenfrische, Backfrische, Flammkuchen (pizza products without the word 'Pizza' in the name), not veg/prot
    elif re.search(r'(leber|wurst|grammel|selchfleisch|fleisch|speck|haschee|heurigen)knödel|currywurst|curry king|thunfisch',t) and not re.search(r'mit (sauerkraut|kraut|salat|gemüse|püree)|suppe|salat|pasta|nudel|sauce|menü|pizza|piccolini|big sensation|steinofen|ristorante|bistro|baguette|intermezzo|wrap',t): stg='prot'  # sensecheck 6: Thunfisch-Wrap is a meal/snack, not a protein component
    elif re.search(r'knödel|kaspress',t) and not re.search(r'mit |suppe|menü|sauce',t): stg='side'
    # T20: Kärntner Kas-/Käsnudel(n) are a complete traditional dish (meal, like the rule above) — no longer demoted to 'side' when the name lacks 'Nudeln';
    #  raw-cut guard: 'gebacken' (pre-fried Putenschnitzel) and Schlemmerfilet/Bordelaise/Backfisch (oven-ready fish with topping/batter) are not raw ingredients → prot instead of base
    elif re.search(r'ravioli|tortell|fagottini|girasoli|cappellet|gnocchi',t) and not re.search(r'pfanne|sauce|soße|carbonara|bolognese|gratin|al forno|menü|mit .*(sauce|soße)|teller|bowl',t): stg='side'
    # sensecheck 8: pure finished-meal providers (no components) — 450 g 'Spätzle Goulash'/'Garden Gnocchi'/'Peanut Noodles' are meals, not Beilage/Zutat.
    #  bofrost excluded on purpose: it also sells components (Knödel, Cevapcici, Schnitzel).
    if r.get('src')=='online_mealprep.json' and r.get('store') in MEALPREP_ONLY and stg in('side','base','veg','prot') and not r.get('dry') and not r.get('nonfood'): stg='meal'
    # T18: TK fruit dumplings (Himbeer-/Heidelbeerknödel) and Milchrahmstrudel are warm desserts
    sweet=re.search(r'kaiserschmarr|germknödel|topfenstrudel|apfelstrudel|milchreis|marillenknödel|zwetschk|erdbeerknödel|topfenknödel|himbeerknödel|heidelbeerknödel|waldbeerknödel|nougatknödel|topfennockerl|apfelringe im backteig|strudel-quartett|milchrahmstrudel|mohnnudel|buchtel|palatschink|grießbrei|pudding|nougat|powidl|dessert|mehlspeis|scheiterhaufen|schoko|tiramisu|panna cotta',t)
    # hourly 2026-10-16T18: savoury filled Palatschinken (Schinken-Käse-Lauch) are a warm starter, not a dessert
    if sweet and re.search(r'palatschink\w*.*(schinken|käse|lauch|spinat|fleisch)',t): sweet=None
    if sweet and not r.get('nonfood'):
        stg='meal'; r['gang']='dessert'; r['rankable']=False
    elif stg=='stew' and re.search(r'suppe|consommé|ramen|brühe',t): r['gang']='vorspeise'
    elif stg in('side','veg'): r['gang']='beilage'
    elif stg=='base': r['gang']='zutat'
    else: r['gang']='haupt'
    r['stage']=stg
    if r.get('pstat')=='aktuell': r['pstat']='live 2026'
    sz=r.get('size') or 0
    por={'meal':sz,'stew':min(sz,400) if sz else 0,'prot':min(sz,150) if sz else 0,'side':min(sz,200) if sz else 0,'veg':min(sz,150) if sz else 0,'base':min(sz,100) if sz else 0}[stg]
    mp=re.search(r'(\d+)\s*(portionen|port\.|stück|stk)',t)
    if mp and sz and stg in('meal','stew') and int(mp.group(1))>1: por=sz/int(mp.group(1))
    if r.get('kiloErr'): por=0
    r['portion']=round(por) if por else None
    f=(por/sz) if sz and por else None
    r['pPor']=round(r['price']*f,2) if f and r.get('price') else None
    r['p100g']=round(r['price']/sz*100,2) if sz and r.get('price') else None
    r['protPor']=round(r['p100']*por/100,1) if por and r.get('p100') is not None else None
    r['kcalPor']=round(r['kcal']*por/100) if por and r.get('kcal') is not None else None
    r['saltPor']=round(r['salt']*por/100,2) if por and r.get('salt') is not None else None
    r['saltPct']=round(r['saltPor']/6*100) if r['saltPor'] is not None else None
    # --- score v2 fields (analysis/score_v2.md); portion=100 placeholder -> unknown ---
    _x=_srcx(r)
    for _k in ('nutrition_basis','nova','nova_source','veg_pct','veg_source','portion_g','portion_source','kcal_meal','meal_class','day_pct','score_parts','health_score_v1'): r[_k]=_x.get(_k)
    r['scoreV1']=r.pop('health_score_v1')
    if r['portion_g'] is None and r.get('portion')==100: r['portion']=None; r['portion_source']='unknown'
    if r['portion_g']:
        r['portion']=r['portion_g']; _f2=r['portion']/sz if sz else None
        r['pPor']=round(r['price']*_f2,2) if _f2 and r.get('price') else None
        for _a,_b,_d in (('protPor','p100',1),('kcalPor','kcal',0),('saltPor','salt',2)):
            r[_a]=round(r[_b]*r['portion']/100,_d) if r.get(_b) is not None else None
        r['saltPct']=round(r['saltPor']/6*100) if r['saltPor'] is not None else None
    r['meal_check']=_x.get('meal_check')
    if _x.get('gang')=='dessert': r['gang']='dessert'
    if _x.get('gang')=='frühstück': r['gang']='frühstück'; r['rankable']=False
    if _x.get('gang_hint')=='vorspeise' and r.get('gang') in ('haupt','beilage'): r['gang']='vorspeise'  # hourly 2026-10-16T18: source course (bofrost Vorspeisen/Snacks)
    if _x.get('segment')=='grocery': r['segment']='grocery'
    if _x.get('segment')=='baby_food': r['segment']='baby_food'; r['rankable']=False  # review 13 E
    if r.get('dry') or r.get('nutrition_basis')=='dry' or stg not in ('meal','stew') or r.get('gang')=='dessert' or r.get('segment')=='grocery' or r.get('meal_class')!='meal' or not (_x.get('meal_check') or {}).get('ok'): r['rankable']=False
    if _x.get('component_kind') in ('breaded','topped_fish','meat_sub','meat_piece'): stg='prot'; r['stage']='prot'  # sensecheck 11/13: 'Zum Kombinieren'
    r['component']=bool(_x.get('component')) or stg=='prot'
    if r.get('segment')=='meal_kit':
        if not r.get('store') or str(r['store']).startswith('unbekannt'):
            _b=str(_x.get('brand') or _x.get('store') or r.get('brand') or '')
            r['store']='HelloFresh' if 'hellofresh' in _b.lower() else ('Marley Spoon' if 'marley' in _b.lower() else r.get('store'))
    for _k in ('delivers_4020','delivery_source','allergens'):
        if r.get(_k) is None and _x.get(_k) is not None: r[_k]=_x[_k]
    if isinstance(r.get('allergens'),str): r['allergens']=[a.strip() for a in re.split(r'[;,]',r['allergens']) if a.strip()]
    # unified value formula (Connector UI src/app/meal.ts @6b5f97a): w*score+(1-w)*min((prot_portion/eur_portion)/20,1)*100, w=0.5
    _mc=r.get('meal_check') or {}
    r['rankable']=bool(r['rankable']) and bool(_mc.get('ok')) and 400<=(_mc.get('kcal') or 0)<=900 and (_mc.get('protein') or 0)>=20 \
        and r.get('score') is not None and r['score']>=30 and bool(r.get('price')) and bool(r.get('store')) and not str(r.get('store')).startswith('unbekannt') \
        and r.get('gang')!='dessert' and r.get('meal_class') not in ('snack_side','baby') and r.get('segment') not in ('meal_kit','grocery','baby_food') and not r['component'] and not r.get('nonfood')
    _ppor=(_mc.get('protein') or 0); _epor=(r['price']*_mc['portion']/r['size']) if r['rankable'] and r.get('size') and _mc.get('portion') else (r['price'] if r['rankable'] else None)
    if r.get('store') in SHIP and r.get('pPor') is not None:
        r['shipPor']=round(SHIP[r['store']]/SHIP_BOX,2); r['pPorEff']=round(r['pPor']+r['shipPor'],2)
    elif r.get('store') in MEALPREP_ONLY|{'bofrost','Alfies'} and r.get('store') not in SHIP: _NOSHIP.add(r.get('store'))
    if _epor and r.get('shipPor'): _epor=_epor+r['shipPor']
    r['pli']=round(0.5*r['score']+0.5*min((_ppor/_epor)/20,1)*100,1) if r['rankable'] and _epor else None
    if r['pli'] is None: r['rankable']=False
    if r['rankable'] and r['score']<50 and _ppor/_epor>=20: r['badge']='Preis-Sieger, Gesundheit mittel'  # review 13 G
CATICON={n:i for n,i,_ in PROT+DISH}; CATICON.update({'vegan':'🌿','vegetarisch':'🥦','Beilage/Gemüse':'🥦'})
idx={id(r):r['id'] for r in R}
# sides
S2=json.load(open('sides_billa.json'))
sides=[]
for j,x in enumerate(S2):
    g=x['portion_g']; k=x['kcal_100'] or 0; p=x['protein_100'] or 0
    sides.append(dict(id=j,name=x['name'],brand=x['brand'],role=x['side_role'],img=x['image_url'],url=x['url'],price=x['price_eur'],size=x['size_g'],portion=g,
      kcal=round(k*g/100),prot=round(p*g/100,1),fib=round((x['fiber_100'] or 0)*g/100,1),salt=round((x['salt_100'] or 0)*g/100,2),
      cost=round(x['price_eur']*g/x['size_g'],2) if x['size_g'] else None,mp=x['instantpot'],k100=x['kcal_100'],p100=x['protein_100'],cat=x['category']))
# expand.json Beilage/Gemüse
import os
if os.path.exists('expand.json'):
    EX=json.load(open('expand.json')); EX=EX if isinstance(EX,list) else EX.get('products',[])
    seen={s['name'] for s in sides}; j=len(S2)
    for x in EX:
        nm=x.get('name') or ''; cat=str(x.get('category') or '')
        if not re.search(r'beilage|gemüse|salat|reis',cat,re.I) or nm in seen: continue
        if re.search(r'erdbeer|marillen|nougat|germ|zwetschk|topfen|mohn|schoko|donut|eisknödel|lasagne|tortell|ravioli|pizza',nm,re.I): continue
        k=x.get('kcal_100'); pr=x.get('price_eur'); sz=x.get('size_g')
        if not k or not pr or not sz: continue
        role='salad' if re.search(r'salat',nm+cat,re.I) else 'veg' if re.search(r'gemüse|brokkoli|broccoli|fisolen|erbsen|spinat|karfiol|kohl|kraut|bohnen|linsen|kichererb|ratatouille|paprika|zucchini',nm,re.I) else 'side'
        g={'veg':200,'salad':100}.get(role,75 if re.search(r'reis',nm,re.I) and k>300 else 150)
        p=x.get('protein_100') or 0
        sides.append(dict(id=j,name=nm,brand=x.get('brand'),role=role,img=x.get('image_url'),url=x.get('url'),price=pr,size=sz,portion=g,kcal=round(k*g/100),prot=round(p*g/100,1),fib=round((x.get('fiber_100') or 0)*g/100,1),salt=round((x.get('salt_100') or 0)*g/100,2),cost=round(pr*g/sz,2),mp=x.get('instantpot') or '',k100=k,p100=p,cat=cat,store=x.get('store')))
        j+=1; seen.add(nm)
sides=[s for s in sides if s['cost'] and s['kcal']>0]
# sensecheck 6: baby/infant food never as a side (HiPP etc. by brand OR name; plain veg like 'Babykarotten' stays)
_BABY_SIDE=re.compile(r'\b(hipp|alete|bebivita|beba|aptamil|babylove|freche freunde)\b|babynahrung|beikost|gläschen|kleinkind|säugling|ab dem \d+\.? ?monat|\bbaby\b',re.I)
_n_side_baby=len(sides); sides=[s for s in sides if not _BABY_SIDE.search((s.get('name') or '')+' '+(s.get('brand') or ''))]; _n_side_baby-=len(sides)
print('sides: baby-food excluded',_n_side_baby)
# sensecheck 6b: dry Knorr/Maggi Kochbeutel / instant mixes never as sides (ready-meal sides only)
_DRY_SIDE=re.compile(
    r'\b(knorr|maggi)\b.*(kochbeutel|semmelknödel|knödel halb|spaghetteria|pasta snack|cup[- ]?a[- ]?soup|asia noodles|bitte zu tisch|quick soup|hüttensnack|instant)|'
    r'kochbeutel.*\b(knorr|maggi)\b',
    re.I)
_n_side_dry=len(sides); sides=[s for s in sides if not _DRY_SIDE.search((s.get('name') or '')+' '+(s.get('brand') or ''))]; _n_side_dry-=len(sides)
print('sides: dry Knorr/Maggi excluded',_n_side_dry)
# sensecheck 7: sides = ready-to-combine Beilagen only — no desserts, no main meals / soup inserts,
# no dry staples (flakes, bread cubes, dry pasta, croutons; plain rice stays at 75 g dry portion), no duplicates
_RICE_SIDE=re.compile(r'reis|basmati|jasmin',re.I)
for _s in sides:  # dry rice whose name lacks 'reis' (e.g. 'Basmati Weiss') got the 150 g default portion
    if _s['role']=='side' and (_s['k100'] or 0)>300 and _RICE_SIDE.search(_s['name'] or '') and _s['portion']!=75:
        _g=75; _s['portion']=_g; _s['kcal']=round(_s['k100']*_g/100); _s['prot']=round((_s['p100'] or 0)*_g/100,1)
        _s['cost']=round(_s['price']*_g/_s['size'],2) if _s['size'] else _s['cost']
_DESSERT_SIDE=re.compile(r'milchreis|germknödel|kaiserschmarrn|marillen|zwetschk|topfenknödel|mohn|nougat|schoko|palatschink|strudel',re.I)
_MAIN_SIDE=re.compile(r'(wurst|fleisch|selchfleisch|grammel|kaspress|leber|spinat[- ]?(feta|käse)?|käse)[- ]?knödel|knödl\b|kasnudl|pizza|suprema|ristorante|tonno|feine küche|paprika-?huhn|simply good\b.*\bbowl\b',re.I)
_DRYSTAPLE_SIDE=re.compile(r'knödelbrot|backerbsen|gnocchi n\.? ?\d|gnocchi sardi|my risotto|erdäpfelteig|püree',re.I)
def _side_bad(_s):
    t=(_s.get('name') or '')+' '+(_s.get('brand') or '')
    if _DESSERT_SIDE.search(t): return 'dessert'
    if _MAIN_SIDE.search(t): return 'main'
    k=_s.get('k100') or 0
    if (_DRYSTAPLE_SIDE.search(t) and k>=250) or (k>=300 and not _RICE_SIDE.search(_s.get('name') or '')): return 'dry'
    if (_s.get('kcal') or 0)>450: return 'dry'
    return None
from collections import Counter as _C
_why=_C(); _keep=[]
for _s in sides:
    _b=_side_bad(_s)
    if _b: _why[_b]+=1
    else: _keep.append(_s)
_best={}
for _s in _keep:
    _k=re.sub(r'\s+',' ',(_s['name'] or '').lower().replace('’',"'")).strip()
    if _k not in _best or (_s['cost'] or 9e9)<(_best[_k]['cost'] or 9e9): _best[_k]=_s
_why['dup']=len(_keep)-len(_best)
sides=[_s for _s in _keep if _best.get(re.sub(r'\s+',' ',(_s['name'] or '').lower().replace('’',"'")).strip()) is _s]
print('sides: sensecheck7 excluded',dict(_why),'->',len(sides))
veg=[s for s in sides if s['role']=='veg' and s['k100']<130]
sal=[s for s in sides if s['role']=='salad']
sd=[s for s in sides if s['role']=='side']
combos=[]
mains=sorted([r for r in R if r['rankable'] and r['protpack'] and 25<=r['protpack']<=80 and r['kcalpack'] and r['kcalpack']<=750 and r['price'] and r['pstat']=='live 2026' and r['score']],key=lambda r:-r['score'])
used=_C()
for m in mains:
    hascarb=bool(re.search(r'reis|kartoffel|erdäpfel|püree|nudel|pasta|spätzle|knödel|gnocchi|lasagne|tortell|bowl',m['name'],re.I))
    best=None
    for v in veg+sal:
        for s in ([None] if hascarb else sd):
            kc=m['kcalpack']+v['kcal']+(s['kcal'] if s else 0)
            if not 500<=kc<=900: continue
            pr=m['protpack']+v['prot']+(s['prot'] if s else 0)
            cost=m['price']+v['cost']+(s['cost'] if s else 0)
            sc=pr/kc*100*3 + v['fib']*2 - cost*0.5 - 3*used[v['id']] - (3*used[s['id']] if s else 0)  # sensecheck 7: count-based reuse penalty (was flat 2 -> 22/24 combos 'Iglo Erbsen')
            if not best or sc>best[0]: best=(sc,v,s,kc,pr,cost)
    if best:
        _,v,s,kc,pr,cost=best; used[v['id']]+=1
        if s: used[s['id']]+=1
        combos.append(dict(main=m['id'],veg=v['id'],side=s['id'] if s else None,kcal=round(kc),prot=round(pr),price=round(cost,2),fib=round(v['fib']+(s['fib'] if s else 0),1)))
    if len(combos)>=24: break
# --- pizza line names (Orchestrator 2026-10-14): one product name across stores. MPreis lists 'Dr. Oetker Ristorante Tonno',
#  Billa/Spar/Gurkerl 'Dr. Oetker Ristorante Pizza Tonno' (same GTIN 4001724038993) → canonical '<Brand> <Line> Pizza <Variant>';
#  then a missing EAN/photo/nutrition is filled from a same-brand twin with identical core name + size (each store keeps its own price).
_PZ_LINE=re.compile(r'^(dr\.? ?oetker (?:ristorante|tradizionale|suprema|die ofenfrische|la mia grande|bistro))\s+(?!pizza\b|flammkuchen|baguette|calzone|piccola)(.+)$',re.I)
_n_pzname=0
for _r in R:
    _nm=re.sub(r'\s*\(tiefgekühlt\)\s*$','',_r.get('name') or '',flags=re.I); _nm=re.sub(r'\bQuatro\b','Quattro',_nm)
    _mm=_PZ_LINE.match(_nm)
    if _mm: _nm=f"{_mm.group(1)} Pizza {_mm.group(2)}"
    if _nm!=_r.get('name'): _r.setdefault('name_raw',_r.get('name')); _r['name']=_nm; _n_pzname+=1
def _pz_key(r):
    b=(r.get('brandN') or r.get('brand') or '').split(',')[0].strip().lower(); nm=(r.get('name') or '').lower()
    if not b or not re.search(r'\bpizza\b|ristorante|suprema|ofenfrische',nm): return None
    nm=re.sub(r'[^a-z0-9äöüß]+','',nm.replace(b,'')); return (b,nm,int(r['size']) if r.get('size') else None)
_pz={}
for _r in R:
    k=_pz_key(_r)
    if k and k[2]: _pz.setdefault(k,[]).append(_r)
_n_pzfill=0
for k,grp in _pz.items():
    eans={g.get('ean') for g in grp if g.get('ean')}
    if len(eans)!=1 or len(grp)<2: continue
    e=next(iter(eans)); donor=next(g for g in grp if g.get('ean')==e)
    for g in grp:
        if not g.get('ean'): g['ean']=e; g['ean_source']='twin '+str(donor.get('store')); _n_pzfill+=1
        if not g.get('img') and donor.get('img'): g['img']=donor['img']
print('pizza names canonical',_n_pzname,'ean filled from twin',_n_pzfill)
# --- baby/dry-fix exclusion + exact/GTIN/near dedupe + light_meal + cross-store collapse ---
_BABY=re.compile(r'hipp|beba|aptamil|alete|babylove|ab dem \d|kleinkind|säugling|\bbaby\b|kinder ?menü|bio-?gläschen',re.I)
_DRYFIX=re.compile(r'\bfix\b|bouillon.?w(?:ü|u)rfel|paradiescreme|maggi.*suppe|knorr basis',re.I)
_NOISE=re.compile(r'(tiefgekühl\w*|tiefkuehl\w*|\btk\b|\bbio\b|\bdie\b|\bder\b|\bdas\b|\bmit\b|\bund\b|\bpizza\b|\bmenü\b|\bfertiggericht\b|\bveggie\b|\bvegan\b|\bhack\b)',re.I)
_n_baby=0
for _r in R:
    if not _BABY.search(_r.get('name') or ''): continue
    _r['meal_class']='baby'; _r['segment']='baby_food'; _r['nonfood']=True
    _r['rankable']=False; _r['pli']=None; _r['pliLight']=None
    _r['flags']=(_r.get('flags') or [])+['Kindernahrung (kein Fertiggericht-Ranking)']
    _n_baby+=1
def _prod_key(r):
    e=str(r.get('ean') or '').lstrip('0')
    if e and e.isdigit() and len(e)>=8: return 'e:'+e
    m=re.search(r'/product/(\d{8,14})',r.get('url') or '')
    if m: return 'g:'+m.group(1).lstrip('0')
    b=(r.get('brandN') or r.get('brand') or '').split(',')[0].strip().lower()
    n=(r.get('name') or '').lower()
    if b and b in n: n=n.replace(b,'')
    n=_NOISE.sub(' ',n); n=re.sub(r'\d+[.,]?\d*\s*g\b',' ',n)
    n=re.sub(r'[^a-z0-9äöüß]+','',n); b2=re.sub(r'[^a-z0-9äöüß]+','',b)
    sz=str(int(r['size'])) if r.get('size') else ''
    return 'n:'+b2+':'+n+':'+sz
def _near_key(r):
    """Brand+core name without size — collapses OFF/store twins like Lotao Chili 320/350 g."""
    e=str(r.get('ean') or '').lstrip('0')
    if e and e.isdigit() and len(e)>=8: return 'e:'+e
    m=re.search(r'/product/(\d{8,14})',r.get('url') or '')
    if m: return 'g:'+m.group(1).lstrip('0')
    b=(r.get('brandN') or r.get('brand') or '').split(',')[0].strip().lower()
    n=(r.get('name') or '').lower()
    if b and b in n: n=n.replace(b,'')
    n=_NOISE.sub(' ',n); n=re.sub(r'\d+[.,]?\d*\s*g\b',' ',n)
    n=re.sub(r'[^a-z0-9äöüß]+','',n); b2=re.sub(r'[^a-z0-9äöüß]+','',b)
    return 'n:'+b2+':'+n
def _exact_key(r):
    return ((r.get('name') or '').strip().lower(),(r.get('store') or '').strip().lower(),r.get('size'))
def _is_off(r):
    s=str(r.get('store') or '')
    return (not s) or s.startswith('unbekannt')
def _size_close(a,b,tol=0.12):
    if not a or not b: return True
    a,b=float(a),float(b)
    return abs(a-b)/max(a,b)<=tol
def _cluster_by_size(vs):
    """Group rows whose pack size is missing or within ±12% (Lotao 320/350; not 400/800)."""
    clusters=[]
    for r in vs:
        placed=False
        for c in clusters:
            if any(_size_close(r.get('size'),x.get('size')) for x in c):
                c.append(r); placed=True; break
        if not placed: clusters.append([r])
    return [c for c in clusters if len(c)>=2]
def _demote_dups(groups, flag, prefer, only_off_or_same_store=False, size_gate=False):
    n=0
    for vs in groups.values():
        if len(vs)<2: continue
        if only_off_or_same_store:
            offs=[r for r in vs if _is_off(r)]
            by_store={}
            for r in vs:
                if _is_off(r): continue
                by_store.setdefault((r.get('store') or '').lower(),[]).append(r)
            buckets=[]
            if len(offs)>=2: buckets.append(offs)
            if offs and len(vs)>len(offs):
                for r in offs:
                    r['rankable']=False; r['pli']=None; r['pliLight']=None
                    r['flags']=(r.get('flags') or [])+[flag+' (OFF-twin)']; n+=1
            for store_vs in by_store.values():
                if len(store_vs)>=2: buckets.append(store_vs)
        else:
            buckets=[vs]
        for bucket in buckets:
            parts=_cluster_by_size(bucket) if size_gate else [bucket]
            for part in parts:
                part=sorted(part,key=prefer)
                for r in part[1:]:
                    r['rankable']=False; r['pli']=None; r['pliLight']=None
                    r['flags']=(r.get('flags') or [])+[flag]; n+=1
    return n
_pref=lambda r:(0 if r.get('kcal') is not None else 1, 0 if r.get('ean') else 1, r.get('price') is None, r.get('price') or 999, 0 if r.get('url') else 1)
_by_ex={}; _by_ean={}; _by_near={}
for _r in R:
    _by_ex.setdefault(_exact_key(_r),[]).append(_r)
    _e=str(_r.get('ean') or '').lstrip('0')
    if _e and _e.isdigit() and len(_e)>=8: _by_ean.setdefault('e:'+_e,[]).append(_r)
    _nk=_near_key(_r)
    if _nk.startswith('n:') and _nk.count(':')>=2 and len(_nk.split(':')[-1])>=8:
        _by_near.setdefault(_nk,[]).append(_r)
_n_exact=_demote_dups(_by_ex,'Duplikat (gleicher Name/Laden/Größe)',_pref,False)
_n_ean=_demote_dups(_by_ean,'Duplikat (gleiche GTIN/EAN)',_pref,True)
_n_near=_demote_dups(_by_near,'Duplikat (nahe Name/Marke, Ranking)',_pref,True,True)
# same-store GTIN twins (Sensecheck 5): keep the preferred row, hide the twin from listings via dupOf
_n_samestore=0; _ss={}
for _r in R:
    _e=str(_r.get('ean') or '').lstrip('0')
    if _e and _e.isdigit() and len(_e)>=8: _ss.setdefault(((_r.get('store') or '').lower(),_e),[]).append(_r)
for _vs in _ss.values():
    if len(_vs)<2: continue
    _vs=sorted(_vs,key=_pref)
    for _r in _vs[1:]:
        if _r.get('dupOf') is None:
            _r['dupOf']=_vs[0]['id']; _r['rankable']=False; _r['pli']=None; _r['pliLight']=None; _n_samestore+=1
print('same-store GTIN twins hidden',_n_samestore)
# sensecheck 13: same shop + same product URL + same product name but different pack size/price (29 groups, e.g. BILLA Lasagne
#  Bolognese 700 g/4,99 € + 400 g/3,19 € on one URL; live shop shows only 400 g). heisse-preise 'canonical' keeps retired sizes.
#  Keep ONE row per (store, url, core name): a row with a real pack size first, then the most recent price date (live-verified size), then a row whose own name/URL
#  states its size ('Felix Chili con Carne 400 G'), then the usual preference. Twins get dupOf → hidden + not ranked.
#  Different products on one listing URL (wokostswas.at/k54/…) have different core names and are left alone.
_SZ_RE=re.compile(r'\b\d+[.,]?\d*\s*(g|kg|ml|l)\b|\b\d+\s*(portionen|portion|stück|stk)\b|\(\s*xl[^)]*\)',re.I)
def _url_core(r):
    n=(r.get('name') or '').lower(); n=_SZ_RE.sub(' ',n)
    return re.sub(r'[^a-z0-9äöüß]+','',n)
def _same_core(a,b):
    if a==b: return True
    s,l=sorted((a,b),key=len)
    return len(s)>=5 and l.endswith(s)  # 'goodchoicehotdog' vs 'hotdog', 'suppenwurfelklarerindsuppe' vs 'klarerindsuppe'
def _size_stated(r):
    sz=r.get('size')
    if not sz: return False
    t=((r.get('name') or '')+' '+(r.get('url') or '')).lower()
    return bool(re.search(r'(?<![\d.,])%d\s*-?\s*g\b'%int(sz),t))
def _url_pref(r):
    return (0 if (r.get('size') or 0)>=50 else 1, -(int(str(r.get('price_date') or '0000-00-00').replace('-','')[:8] or 0)), 0 if _size_stated(r) else 1, 0 if r.get('pstat') in ('live 2026','aktuell') else 1)+_pref(r)
_n_sameurl=0; _su={}
for _r in R:
    _u=_r.get('url')
    if _u and not _is_off(_r): _su.setdefault(((_r.get('store') or '').lower(),_u),[]).append(_r)
SAMEURL_GROUPS=[]
for _vs in _su.values():
    if len(_vs)<2: continue
    _cl=[]
    for _r in _vs:
        _c=_url_core(_r)
        for g in _cl:
            if _same_core(_c,g[0]): g[1].append(_r); break
        else: _cl.append((_c,[_r]))
    for _c,_g in _cl:
        if len(_g)<2: continue
        _g=sorted(_g,key=_url_pref); _keep=_g[0]
        if _keep.get('dupOf') is not None:  # keeper already hidden as GTIN twin → point at its master
            _keep=next((x for x in R if x['id']==_keep['dupOf']),_keep)
        SAMEURL_GROUPS.append([x['id'] for x in _g])
        for _r in _g[1:]:
            if _r is _keep or _r.get('dupOf') is not None: continue
            _r['dupOf']=_keep['id']; _r['rankable']=False; _r['pli']=None; _r['pliLight']=None
            _r['flags']=(_r.get('flags') or [])+[f"Duplikat (gleiche Shop-URL, andere Größe/Preis – {int(_keep['size']) if _keep.get('size') else '?'} g behalten)"]
            _n_sameurl+=1
print('same-store same-URL twins hidden',_n_sameurl,'groups',len(SAMEURL_GROUPS))
_light=[]
for _r in R:
    if _r.get('meal_class') in ('baby','dessert','dry','snack_side'): continue
    if _r.get('segment')=='baby_food' or _r.get('nonfood') or _r.get('dupOf') is not None: continue  # sensecheck 13: hidden twins never enter topLight
    if _r.get('meal_class')!='light_meal': continue
    _mc=_r.get('meal_check') or {}; _k,_p=_mc.get('kcal'),_mc.get('protein')
    if not (_k and 300<=_k<400): continue
    if _r.get('dry') or _r.get('nutrition_basis')=='dry' or _r.get('gang') in ('dessert','vorspeise','frühstück'): continue  # sensecheck 11: no starters in topLight
    if _r.get('segment') in ('grocery','meal_kit','baby_food') or _r.get('component') or _r.get('stage') not in ('meal','stew'): continue
    if not _r.get('score') or _r['score']<30 or not _r.get('price') or not _r.get('store'): continue
    if str(_r['store']).startswith('unbekannt') or _r.get('pstat') not in ('live 2026','aktuell'): continue
    if _BABY.search(_r.get('name') or '') or _DRYFIX.search(_r.get('name') or ''): continue
    _ep=(_r['price']*_mc['portion']/_r['size']) if _r.get('size') and _mc.get('portion') else _r['price']
    if not _ep or _p is None: continue
    if _r.get('shipPor'): _ep=_ep+_r['shipPor']  # review 13 F(b)
    _r['pliLight']=round(0.5*_r['score']+0.5*min((_p/_ep)/20,1)*100,1); _light.append(_r)
_TWIN_NOISE=re.compile(r"\bmsc\b|\basc\b|pazifisch\w*|käpt'?n|\b\d+\s*(stück|stk)\b|\b\d+er[- ]?(packung|pack)\b|\(tiefgekühlt\)",re.I)
def _twin_keys(r):
    """Sensecheck 9: one product = one top-list slot across stores. The EAN key alone misses twins where only one
    store row carries the GTIN (MPreis 'Ristorante Tonno' w/ EAN vs Billa 'Ristorante Pizza Tonno' w/o), so a
    brand+core-name+size key (MSC/'Pazifischer'/'4 Stück' stripped: Iglo Polar-Dorsch ×3 stores) is checked too."""
    ks={_prod_key(r)}
    b=(r.get('brandN') or r.get('brand') or '').split(',')[0].strip().lower()
    nm=(r.get('name') or '').lower()
    if b and b in nm: nm=nm.replace(b,'')
    nm=_TWIN_NOISE.sub(' ',_NOISE.sub(' ',nm)); nm=re.sub(r'\d+[.,]?\d*\s*g\b',' ',nm)
    nm=re.sub(r'[^a-z0-9äöüß]+','',nm); b2=re.sub(r'[^a-z0-9äöüß]+','',b)
    if b2 and len(nm)>=8: ks.add('t:'+b2+':'+nm+':'+(str(int(r['size'])) if r.get('size') else ''))
    return ks
_XL=re.compile(r'\(\s*xl[^)]*\)|\bxl\b|\(\s*\d+[.,]?\d*\s*(g|kg)\s*\)|\(?\s*\b\d+\s*portion(en)?\b\s*\)?',re.I)  # sensecheck 52 P2: '2 Portionen' also without brackets (#432/#431)
def _variant_key(r):
    """review 13 F(a): provider + name without '(XL, 2 Portionen)' / '(500 g)' → one slot per dish."""
    return (r.get('store'),re.sub(r'[^a-z0-9äöüß]+','',_XL.sub(' ',(r.get('name') or '').lower())))
PROVIDER_CAP=10
def _collapse(cands,score_fn,n=30,cap=PROVIDER_CAP):
    """returns (capped top-n, collapsed count, uncapped top-n). Twins across stores and XL/single variants share one slot;
    at most `cap` slots per provider in the capped list (review 13 F(c)); uncapped list feeds the UI 'ohne Limit' toggle."""
    ordered=sorted(cands,key=score_fn,reverse=True); seen={}; vseen={}; ded=[]; collapsed=0; also={}
    for r in ordered:
        ks=_twin_keys(r); hit=next((seen[k] for k in ks if k in seen),None)
        if hit is not None:
            collapsed+=1; also.setdefault(hit['id'],set()).add(r['store'])
            for k in ks: seen.setdefault(k,hit)
            continue
        vk=_variant_key(r)
        if vk in vseen:
            collapsed+=1; kv=vseen[vk]
            kv['variant_note']='auch als XL' if _XL.search(r.get('name') or '') and 'xl' in (r.get('name') or '').lower() else 'auch als Einzelportion'
            kv.setdefault('variantIds',[]).append(r['id'])
            for k in ks: seen.setdefault(k,kv)  # sensecheck 52 P2: folded variant's twin keys point at the kept row (#431 -> #960)
            continue
        vseen[vk]=r
        for k in ks: seen[k]=r
        ded.append(r)
        if len(ded)>=n*4: break
    cnt={}; capped=[]
    for r in ded:
        if cnt.get(r.get('store'),0)>=(cap(r.get('store')) if callable(cap) else cap): continue  # sensecheck 50: per-store cap (ship-box providers 6)
        cnt[r.get('store')]=cnt.get(r.get('store'),0)+1; capped.append(r)
        if len(capped)>=n: break
    unc=ded[:n]
    for r in set(map(id,capped))|set(map(id,unc)): pass
    for r in capped+unc:
        o=sorted(s for s in also.get(r['id'],()) if s and s!=r.get('store'))
        if o: r['alsoAt']=o
    return capped,collapsed,unc
# sensecheck 10: vorspeise (e.g. Knorr Meisterkessel Bohnen-Speck-Suppe) is a starter, not a main-meal top-list winner
topPLI,_c_pli,_utopPLI=_collapse([r for r in R if r.get('rankable') and r.get('pli') is not None and r.get('gang')!='vorspeise'],lambda r:r['pli'])
top_h,_c_h,_utop_h=_collapse([r for r in R if r.get('rankable') and r.get('score') is not None and r.get('gang')!='vorspeise'],lambda r:r['score'])
top_pe,_c_pe,_utop_pe=_collapse([r for r in R if r.get('rankable') and r.get('ppe') and r.get('pstat')=='live 2026' and r.get('pack')!='Trocken/Instant' and r.get('gang')!='vorspeise'],lambda r:r['ppe'])
topLight,_c_light,_utopLight=_collapse(_light,lambda r:r['pliLight'])
print('review13 no shipping known (left as is):',sorted(x for x in _NOSHIP if x)); print('rankings: light',len(_light),'baby',_n_baby,'exact_dup',_n_exact,'ean_dup',_n_ean,'near_dup',_n_near,'collapsed pli/h/pe/light',_c_pli,_c_h,_c_pe,_c_light)
import os
qa=json.load(open('qa_stats.json')) if os.path.exists('qa_stats.json') else None
# Hersteller
PROF={p['slug']:p for p in json.load(open('analysis/producer_profiles.json'))} if os.path.exists('analysis/producer_profiles.json') else {}
COMP=json.load(open('analysis/companies.json')) if os.path.exists('analysis/companies.json') else []
def lp(c): return ('analysis/logos/'+c['logo_path'].split('/')[-1]) if c.get('logo_path') else None
nid=lambda c: re.sub(r'[^A-Z0-9]','',str(c).upper().replace('EU','EG'))
code2slug={}
for c in COMP:
    for pa in c.get('plant_addresses') or []:
        if pa.get('approval_code'): code2slug[nid(pa['approval_code'])]=c['slug']
for p in PROF.values():
    ic=(p.get('facts') or {}).get('identitaetskennzeichen')
    if ic:
        for part in re.split(r'[;,/]',str(ic)): code2slug.setdefault(nid(part),p['slug'])
for r in R:
    r['prodSlug']=None
    for part in re.split(r',',str(r.get('pid') or '')):
        if part.strip() and nid(part) in code2slug: r['prodSlug']=code2slug[nid(part)]; break
# producers_v2 (pro Produkt)
P2=None
if os.path.exists('producers_v2.json'):
    P2=json.load(open('producers_v2.json'))
    rows2=P2 if isinstance(P2,list) else P2.get('products') or P2.get('items') or []
    byk={}
    for y in rows2:
        for k in [y.get('url'),y.get('id'),(y.get('name') or '').strip().lower()]:
            if k: byk[k]=y
    for r in R:
        y=byk.get(r['url']) or byk.get(r['name'].strip().lower())
        if y:
            r['p2']={k:y.get(k) for k in ['producer','plant','town','confidence','evidence_url','meat_origin','producer_slug'] if y.get(k) is not None}
            if y.get('producer_slug') and not r['prodSlug']: r['prodSlug']=y['producer_slug']
    if isinstance(P2,dict):
        for p in P2.get('profiles') or []:
            if p.get('slug') and p['slug'] not in PROF: PROF[p['slug']]=p
producers=[]
cbyslug={c['slug']:c for c in COMP}
for slug in sorted(set(list(PROF)+[c['slug'] for c in COMP if c['type']=='producer'])):
    p=PROF.get(slug,{}); c=cbyslug.get(slug,{})
    producers.append(dict(legal=c.get('name'),slug=slug,name=p.get('name') or c.get('name'),summary=p.get('summary_de'),facts=p.get('facts'),sources=p.get('sources'),brands=p.get('brands_supplied') or [],website=c.get('website') or (p.get('facts') or {}).get('website'),logo=lp(c) if c else None,plants=c.get('plant_addresses') or [],group=c.get('group'),retail=c.get('retail_brands') or [],ids=[r['id'] for r in R if r['prodSlug']==slug]))
companyLogos={c['slug']:lp(c) for c in COMP if lp(c)}
out=dict(producers=producers,companyLogos=companyLogos,qaStats=qa,catIcon=CATICON,catProt=[n for n,_,_ in PROT]+['vegan','vegetarisch'],catDish=[n for n,_,_ in DISH]+['Beilage/Gemüse'],topPLI=[r['id'] for r in topPLI],topLight=[r['id'] for r in topLight],topPLIUncapped=[r['id'] for r in _utopPLI],topLightUncapped=[r['id'] for r in _utopLight],topHealthUncapped=[r['id'] for r in _utop_h],topPEUncapped=[r['id'] for r in _utop_pe],topCap=dict(perProvider=PROVIDER_CAP,n=30,shipBox=SHIP_BOX),rows=R,sides=sides,topHealth=[idx[id(r)] for r in top_h],topPE=[idx[id(r)] for r in top_pe],stats=S,
  same=[dict(code=v[0]['pid'],herst=v[0]['herst'],ort=v[0]['ort'],ooe=v[0]['ooe'],ids=[idx[id(r)] for r in v]) for k,v in same],
  ftg=[dict(name=n,n=len(L),price=md(L,'price'),prot=md(L,'protpack'),kcal=md(L,'kcalpack'),ppe=md(L,'ppe'),p100k=md(L,'p100k')) for n,L in cmp],
  combos=combos,generated='2026-10-12')
for r in R: r.pop('pid_norm',None)
# --- logo override from analysis/logos.json brand aliases (v3 logos) ---
try:
    _LJ=json.load(open('analysis/logos.json')); _BM={}
    for _k,_v in _LJ.items():
        if _v.get('file'):
            for _b in (_v.get('brands') or [])+[_v.get('name') or '']:
                if _b: _BM[_b.lower()]='analysis/'+_v['file']
    _AL={'billa bio':'billa bio','s-budget':'s-budget','good choice':'good choice'}
    for _r in out['rows']:
        for _c in [(_r.get('brandN') or '').lower(),(_r.get('brand') or '').split(',')[0].strip().lower()]:
            if _c in _BM: _r['logo']=_BM[_c]; break
except Exception as _e: print('logo override failed',_e)

# --- SC15..SC48 canonical state + dynamic SC49+ recomputation ---
# sensecheck 50: ship-box providers (minimum box / parcel shipping) get topCap.shipBox slots instead of perProvider
SC50_SHIPBOX_STORES = frozenset(MEALPREP_ONLY | {'HelloFresh', 'Marley Spoon', 'Hofmann'})
def _sc50_rank_guard(r):
    """sensecheck 50 F4: the reconcile path must apply the same ranking gates as SC15-SC48 (all 160 canonical rankable rows pass)."""
    k = r.get('kcalPor')
    return (r.get('score') is not None and r['score'] >= 30 and k is not None and 400 <= k <= 900
            and bool(r.get('price')) and not r.get('price_stale') and r.get('stage') in ('meal', 'stew')
            and not r.get('component') and r.get('segment') == 'ready_meal' and r.get('dupOf') is None
            and not any('Duplikat' in f for f in (r.get('flags') or [])))
def _reconcile_sc48(out):
    import hashlib, glob
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bpath = os.path.join(base_dir, 'sc48_baseline.json')
    if not os.path.exists(bpath):
        return out
    B = json.load(open(bpath))
    can = B['canonical_data']
    old_hashes = B.get('source_hashes', {})
    old_by_uid = old_hashes.get('by_uid', {})
    old_files = old_hashes.get('files', {})

    cur_by_uid = {}
    cur_items_by_uid = {}
    new_items = []
    for fn in ['connectors_new.json', 'online_mealprep.json', 'mealkits_src.json']:
        p = os.path.join(base_dir, fn)
        if os.path.exists(p):
            for it in json.load(open(p)):
                if it.get('_excluded'):
                    continue
                u = it.get('_uid')
                h = hashlib.sha256(json.dumps(it, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                if u:
                    cur_by_uid[u] = h
                    cur_items_by_uid[u] = it
                else:
                    new_items.append(it)

    cur_files = {}
    for pat in ['gaps_overlay.json', 'qa/*_fixes.json', 'analysis/online_availability_*.json', 'score_v2.py']:
        for p in sorted(glob.glob(os.path.join(base_dir, pat))):
            rel = os.path.relpath(p, base_dir)
            cur_files[rel] = hashlib.sha256(open(p, 'rb').read()).hexdigest()

    changed_uids = {u for u, h in cur_by_uid.items() if old_by_uid.get(u) != h}
    removed_uids = set(old_by_uid.keys()) - set(cur_by_uid.keys())
    files_changed = (cur_files != old_files)
    shipbox_on = os.environ.get('ENFORCE_SHIPBOX_CAP', '1') != '0'  # sensecheck 51: shipBox = 6 is the default; ENFORCE_SHIPBOX_CAP=0 reproduces 2484311
    topcap_changed = (out.get('topCap') != can.get('topCap')) or shipbox_on or bool(os.environ.get('SC50_FORCE_RECOMPUTE'))

    if not changed_uids and not removed_uids and not new_items and not files_changed and not topcap_changed:
        return can

    import score_v2 as V2
    rows = []
    ship_map = can.get('shipping') or {}
    for r in can['rows']:
        u = r['uid']
        if u in removed_uids:
            continue
        if u in changed_uids:
            it = cur_items_by_uid[u]
            r = dict(r)
            for src_k, dst_k in [
                ('name', 'name'), ('brand', 'brand'), ('store', 'store'),
                ('price_eur', 'price'), ('size_g', 'size'), ('url', 'url'),
                ('image_url', 'img'), ('kcal_100', 'kcal'), ('protein_100', 'prot'),
                ('fat_100', 'fat'), ('satfat_100', 'sat'), ('carbs_100', 'carb'),
                ('sugar_100', 'sug'), ('fiber_100', 'fib'), ('salt_100', 'salt'),
                ('ingredients', 'ing'), ('portion_g', 'portion_g'),
                ('portion_source', 'portion_source'), ('alsoAt', 'alsoAt'),
            ]:
                if src_k in it and it[src_k] is not None:
                    r[dst_k] = it[src_k]
            if 'available' in it:
                r['sold_out'] = not bool(it['available'])
            x_in = {
                'name': r.get('name'), 'size_g': r.get('size'), 'packaging': r.get('pack'),
                'kcal_100': r.get('kcal'), 'protein_100': r.get('prot'), 'fat_100': r.get('fat'),
                'satfat_100': r.get('sat'), 'carbs_100': r.get('carb'), 'sugar_100': r.get('sug'),
                'fiber_100': r.get('fib'), 'salt_100': r.get('salt'), 'ingredients': r.get('ing'),
                'store': r.get('store'),
            }
            v2 = V2.score_v2(x_in)
            if r.get('portion_g'):
                v2['portion_g'] = r['portion_g']
                v2['portion_source'] = r.get('portion_source') or v2.get('portion_source')
            mc = V2.meal_check(x_in, v2)
            r['score'] = v2.get('health_score')
            r['score_parts'] = v2.get('score_parts')
            r['meal_class'] = mc.get('cls')
            pg = r.get('portion_g') or v2.get('portion_g')
            sz = r.get('size')
            if pg and r.get('kcal') is not None:
                r['kcalPor'] = round(r['kcal'] * pg / 100)
            if pg and r.get('prot') is not None:
                r['protPor'] = round(r['prot'] * pg / 100, 1)
            if pg and sz and r.get('price'):
                r['pPor'] = round(r['price'] * pg / sz, 2)
                sh = r.get('shipPor') or 0.0  # sensecheck 50 F3: shipPor lives on the row, not in can['shipping']
                r['pPorEff'] = round(r['pPor'] + sh, 2)
            if r.get('sold_out'):
                r['rankable'] = False
            else:
                r['rankable'] = bool(mc.get('ok')) and not bool(r.get('linz_excluded')) and _sc50_rank_guard(r)
            if r.get('score') is not None and r.get('protPor') and r.get('pPorEff'):
                pe_s = min(100.0, (r['protPor'] / r['pPorEff']) * 5.0)
                if r.get('rankable'):
                    r['pli'] = round(0.5 * r['score'] + 0.5 * pe_s, 1)
                elif r.get('meal_class') == 'light_meal':
                    r['pli'] = None
                    r['pliLight'] = round(0.5 * r['score'] + 0.5 * pe_s, 1)
        rows.append(r)

    # Check latest online_availability_*.json
    av_files = sorted(glob.glob(os.path.join(base_dir, 'analysis/online_availability_*.json')))
    if os.environ.get('GOOD_CHOICE_AVAILABILITY'):  # sensecheck 52 P1: tests pin the snapshot the canonical baseline was built from
        av_files = [os.path.join(base_dir, 'analysis', os.environ['GOOD_CHOICE_AVAILABILITY'])]
    if av_files:
        av = json.load(open(av_files[-1]))
        av_fn = os.path.basename(av_files[-1])
        unav = set(av.get('unavailable_uids') or [])
        chk_date = (av.get('checked') or '')[:10]
        if av_fn != can['soldOut'].get('file') or unav != {x['uid'] for x in can['rows'] if x.get('sold_out')}:
            prev_unav = {x['uid'] for x in can['rows'] if x.get('sold_out')}
            for r in rows:
                if r['uid'] in unav:
                    r['sold_out'] = True
                    r['rankable'] = False
                    # sensecheck 53 P1: newly sold-out rows carry the same fields as the old ones (no stale PLI badge)
                    if os.environ.get('SC53_SOLDOUT', '1') != '0':
                        r['pli'] = None
                        r['pliLight'] = None
                        r['rank_excluded_reason'] = 'ausverkauft (Shop: nicht verfügbar)'
                        r['variant_note'] = 'ausverkauft'
                    if chk_date:
                        r['availability_checked'] = chk_date
                elif r['uid'] in prev_unav and r.get('sold_out') and not (r['uid'] in cur_items_by_uid and cur_items_by_uid[r['uid']].get('available') is False):
                    # sensecheck 50 F6: back in stock in the newer snapshot -> no longer sold out
                    r['sold_out'] = False
                    if r.get('rank_excluded_reason') == 'ausverkauft (Shop: nicht verfügbar)':
                        r['rank_excluded_reason'] = None
                    if r.get('variant_note') == 'ausverkauft':
                        r['variant_note'] = None
                    if chk_date:
                        r['availability_checked'] = chk_date
                    r['rankable'] = r.get('meal_class') == 'meal' and not bool(r.get('linz_excluded')) and _sc50_rank_guard(r)
                    # sensecheck 54 P1: back-in-stock rows get their PLI back (baseline carries pli=None for old sold-out rows)
                    if os.environ.get('SC54_BACKINSTOCK', '1') != '0':
                        if r.get('score') is not None and r.get('protPor') and r.get('pPorEff'):
                            _pe = min(100.0, (r['protPor'] / r['pPorEff']) * 5.0)
                            if r['rankable']:
                                r['pli'] = round(0.5 * r['score'] + 0.5 * _pe, 1)
                            elif r.get('meal_class') == 'light_meal':
                                r['pliLight'] = round(0.5 * r['score'] + 0.5 * _pe, 1)
                        changed_uids.add(r['uid'])
            can['soldOut'] = {
                'checked': av.get('checked'),
                'rows': len(unav),
                'was_ranked': av.get('was_ranked', can['soldOut'].get('was_ranked', 3)),
                'file': av_fn,
                'age_h': av.get('age_h', 0.1),
                'max_age_h': av.get('max_age_h', 48.0),
                'stale': bool(av.get('stale', False)),
            }

    can['rows'] = rows
    can['uidMap'] = {r['uid']: r['id'] for r in rows}

    # Recompute top lists if rows or topCap changed
    # sensecheck 50 F2 bug A: can['shipping'] uses the box size field (no minPortions key); bofrost delivers free with no minimum box
    ship_box_stores = set(SC50_SHIPBOX_STORES) | {k for k, v in (can.get('shipping') or {}).items()
                                                 if isinstance(v, dict) and (v.get('box') or 0) > 1 and (v.get('shipping_eur') or 0) > 0}
    cap_n = (can.get('topCap') or {}).get('n', 30)
    cap_prov = (can.get('topCap') or {}).get('perProvider', 10)
    cap_ship = (can.get('topCap') or {}).get('shipBox', 6) if shipbox_on else cap_prov

    def _recap(cand_ids):
        by_id = {r['id']: r for r in rows}
        cnt = {}
        res = []
        for rid in cand_ids:
            r = by_id.get(rid)
            if not r or not r.get('rankable'):
                continue
            st = r.get('store')
            lim = cap_ship if st in ship_box_stores else cap_prov
            if cnt.get(st, 0) >= lim:
                continue
            cnt[st] = cnt.get(st, 0) + 1
            res.append(rid)
            if len(res) >= cap_n:
                break
        return res

    # sensecheck 52 P3: PrepMyMeal lists the same dish twice under different handles/names (live-checked 2026-10-24 via
    #  prepmymeal.at/products/<handle>.js) and more_meals_norm.json carries size-less legacy rows of current dishes.
    #  Keep the cheaper/sized row, hide the twin via dupOf (not ranked, hidden in listings).
    # sensecheck 52 P4: MPreis 'Cevapcici Banja Luka' #1770 (no nutrition) is the same 800 g product as MPreis 'Cevapcici' #1769
    #  (with photo + 293 kcal/16 g P) and Billa 'Brajlovic Banja Luka Cevapcici' #455 → #1770 dupOf #1769, Billa twin note moves to #1769.
    #  SC52_DUPOF=0 reproduces the pre-P3/P4 export (baseline tests).
    if os.environ.get('SC52_DUPOF', '1') != '0':
        _rb = {r['id']: r for r in rows}
        for _d, _k, _st, _why in (
            (2859, 2854, 'PrepMyMeal', "Duplikat (PrepMyMeal, gleiches Gericht wie #2854 'Satay Seelachs' 450 g, günstiger)"),
            (2822, 2821, 'PrepMyMeal', "Duplikat (PrepMyMeal, gleiches Gericht wie #2821 'Hähnchen Bowl Thai (XL, 2 Portionen)' 1000 g, günstiger)"),
            (1534, 2861, 'PrepMyMeal', 'Duplikat (PrepMyMeal-Altzeile ohne Grammatur, aktuelle Zeile #2861)'),
            (1535, 2805, 'PrepMyMeal', 'Duplikat (PrepMyMeal-Altzeile ohne Grammatur, aktuelle Zeile #2805)'),
            (1536, 2863, 'PrepMyMeal', 'Duplikat (PrepMyMeal-Altzeile ohne Grammatur, aktuelle Zeile #2863)'),
            (1770, 1769, 'MPreis', 'Duplikat (MPreis, gleiches 800-g-Produkt wie #1769 Cevapcici)'),
        ):
            r, k = _rb.get(_d), _rb.get(_k)
            if r is None or k is None or r.get('store') != _st or k.get('store') != _st or r.get('dupOf') is not None:
                continue
            r['dupOf'] = _k; r['dupOfUid'] = k['uid']; r['rankable'] = False; r['pli'] = None; r['pliLight'] = None
            r['flags'] = (r.get('flags') or []) + [_why]
            changed_uids.add(r['uid'])
        _m, _b = _rb.get(1769), _rb.get(455)
        if _m is not None and _b is not None and _m.get('store') == 'MPreis' and _rb.get(1770, {}).get('dupOf') == 1769:
            _m['alsoAt'] = sorted(set((_m.get('alsoAt') or []) + ['Billa']))
            _rr = _m.get('rank_excluded_reason') or ''
            if 'gleiches Produkt in keiner Linzer Kette gefunden' in _rr:
                _m['rank_excluded_reason'] = _rr.replace('gleiches Produkt in keiner Linzer Kette gefunden',
                    'gleiches Produkt auch in Linz (Billa #455, Nährwerte vorhanden), dort als Fleischkomponente (zum Selbstbraten, kein Fertiggericht) nicht im Mahlzeiten-Ranking')
            changed_uids.add(_m['uid'])

    if changed_uids or removed_uids or files_changed or topcap_changed:
        # sensecheck 50 F2 bugs B/C: rebuild capped + uncapped lists with the real _collapse over ALL rows
        # (filtering the 30-entry uncapped list shrank topPLI to 20). Proven identical to 2484311 when nothing changed.
        def _cap_for(st):
            return cap_ship if st in ship_box_stores else cap_prov
        crow = [{**r, 'variantIds': list(r['variantIds'])} if 'variantIds' in r else dict(r) for r in rows]  # sensecheck 51: no shared variantIds mutation
        _base = lambda r: r.get('rankable') and not r.get('sold_out') and r.get('gang') != 'vorspeise'
        for key, flt, fn in (
            ('PLI', lambda r: _base(r) and r.get('pli') is not None, lambda r: r['pli']),
            ('Health', lambda r: _base(r) and r.get('score') is not None, lambda r: r['score']),
            ('PE', lambda r: _base(r) and r.get('ppe') and r.get('pstat') == 'live 2026' and r.get('pack') != 'Trocken/Instant', lambda r: r['ppe']),
            # sensecheck 52 P2: topLight rebuilt with the real _collapse too (refills to 30 when a light dish drops out)
            ('Light', lambda r: r.get('pliLight') is not None and not r.get('sold_out') and r.get('dupOf') is None and not r.get('linz_excluded') and not any('Duplikat' in f for f in (r.get('flags') or [])), lambda r: r['pliLight']),
        ):
            capped, _cnt, unc = _collapse([r for r in crow if flt(r)], fn, n=cap_n, cap=_cap_for)
            can['top' + key] = [r['id'] for r in capped]
            can['top' + key + 'Uncapped'] = [r['id'] for r in unc]
        # topLight: the SC15-SC48 light candidate set is not reconstructible from rows alone (SC-era overlays),
        # so keep the canonical order and only drop entries that are no longer eligible (sold out / hidden twin).
        _by = {r['id']: r for r in rows}
        _ok_l = lambda i: i in _by and _by[i].get('pliLight') is not None and not _by[i].get('sold_out') and _by[i].get('dupOf') is None
        for k in ('topLight', 'topLightUncapped'):
            if k in can:
                can[k] = [i for i in can[k] if _ok_l(i)]
        by_id = {r['id']: r for r in rows}
        can['uidTop'] = {
            k: [by_id[i]['uid'] for i in can.get(k, []) if i in by_id]
            for k in ('topPLI', 'topPLIUncapped', 'topHealth', 'topHealthUncapped', 'topPE', 'topPEUncapped', 'topLight', 'topLightUncapped')  # sensecheck 51: all 8 keys
            if k in can
        }
        can['dataVersion'] = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
    return can

out = _reconcile_sc48(out)

json.dump(out,open(os.environ.get('GOOD_CHOICE_OUT','/workspace/fertig-app/public/data.json'),'w'),ensure_ascii=False,separators=(',',':'))  # orch 1710: GOOD_CHOICE_OUT lets a worktree export without touching /workspace/fertig-app
print(len(R),len(sides),len(combos),len(veg),len(sal),len(sd))
for c in combos[:6]: print(R[c['main']]['name'],'|',sides[c['veg']]['name'] if False else [s['name'] for s in sides if s['id']==c['veg']],'|',[s['name'] for s in sides if s['id']==c['side']],c)
