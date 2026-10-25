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
_sc62_top_on = os.environ.get('SC62_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC62', '0') != '1'
_sc63_top_on = os.environ.get('SC63_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC63', '0') != '1'
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
    _raw_not_re = r'gegart|gebraten|gebacken|schlemmerfilet|bordelaise|backfisch|backteig|paniert|gegrillt|mariniert|sous|knusper|nugget|backhendl|cordon|fertig|gekocht|geräuchert|räucher|mit |sauce|soße|in |menü|curry|gulasch\b|suppe|topf|salat|knödel|reis|bowl|wrap|sandwich|pizza|burger|stäbchen|sticks|chili|bbq|grill|pulled|rahm|natur\*pur bio hendl mini|pasta|spaghetti|penne|tagliatelle|pappardelle|linguine|fusilli|rigatoni|makkaroni|nudel|gnocchi|tortell|ravioli' + (r'|lasagne|auflauf|gratin|tikka|mediterran' if _sc62_top_on else '')
    raw=re.search(r'faschiert|hackfleisch|\bhack\b|filet|brust|keule|unterkeul|oberkeul|flügel|wings|steak|schnitzel|leber|gulaschfleisch|geschnetzeltes|würfel|minute|ganzes|ganzer|hendl\b|hähnchen|kotelett|karree|schopf|bauch|lachs|forelle|garnelen|shrimps|kabeljau|seelachs|zander|saibling|thunfisch.*steak',t) and not re.search(_raw_not_re,t) and not r['pack'].startswith('Dose')
    if raw or ((r.get('kcal') or 0)>=300 and re.search(r'suppe|nudel|pulver|teigwar|einlage|abc|sternderl|gerstl|hörnchen|fadennudel|buchstaben|instant|terrine|cup|reis\b|couscous|bulgur|polenta|grieß',t) and (r.get('fat') or 0)<15) or re.search(r'barilla lasagne|collezione lasagne|recheis lasagne|lasagne hartweizen|glutenfreie lasagne|lasagneblätter|lasagne-?platten',t) or ('lasagne' in t and (r.get('kcal') or 0)>=300): stg='base'
    elif re.search(r'erdbeer|marillen|zwetschk|nougat|germknödel|topfenknödel|mehlspeis|kaiserschmarr|powidl|mohn|vanille|schoko',t): stg='base'
    elif r.get('dry') or re.search(r'sauce|soße|fix\b|fix |pesto|gewürz|würfel|pulver|bouillon|fond|dressing|mehl|paniermehl|brühe(?!.*einlage)',t) and not re.search(r'suppe|topf|\bin \w*(sauce|soße)|mit \w*(sauce|soße)|\bpizza\b|ristorante|intermezzo|tradizionale|ravioli|tortell|nudel|spaghetti|cannelloni|gnocchi|reis|fleisch|würstel|huhn|hendl|rind' + (r'|\b(in|mit)\s+[\wäöüß-]+\s+(sauce|soße)|hühner|garnelen|shrimps' if _sc63_top_on else ''),t): stg='base'
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
    elif stg in('veg','side','prot') and re.search(r'strudel|pinsa|pizza|brot\b|pastasalat|nudelsalat|eiersalat|bbq salat|wrap|burger|pasta fertig|fertiggericht|gebratene nudeln|magic asia|kasnudel|käsnudel|tomaten-mozzarella-nudeln|kürbis-nudeln|meeresküche|airfryer snack|goldschatz|cashew taschen|baguette|piccolini|big sensation|steinofen|ofenfrische|backfrische|flammkuchen|intermezzo' + (r'|bratnudeln|pop-up sushi|lachs picknick|kichererbsen-tahina-salat|smashed falafel' if _sc63_top_on else ''),t): stg='meal'  # T18: Dr. Oetker Intermezzo (TK Baguette-Snack, Thunfisch/Pesto variants) → meal; T16: TK snack pizzas/baguettes & Goldschatz fillets are meals; T17: Wagner Piccolinis/Big Sensation/Steinofen, Dr. Oetker Ofenfrische, Backfrische, Flammkuchen (pizza products without the word 'Pizza' in the name), not veg/prot
    elif re.search(r'(leber|wurst|grammel|selchfleisch|fleisch|speck|haschee|heurigen)knödel|currywurst|curry king|thunfisch',t) and not re.search(r'mit (sauerkraut|kraut|salat|gemüse|püree)|suppe|salat|pasta|nudel|sauce|menü|pizza|piccolini|big sensation|steinofen|ristorante|bistro|baguette|intermezzo|wrap' + (r'|fusilli|spaghetti|penne|tagliatelle|rigatoni|makkaroni' if _sc63_top_on else ''),t): stg='prot'  # sensecheck 6: Thunfisch-Wrap is a meal/snack, not a protein component
    elif re.search(r'knödel|kaspress',t) and not re.search(r'mit |suppe|menü|sauce',t): stg='side'
    # T20: Kärntner Kas-/Käsnudel(n) are a complete traditional dish (meal, like the rule above) — no longer demoted to 'side' when the name lacks 'Nudeln';
    #  raw-cut guard: 'gebacken' (pre-fried Putenschnitzel) and Schlemmerfilet/Bordelaise/Backfisch (oven-ready fish with topping/batter) are not raw ingredients → prot instead of base
    elif re.search(r'ravioli|tortell|fagottini|girasoli|cappellet|gnocchi',t) and not (r['pack'].startswith('Dose') if _sc63_top_on else False) and not re.search(r'pfanne|sauce|soße|carbonara|bolognese|gratin|al forno|menü|mit .*(sauce|soße)|teller|bowl' + (r'|veggie love meals|every foods|garden gnocchi|gnocchi mit (blattspinat|lachs|spargel)' if _sc63_top_on else ''),t): stg='side'
    # sensecheck 8: pure finished-meal providers (no components) — 450 g 'Spätzle Goulash'/'Garden Gnocchi'/'Peanut Noodles' are meals, not Beilage/Zutat.
    #  bofrost excluded on purpose: it also sells components (Knödel, Cevapcici, Schnitzel).
    if (r.get('src') in ('online_mealprep.json', 'linz_providers_src.json') if _sc62_top_on else r.get('src')=='online_mealprep.json') and (r.get('store') in MEALPREP_ONLY or (_sc63_top_on and (r.get('brand') or '').lower() == 'every foods')) and stg in('side','base','veg','prot') and not r.get('dry') and not r.get('nonfood'): stg='meal'
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
_XL=re.compile(r'\(\s*xl[^)]*\)|\bxl\b|\(\s*\d+[.,]?\d*\s*(g|kg)\s*\)|\(?\s*\b\d+\s*portion(en)?\b\s*\)?|\b\d+\s*(stück|stk)\b|\b\d+er[- ]?(packung|pack)\b',re.I)  # sensecheck 52 P2 / SC63 P2c: '2 Portionen' and '2 Stück' (#2670/#2416)
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
            if os.environ.get('SC64_FIXES', '1') == '0' or os.environ.get('GOOD_CHOICE_DISABLE_SC64', '0') == '1' or r['id'] not in kv.setdefault('variantIds', []):
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

    # sensecheck 54 P1.2/P1.3: PrepMyMeal URL, size & price reconciliation (live-verified 2026-10-24)
    _sc54_pmm_on = (
        os.environ.get('SC54_PREPMYMEAL', '1') != '0'
        and os.environ.get('GOOD_CHOICE_DISABLE_SC54_PREPMYMEAL', '0') != '1'
        and os.environ.get('SC52_DUPOF', '1') != '0'
        and os.environ.get('SC53_SOLDOUT', '1') != '0'
        and os.environ.get('SC54_BACKINSTOCK', '1') != '0'
    )
    if _sc54_pmm_on:
        _pmm_by_id = {r['id']: r for r in rows}
        # Item 1: #2785 Butter Chicken (XL, 2 Portionen) & #2788 Käsespätzle mit Hähnchen (XL, 2 Portionen)
        for _id, _url in (
            (2785, 'https://prepmymeal.at/products/butter-chicken-xl-2-portionen'),
            (2788, 'https://prepmymeal.at/products/kasespatzle-mit-hahnchen'),
        ):
            _r = _pmm_by_id.get(_id)
            if _r is not None and _r.get('store') == 'PrepMyMeal':
                _r['url'] = _url
                _r['nutrition_source'] = _url
                _r['size'] = 1000.0
                _r['price'] = 12.48
                _r['ppk'] = 12.48
                _r['p100g'] = 1.25
                _r['pPor'] = 6.24
                _r['pPorEff'] = round(6.24 + (_r.get('shipPor') or 1.0), 2)
                if _r.get('protPor'):
                    _r['ppe'] = round(_r['protPor'] / _r['pPor'], 1)
                if _r.get('protpack'):
                    _r['eur10p'] = round(12.48 / (_r['protpack'] / 10.0), 2)
                if _r.get('kcalpack'):
                    _r['eur100k'] = round(12.48 / (_r['kcalpack'] / 100.0), 2)
                changed_uids.add(_r['uid'])
        # Item 2a: #1533 Hähnchen im Kokosmantel -> live handle, 500 g, €10.49, rankable meal
        _r1533 = _pmm_by_id.get(1533)
        if _r1533 is not None and _r1533.get('store') == 'PrepMyMeal':
            _r1533['url'] = 'https://prepmymeal.at/products/hahnchen-im-kokosmantel-1'
            _r1533['size'] = 500.0
            _r1533['price'] = 10.49
            _r1533['ppk'] = 20.98
            _r1533['p100g'] = 2.1
            _r1533['portion'] = 500
            _r1533['portion_g'] = 500
            _r1533['portion_source'] = 'pack_single'
            _r1533['stage'] = 'meal'
            _r1533['gang'] = 'haupt'
            _r1533['pack'] = 'Tiefkühl (TK)'
            _r1533['shipPor'] = 1.0
            _r1533['pPor'] = 10.49
            _r1533['pPorEff'] = 11.49
            _x1533 = {
                'name': _r1533.get('name'), 'size_g': 500.0, 'packaging': 'Tiefkühl (TK)',
                'kcal_100': _r1533.get('kcal'), 'protein_100': _r1533.get('p100'), 'fat_100': _r1533.get('fat'),
                'satfat_100': _r1533.get('sat'), 'carbs_100': _r1533.get('carbs'), 'sugar_100': _r1533.get('sugar'),
                'fiber_100': _r1533.get('fib'), 'salt_100': _r1533.get('salt'), 'ingredients': _r1533.get('ing'),
                'store': _r1533.get('store'),
            }
            _v1533 = V2.score_v2(_x1533)
            _mc1533 = V2.meal_check(_x1533, _v1533)
            _r1533['score'] = _v1533.get('health_score')
            _r1533['score_parts'] = _v1533.get('score_parts')
            _r1533['day_pct'] = _v1533.get('day_pct')
            _r1533['meal_class'] = _mc1533.get('cls')
            _r1533['meal_check'] = _mc1533
            _r1533['kcal_meal'] = _v1533.get('kcal_meal')
            _r1533['kcalPor'] = 480.0
            _r1533['kcalpack'] = 480.0
            _r1533['protPor'] = 44.5
            _r1533['protpack'] = 44.5
            _r1533['saltPor'] = 3.45
            _r1533['saltPct'] = 58
            _r1533['ppe'] = round(44.5 / 10.49, 1)
            _r1533['eur10p'] = round(10.49 / 4.45, 2)
            _r1533['eur100k'] = round(10.49 / 4.8, 2)
            _r1533['flags'] = [f for f in (_r1533.get('flags') or []) if 'Portion unbekannt' not in f]
            _r1533['rankable'] = bool(_mc1533.get('ok')) and _sc50_rank_guard(_r1533)
            if _r1533['rankable'] and _r1533.get('score') is not None:
                _pe1533 = min(100.0, (_r1533['protPor'] / _r1533['pPorEff']) * 5.0)
                _r1533['pli'] = round(0.5 * _r1533['score'] + 0.5 * _pe1533, 1)
            changed_uids.add(_r1533['uid'])
        # Item 2c: #1534, #1535, #1536 backfill size while keeping dupOf (2861, 2805, 2863) intact
        for _id, _sz, _ppk, _p100g in (
            (1534, 450.0, 23.31, 2.33),
            (1535, 400.0, 26.23, 2.62),
            (1536, 460.0, 22.8, 2.28),
        ):
            _r = _pmm_by_id.get(_id)
            if _r is not None and _r.get('store') == 'PrepMyMeal':
                _r['size'] = _sz
                _r['ppk'] = _ppk
                _r['p100g'] = _p100g
                changed_uids.add(_r['uid'])
        # Item 2d: #2847 Lachs, Reis, grüne Bohnen -> live handle -1, 490 g, €12.49, ppk 25.49
        _r2847 = _pmm_by_id.get(2847)
        if _r2847 is not None and _r2847.get('store') == 'PrepMyMeal':
            _r2847['url'] = 'https://prepmymeal.at/products/lachs-reis-grune-bohnen-1'
            _r2847['nutrition_source'] = 'https://prepmymeal.at/products/lachs-reis-grune-bohnen-1'
            _r2847['size'] = 490.0
            _r2847['price'] = 12.49
            _r2847['ppk'] = 25.49
            _r2847['p100g'] = 2.55
            _r2847['portion'] = 490
            _r2847['portion_g'] = 490
            _r2847['pPor'] = 12.49
            _r2847['pPorEff'] = round(12.49 + (_r2847.get('shipPor') or 1.0), 2)
            _r2847['kcalPor'] = 681.0
            _r2847['kcal_meal'] = 681
            _r2847['kcalpack'] = 681.0
            _r2847['protPor'] = 34.3
            _r2847['protpack'] = 34.3
            _r2847['saltPor'] = 1.37
            _r2847['saltPct'] = 23
            _r2847['day_pct'] = {'kcal': 34, 'protein': 69, 'salt': 23, 'satfat': 39, 'sugar': 2, 'fiber': None}
            _r2847['meal_check'] = {'portion': 490, 'kcal': 681, 'protein': 34.3, 'ok': True, 'cls': 'meal', 'reason': None}
            _r2847['ppe'] = round(34.3 / 12.49, 1)
            _r2847['eur10p'] = round(12.49 / 3.43, 2)
            _r2847['eur100k'] = round(12.49 / 6.81, 2)
            _r2847['rankable'] = _sc50_rank_guard(_r2847)
            if _r2847['rankable'] and _r2847.get('score') is not None:
                _pe2847 = min(100.0, (_r2847['protPor'] / _r2847['pPorEff']) * 5.0)
                _r2847['pli'] = round(0.5 * _r2847['score'] + 0.5 * _pe2847, 1)
            changed_uids.add(_r2847['uid'])
        # Item 2b / SC55 P2.2: #1532 Kichererbsen mit Harissa -> delisted 12er-box orphan without weight
        _r1532 = _pmm_by_id.get(1532)
        if _r1532 is not None and _r1532.get('store') == 'PrepMyMeal':
            _r1532['variant_note'] = 'ausgelistet'
            _r1532['rank_excluded_reason'] = 'nicht mehr im PrepMyMeal-Sortiment (ausgelistet); Gewicht nicht angegeben'
            _r1532['rankable'] = False
            _r1532['rankableLight'] = False
            _r1532['pli'] = None
            _r1532['pliLight'] = None
            changed_uids.add(_r1532['uid'])
        # SC55 P1.2: #2857 Chili con Carne Blumenkohlreis (Copy) -> dupOf #2845 Chili con Carne (500 g)
        if os.environ.get('SC55_PREPMYMEAL', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC55_PREPMYMEAL', '0') != '1':
            _r2857, _r2845 = _pmm_by_id.get(2857), _pmm_by_id.get(2845)
            if _r2857 is not None and _r2845 is not None and _r2857.get('store') == 'PrepMyMeal':
                _r2857['dupOf'] = 2845
                _r2857['dupOfUid'] = _r2845.get('uid')
                _r2857['rankable'] = False
                _r2857['rankableLight'] = False
                _r2857['pli'] = None
                _r2857['pliLight'] = None
                _fl2857 = list(_r2857.get('flags') or [])
                _dup_reason_2857 = "Duplikat (PrepMyMeal, Copy-Dublette von #2845 'Chili con Carne' 500 g)"
                if not any(isinstance(x, str) and x.startswith('Duplikat') for x in _fl2857):
                    _fl2857.append(_dup_reason_2857)
                _r2857['flags'] = _fl2857
                changed_uids.add(_r2857['uid'])
            # SC55 Versand-/Kochbox audit (2026-10-24): Bofrost #2951 (01283) & #3068 (20550) moved from /shop/neuheiten_48008/ to canonical /shop/<slug>.html
            if os.environ.get('SC55_VERSANDBOX', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC55_VERSANDBOX', '0') != '1':
                for _bf_id, _bf_old, _bf_new in (
                    (2951, 'https://www.bofrost.at/shop/neuheiten_48008/thai-curry_01283.html', 'https://www.bofrost.at/shop/thai-curry_01283.html'),
                    (3068, 'https://www.bofrost.at/shop/neuheiten_48008/bauerntopf_20550.html', 'https://www.bofrost.at/shop/bauerntopf_20550.html'),
                ):
                    _rbf = _pmm_by_id.get(_bf_id)
                    if _rbf is not None and _rbf.get('store') == 'bofrost':
                        _rbf['url'] = _bf_new
                        if isinstance(_rbf.get('nutrition_source'), str) and _bf_old in _rbf['nutrition_source']:
                            _rbf['nutrition_source'] = _rbf['nutrition_source'].replace(_bf_old, _bf_new)
                        changed_uids.add(_rbf['uid'])
            # SC58 (from Sensecheck 57 P1.2 + P3):
            # 1) Ungate 6 live available PrepMyMeal full meals (#2828, #2852, #2793, #2849, #2867, #2801) blocked by legacy V1 heuristics
            # 2) Billa Clever dry soups #534-#539: meal_class='dry', rank_excluded_reason='Trockensuppe (kein Fertiggericht)', remove 1g placeholder
            if os.environ.get('SC58_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC58', '0') != '1':
                for _pmm_id in (2828, 2852, 2793, 2849, 2867, 2801):
                    _rpm = _pmm_by_id.get(_pmm_id)
                    if _rpm is None or _rpm.get('store') != 'PrepMyMeal':
                        continue
                    if _pmm_id == 2793:
                        _rpm.pop('kiloErr', None)
                        _rpm['flags'] = [f for f in (_rpm.get('flags') or []) if 'Preis ist vermutlich €/kg' not in f]
                    if _pmm_id == 2801:
                        _rpm['meal_class'] = 'meal'
                        _rpm['meal_check'] = {
                            'portion': _rpm.get('portion') or 470,
                            'kcal': int(_rpm.get('kcalPor') or 555),
                            'protein': _rpm.get('protPor') or 38.5,
                            'ok': True,
                            'cls': 'meal',
                            'reason': None,
                        }
                        _rpm['flags'] = [f for f in (_rpm.get('flags') or []) if 'Brot/Snack/Instant' not in f]
                    if not _rpm.get('sold_out') and _rpm.get('meal_class') == 'meal' and not _rpm.get('linz_excluded') and _sc50_rank_guard(_rpm):
                        _rpm['rankable'] = True
                        if _rpm.get('score') is not None and _rpm.get('protPor') and _rpm.get('pPorEff'):
                            _pe58 = min(100.0, (_rpm['protPor'] / _rpm['pPorEff']) * 5.0)
                            _rpm['pli'] = round(0.5 * _rpm['score'] + 0.5 * _pe58, 1)
                    changed_uids.add(_rpm['uid'])
                for _ds_id in (534, 535, 536, 537, 538, 539):
                    _rds = _pmm_by_id.get(_ds_id)
                    if _rds is not None and _rds.get('store') == 'Billa' and _rds.get('dry'):
                        _rds['meal_class'] = 'dry'
                        _rds['meal_check'] = {'ok': False, 'cls': 'dry', 'reason': 'Trockenprodukt'}
                        _rds['rank_excluded_reason'] = 'Trockensuppe (kein Fertiggericht)'
                        for _k_clr in ('size', 'portion', 'portion_g', 'pPor', 'p100g', 'ppk', 'protpack', 'kcalpack', 'protPor', 'kcalPor', 'kcal_meal', 'saltPor', 'saltPct', 'eur10p', 'eur100k', 'ppe'):
                            _rds[_k_clr] = None
                        changed_uids.add(_rds['uid'])
                for _dup_ds_id in (994, 995, 996, 997, 998, 999):
                    _rdup = _pmm_by_id.get(_dup_ds_id)
                    if _rdup is not None and _rdup.get('store') == 'Billa' and _rdup.get('dry'):
                        _rdup['meal_class'] = 'dry'
                        _rdup['meal_check'] = {'ok': False, 'cls': 'dry', 'reason': 'Trockenprodukt'}
                        _rdup['rank_excluded_reason'] = 'Trockensuppe (kein Fertiggericht)'
                        changed_uids.add(_rdup['uid'])

                # sensecheck 59 (SC57 P2 Linzer Lokal-Hebel):
                # 1. Fit to Go (#1435-#1464, #2749): fix 5 misclassified full meals (#1436, #1437, #1441, #1443, #1455)
                #    so all 25 verified full meals pass isFullMeal / passesLightScore (fittogo.at publishes only
                #    KCAL/PROTEIN/CARBS/FETT in meal_nutrients; sat & salt remain None without estimation).
                # 2. 9 Billa & 17 Hofer fresh-2026 priceOnly rows: backfill verified nutrition & EANs for 7 products
                #    (#876 Aumaerk Beef Loyal Sous Vide from Billa label photo; #860/#861/#862 Asia Green Garden Udon bowls
                #    and #1228/#1229/#1235 Hofer chilled items from verified OpenFoodFacts label entries), link #3487 EAN,
                #    and reclassify non-ready-meal items (#0, #1, #6 raw butcher meat; #3536 dry spice; #3579-#3581/#3583
                #    cut fruit cups; #859 canned pickled mushrooms) with explicit rank_excluded_reason.
                if os.environ.get('SC59_LINZ_LOKAL', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC59', '0') != '1':
                    # Part 1: Fit to Go full-meal classification fixes
                    for _ftg_id, _ftg_port, _ftg_kcal, _ftg_prot in (
                        (1436, 400, 488, 46.0),
                        (1437, 360, 537, 38.9),
                        (1441, 450, 552, 30.1),
                        (1443, 400, 456, 36.0),
                        (1455, 420, 483, 29.0),
                    ):
                        _rftg = _pmm_by_id.get(_ftg_id)
                        if _rftg is not None and _rftg.get('store') == 'Fit to Go':
                            _rftg['stage'] = 'meal'
                            _rftg['gang'] = 'haupt'
                            _rftg['meal_class'] = 'meal'
                            _rftg['component'] = False
                            _rftg['meal_check'] = {
                                'portion': _ftg_port,
                                'kcal': _ftg_kcal,
                                'protein': _ftg_prot,
                                'ok': True,
                                'cls': 'meal',
                                'reason': None,
                            }
                            _rftg['flags'] = [
                                f for f in (_rftg.get('flags') or [])
                                if 'Proteinkomponente' not in f and 'Brot/Snack/Instant' not in f
                            ]
                            changed_uids.add(_rftg['uid'])

                    # Part 2A: Billa #876 Aumaerk Beef Loyal Sous Vide (350 g, €13.99, verified back-of-pack label)
                    _r876 = _pmm_by_id.get(876)
                    if _r876 is not None and _r876.get('store') == 'Billa':
                        _r876['ean'] = '9120077263045'
                        _r876['kcal'] = 154.0
                        _r876['p100'] = 26.6
                        _r876['fat'] = 5.1
                        _r876['sat'] = 2.2
                        _r876['carbs'] = 0.3
                        _r876['sugar'] = 0.3
                        _r876['salt'] = 1.53
                        _r876['kcalPor'] = 539.0
                        _r876['kcal_meal'] = 539
                        _r876['kcalpack'] = 539.0
                        _r876['protPor'] = 93.1
                        _r876['protpack'] = 93.1
                        _r876['saltPor'] = 5.36
                        _r876['saltPct'] = 89
                        _r876['ppe'] = 6.7
                        _r876['eur10p'] = 1.5
                        _r876['eur100k'] = 2.6
                        _r876['priceOnly'] = False
                        _r876['incomplete'] = False
                        _r876['nutrition_source'] = 'https://shop.billa.at/produkte/aumaerk-beef-loyal-sous-vide-00763187'
                        _x876 = {
                            'name': _r876.get('name'), 'size_g': 350.0, 'packaging': _r876.get('pack'),
                            'kcal_100': 154.0, 'protein_100': 26.6, 'fat_100': 5.1,
                            'satfat_100': 2.2, 'carbs_100': 0.3, 'sugar_100': 0.3,
                            'fiber_100': None, 'salt_100': 1.53,
                            'ingredients': 'Rindfleisch 97%, Speisesalz, Gewürze, Zwiebel, Karotte, Pastinake, Karamell, Maltodextrin, Sonnenblumenöl',
                            'store': 'Billa',
                        }
                        _v876 = V2.score_v2(_x876)
                        _r876['score'] = _v876.get('health_score')
                        _r876['score_parts'] = _v876.get('score_parts')
                        _r876['day_pct'] = _v876.get('day_pct')
                        _r876['nova'] = _v876.get('nova')
                        _r876['nova_source'] = _v876.get('nova_source')
                        _r876['veg_pct'] = _v876.get('veg_pct')
                        _r876['veg_source'] = _v876.get('veg_source')
                        _r876['stage'] = 'prot'
                        _r876['gang'] = 'zutat'
                        _r876['meal_class'] = 'protein_component'
                        _r876['component'] = True
                        _r876['meal_check'] = {
                            'portion': 350, 'kcal': 539, 'protein': 93.1,
                            'ok': False, 'cls': 'protein_component',
                            'reason': 'Proteinkomponente ohne Sättigungsbeilage (kein vollständiges Fertiggericht)',
                        }
                        _r876['rank_excluded_reason'] = 'Proteinkomponente ohne Sättigungsbeilage (kein vollständiges Fertiggericht)'
                        _r876['rankable'] = False
                        _r876['flags'] = [f for f in (_r876.get('flags') or []) if 'Nährwerte fehlen' not in f]
                        changed_uids.add(_r876['uid'])

                    # Other 8 Billa non-ready-meal rows
                    for _raw_id in (0, 1, 6):
                        _rraw = _pmm_by_id.get(_raw_id)
                        if _rraw is not None and _rraw.get('store') == 'Billa':
                            _rraw['stage'] = 'prot'
                            _rraw['gang'] = 'zutat'
                            _rraw['meal_class'] = 'raw_ingredient'
                            _rraw['component'] = True
                            _rraw['meal_check'] = {'ok': False, 'cls': 'raw_ingredient', 'reason': 'Rohes Gulasch-/Ragoutfleisch (kein Fertiggericht)'}
                            _rraw['rank_excluded_reason'] = 'Rohes Gulasch-/Ragoutfleisch (kein Fertiggericht)'
                            changed_uids.add(_rraw['uid'])

                    _r3536 = _pmm_by_id.get(3536)
                    if _r3536 is not None and _r3536.get('store') == 'Billa':
                        _r3536['stage'] = 'sauce'
                        _r3536['gang'] = 'zutat'
                        _r3536['meal_class'] = 'condiment_or_base'
                        _r3536['dry'] = True
                        _r3536['ppk'] = 69.53
                        _r3536['p100g'] = 6.95
                        _r3536.pop('kiloErr', None)
                        _r3536['meal_check'] = {'ok': False, 'cls': 'condiment_or_base', 'reason': 'Gewürzmischung (kein Fertiggericht)'}
                        _r3536['rank_excluded_reason'] = 'Gewürzmischung (kein Fertiggericht)'
                        _r3536['flags'] = [f for f in (_r3536.get('flags') or []) if '€/kg' not in f]
                        changed_uids.add(_r3536['uid'])

                    for _fr_id in (3579, 3580, 3581, 3583):
                        _rfr = _pmm_by_id.get(_fr_id)
                        if _rfr is not None and _rfr.get('store') == 'Billa':
                            _rfr['stage'] = 'sweet'
                            _rfr['gang'] = 'dessert'
                            _rfr['meal_class'] = 'dessert'
                            _rfr['meal_check'] = {'ok': False, 'cls': 'dessert', 'reason': 'Frischer Obstbecher (kein Hauptgericht)'}
                            _rfr['rank_excluded_reason'] = 'Frischer Obstbecher (kein Hauptgericht)'
                            changed_uids.add(_rfr['uid'])

                    # Part 2B: Hofer verified OpenFoodFacts backfills (#860, #861, #862, #1228, #1229, #1235) + #859 & #3487
                    for _hid, _ean, _sz, _kcal, _p100, _fat, _sat, _carbs, _sugar, _fib, _salt, _ing_override, _mc_override in (
                        (860, '4061461867645', 249.0, 141.0, 3.4, 1.2, 0.2, 28.0, 6.3, None, 0.8, None, None),
                        (861, '4061461867669', 252.0, 171.0, 4.8, 4.7, 0.9, 26.0, 4.5, None, 0.76, None, None),
                        (862, '4061461867683', 249.0, 145.0, 3.2, 1.3, 0.2, 29.0, 0.5, None, 1.0, None, None),
                        (1228, '4061458049443', 430.0, 215.0, 9.6, 7.8, 3.3, 25.5, 3.7, 2.1, 1.33,
                         'Weizenmehl, passierte Tomaten, Edamer, Calabrese-Salami, Peperoni, Rapsöl, Hefe, Speisesalz', None),
                        (1229, '4061458049436', 430.0, 223.0, 11.0, 8.3, 2.8, 25.0, 3.6, None, 1.4,
                         'Weizenmehl, passierte Tomaten, Edamer, Kochschinken, Speisesalz, Hefe, Rapsöl', None),
                        (1235, '4061458041997', 250.0, 252.0, 5.7, 12.0, 5.9, 30.0, 13.0, None, 1.2, None, 'snack_side'),
                    ):
                        _rh = _pmm_by_id.get(_hid)
                        if _rh is not None and _rh.get('store') == 'Hofer':
                            _rh['ean'] = _ean
                            _rh['size'] = _sz
                            _rh['portion'] = int(_sz)
                            _rh['portion_g'] = int(_sz)
                            _rh['portion_source'] = 'pack_single'
                            _rh['kcal'] = _kcal
                            _rh['p100'] = _p100
                            _rh['fat'] = _fat
                            _rh['sat'] = _sat
                            _rh['carbs'] = _carbs
                            _rh['sugar'] = _sugar
                            if _fib is not None:
                                _rh['fib'] = _fib
                            _rh['salt'] = _salt
                            if _ing_override is not None and not _rh.get('ing'):
                                _rh['ing'] = _ing_override
                            _rh['priceOnly'] = False
                            _rh['incomplete'] = False
                            _rh['nutrition_source'] = f'https://world.openfoodfacts.org/product/{_ean}'
                            _pr_h = _rh.get('price')
                            if _pr_h:
                                _rh['ppk'] = round(_pr_h / (_sz / 1000.0), 2)
                                _rh['p100g'] = round(_pr_h / (_sz / 100.0), 2)
                                _rh['pPor'] = _pr_h
                                _rh['pPorEff'] = _pr_h
                            _xh = {
                                'name': _rh.get('name'), 'size_g': _sz, 'packaging': _rh.get('pack'),
                                'kcal_100': _kcal, 'protein_100': _p100, 'fat_100': _fat,
                                'satfat_100': _sat, 'carbs_100': _carbs, 'sugar_100': _sugar,
                                'fiber_100': _rh.get('fib'), 'salt_100': _salt,
                                'ingredients': _rh.get('ing'), 'store': 'Hofer',
                            }
                            _vh = V2.score_v2(_xh)
                            _mch = V2.meal_check(_xh, _vh)
                            _rh['score'] = _vh.get('health_score')
                            _rh['score_parts'] = _vh.get('score_parts')
                            _rh['day_pct'] = _vh.get('day_pct')
                            _rh['nova'] = _vh.get('nova')
                            _rh['nova_source'] = _vh.get('nova_source')
                            _rh['veg_pct'] = _vh.get('veg_pct')
                            _rh['veg_source'] = _vh.get('veg_source')
                            _rh['kcal_meal'] = _vh.get('kcal_meal')
                            _rh['kcalPor'] = round(_kcal * _sz / 100.0, 1)
                            _rh['kcalpack'] = round(_kcal * _sz / 100.0, 1)
                            _rh['protPor'] = round(_p100 * _sz / 100.0, 1)
                            _rh['protpack'] = round(_p100 * _sz / 100.0, 1)
                            _rh['saltPor'] = round(_salt * _sz / 100.0, 2)
                            _rh['saltPct'] = int(round((_rh['saltPor'] / 6.0) * 100.0))
                            if _pr_h and _rh['protPor'] > 0:
                                _rh['ppe'] = round(_rh['protPor'] / _pr_h, 1)
                                _rh['eur10p'] = round(_pr_h / (_rh['protpack'] / 10.0), 2)
                            if _pr_h and _rh['kcalpack'] > 0:
                                _rh['eur100k'] = round(_pr_h / (_rh['kcalpack'] / 100.0), 2)
                            if _mc_override == 'snack_side':
                                _rh['meal_class'] = 'snack_side'
                                _rh['meal_check'] = {
                                    'portion': int(_sz), 'kcal': _vh.get('kcal_meal'), 'protein': _rh['protPor'],
                                    'ok': False, 'cls': 'snack_side', 'reason': 'Brot/Snack/Instant – keine Mahlzeit',
                                }
                            else:
                                _rh['meal_class'] = _mch.get('cls')
                                _rh['meal_check'] = _mch
                            _rh['flags'] = [f for f in (_rh.get('flags') or []) if 'Nährwerte fehlen' not in f]
                            if not _mch.get('ok') and _mch.get('reason'):
                                _mflag = f"Mahlzeit-Check: {_mch['reason']}"
                                if _mflag not in _rh['flags']:
                                    _rh['flags'].append(_mflag)
                            if (
                                _rh.get('meal_class') == 'light_meal'
                                and 300 <= (_rh.get('kcal_meal') or 0) < 400
                                and (_rh.get('score') or 0) >= 30
                                and _rh.get('pstat') == 'live 2026'
                                and _pr_h
                            ):
                                _rh['pliLight'] = round(0.5 * _rh['score'] + 0.5 * min((_rh['protPor'] / _pr_h) / 20.0, 1.0) * 100.0, 1)
                                _rh['rankableLight'] = True
                            changed_uids.add(_rh['uid'])

                    _r859 = _pmm_by_id.get(859)
                    if _r859 is not None and _r859.get('store') == 'Hofer':
                        _r859['stage'] = 'veg'
                        _r859['gang'] = 'zutat'
                        _r859['meal_class'] = 'component'
                        _r859['component'] = True
                        _r859['meal_check'] = {'ok': False, 'cls': 'component', 'reason': 'Pilzkonserve (kein Fertiggericht)'}
                        _r859['rank_excluded_reason'] = 'Pilzkonserve (kein Fertiggericht)'
                        changed_uids.add(_r859['uid'])

                    _r3487 = _pmm_by_id.get(3487)
                    if _r3487 is not None and _r3487.get('store') == 'Hofer':
                        _r3487['ean'] = '4069365963722'
                        changed_uids.add(_r3487['uid'])

                    # sensecheck 60 (SC60):
                    # 1. Spar #176 (S-BUDGET Rindsgulasch 400 G, p/7442025): backfill verified satfat_100=1.6 & fiber_100=0.9
                    #    from official SPAR Produktwelt / INTERSPAR (plus image from duplicate #1116) -> score 48.8, pli 55.8, rankable.
                    # 2. Spar #1162 (Inzersdorfer Rindsgulasch 800 G, p/145930): backfill verified satfat_100=1.6, EAN 9017100001050,
                    #    manufacturer metadata & 2-portion (400 g) split from INTERSPAR twin #97 ('2 Portionen') & MPreis twin #2445
                    #    -> score 45.7, pli 41.3, rankable; update MPreis #2445 rank_excluded_reason accordingly.
                    # 3. Spar #95 (Inzersdorfer Riesenbohnengulasch 400 G, p/412568): backfill verified satfat_100=2.1 from official
                    #    SPAR Produktwelt / INTERSPAR -> score 25.4 (< 30, remains non-rankable with explicit score reason).
                    # 4. OFF #1382 (Suppe Thai Chili, EAN 4049162022976): clear implausible 2.0 g pack size artefact and mark as dry soup.
                    if os.environ.get('SC60_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC60', '0') != '1':
                        _r176 = _pmm_by_id.get(176)
                        if _r176 is not None and _r176.get('store') == 'Spar':
                            _r176['sat'] = 1.6
                            _r176['fib'] = 0.9
                            _r176['img'] = _r176.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/7442025/dt_main.jpg'
                            _r176['incomplete'] = False
                            _r176['nutrition_source'] = 'SPAR Produktwelt / INTERSPAR Webshop (p/7442025, je 100 g unzubereitet) 2026-10-24'
                            _r176['score'] = 48.8
                            _r176['scoreV1'] = 49.9
                            _r176['score_parts'] = {'base': 30.0, 'protein': 30.7, 'salt': -7.1, 'satfat': -0.3, 'sugar': 0.0, 'fiber': 1.5, 'veg': 0, 'nova': -3, 'portion_salt': -8, 'portion_protein': 5}
                            _r176['day_pct'] = {'kcal': 21, 'protein': 75, 'salt': 73, 'satfat': 32, 'sugar': 2, 'fiber': 12}
                            _r176['meal_class'] = 'meal'
                            _r176['meal_check'] = {'portion': 400, 'kcal': 428, 'protein': 37.6, 'ok': True, 'cls': 'meal', 'reason': None}
                            _r176['flags'] = [f for f in (_r176.get('flags') or []) if 'Score unvollständig' not in f]
                            _r176['rankable'] = True
                            _r176['pli'] = 55.8
                            changed_uids.add(_r176['uid'])

                        _r1162 = _pmm_by_id.get(1162)
                        if _r1162 is not None and _r1162.get('store') == 'Spar':
                            _r1162['sat'] = 1.6
                            _r1162['ean'] = '9017100001050'
                            _r1162['img'] = _r1162.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/145930/dt_main.jpg'
                            _r1162['pid'] = 'AT 62028 EG'
                            _r1162['herst'] = 'Landgenossenschaft Ennstal LANDENA KG'
                            _r1162['ort'] = 'Erzherzog-Johann-Straße 303, 8950 Stainach-Pürgg'
                            _r1162['state'] = 'Steiermark'
                            _r1162['prodSlug'] = 'landena'
                            _r1162['incomplete'] = False
                            _r1162['nutrition_source'] = 'INTERSPAR Webshop (p/145930, Zwilling #97, 2 Portionen à 400 g)'
                            _r1162['portion'] = 400
                            _r1162['portion_g'] = 400
                            _r1162['portion_source'] = 'name_portions'
                            _r1162['pPor'] = 5.25
                            _r1162['protPor'] = 38.8
                            _r1162['kcalPor'] = 444.0
                            _r1162['kcal_meal'] = 444
                            _r1162['saltPor'] = 4.8
                            _r1162['saltPct'] = 80
                            _r1162['score'] = 45.7
                            _r1162['scoreV1'] = 46.1
                            _r1162['score_parts'] = {'base': 30.0, 'protein': 30.6, 'salt': -8.6, 'satfat': -0.3, 'sugar': 0.0, 'fiber': 0, 'veg': 0, 'nova': -3, 'portion_salt': -8, 'portion_protein': 5}
                            _r1162['day_pct'] = {'kcal': 22, 'protein': 78, 'salt': 80, 'satfat': 32, 'sugar': 3, 'fiber': None}
                            _r1162['meal_class'] = 'meal'
                            _r1162['meal_check'] = {'portion': 400, 'kcal': 444, 'protein': 38.8, 'ok': True, 'cls': 'meal', 'reason': None}
                            _r1162['flags'] = [f for f in (_r1162.get('flags') or []) if 'Score unvollständig' not in f and 'Mehrportionen-Packung' not in f]
                            _r1162['rankable'] = True
                            _r1162['pli'] = 41.3
                            changed_uids.add(_r1162['uid'])

                        _r2445 = _pmm_by_id.get(2445)
                        if _r2445 is not None and _r2445.get('store') == 'MPreis':
                            _r2445['rank_excluded_reason'] = 'MPreis hat keine Filiale in 4020 Linz und liefert nicht (keine MPREIS-Filiale in Linz (Oberösterreich nur Lenzing und Steyr), kein Lieferservice für Privatkunden); gleiches Produkt in Linz bei Spar – dort gerankt'
                            changed_uids.add(_r2445['uid'])

                        _r95 = _pmm_by_id.get(95)
                        if _r95 is not None and _r95.get('store') == 'Spar':
                            _r95['sat'] = 2.1
                            _r95['incomplete'] = False
                            _r95['nutrition_source'] = 'SPAR Produktwelt / INTERSPAR Webshop (p/412568, je 100 g unzubereitet) 2026-10-24'
                            _r95['score'] = 25.4
                            _r95['scoreV1'] = 28.9
                            _r95['score_parts'] = {'base': 30.0, 'protein': 15.1, 'salt': -11.4, 'satfat': -2.0, 'sugar': 0.0, 'fiber': 0, 'veg': 0, 'nova': -3, 'portion_salt': -8, 'portion_satfat': -0.3, 'portion_protein': 5}
                            _r95['day_pct'] = {'kcal': 31, 'protein': 54, 'salt': 93, 'satfat': 42, 'sugar': 4, 'fiber': None}
                            _r95['cprot'] = ['Schwein', 'Rind', 'Hülsenfrüchte']
                            _r95['dishKey'] = 'gulasch'
                            _r95['dish'] = 'Gulasch & Ragout'
                            _r95['flags'] = [f for f in (_r95.get('flags') or []) if 'Score unvollständig' not in f]
                            _r95['rankable'] = False
                            _r95['pli'] = None
                            _r95['rank_excluded_reason'] = 'Gesundheits-Score unter 30 (25.4)'
                            changed_uids.add(_r95['uid'])

                        _r1382 = _pmm_by_id.get(1382)
                        if _r1382 is not None and _r1382.get('store') == 'unbekannt (OFF)' and _r1382.get('size') is not None and _r1382['size'] < 10:
                            for _k_clr in ('size', 'portion', 'portion_g', 'pPor', 'p100g', 'ppk', 'protpack', 'kcalpack', 'protPor', 'kcalPor', 'kcal_meal', 'saltPor', 'saltPct', 'eur10p', 'eur100k', 'ppe'):
                                _r1382[_k_clr] = None
                            _r1382['portion_source'] = 'unknown'
                            _r1382['dry'] = True
                            _r1382['meal_class'] = 'dry'
                            _r1382['meal_check'] = {'ok': False, 'cls': 'dry', 'reason': 'Trockenprodukt'}
                            _r1382['rank_excluded_reason'] = 'Trockensuppe (kein Fertiggericht)'
                            _r1382['flags'] = [
                                'nur Open Food Facts, kein Laden/Preis – nicht in Rankings',
                                'Score unvollständig (Salz oder ges. Fett fehlt)',
                                'Trockenprodukt: Nährwerte pro 100 g trocken, nicht in Rankings',
                                'Mahlzeit-Check: Trockenprodukt',
                            ]
                            changed_uids.add(_r1382['uid'])

                        # sensecheck 61 (SC61 — P3 follow-up from SC59):
                        # 1. Hofer #861 (Asia Green Garden Udon Nudelschüssel, Erdnuss-Satay, 252 g, 430.9 kcal, 12.1 g P,
                        #    score 32.5, meal_class='light_meal'): include cup-noodle light_meal with 400 <= kcal_meal <= 450
                        #    and 12 <= protPor < 20 in rankableLight (pliLight=31.5, matching meal.ts passesLightRank), set
                        #    explicit rank_excluded_reason on #860/#861/#862, and strip stale 'Score unvollständig' flags
                        #    from SC59-backfilled rows (#860, #861, #862, #876, #1228, #1229, #1235).
                        # 2. Linz Spar live-2026 priceOnly dishes (#69 Hilcona Tortellini Bolognese, #79 Iglo Lasagne al Forno,
                        #    #89/#90 Inzersdorfer Erdäpfelgulasch 400 g & 800 g 2 Portionen, #93 Inzersdorfer Paprikahendlragout
                        #    mit Nockerln, #145/#1163 Little Lunch Thai Curry Eintopf 350 g, #493 Inzersdorfer Bohnen mit Speck
                        #    2 Portionen 800 g, #2727 Inzersdorfer Bauernschmaus 400 g): backfill verified manufacturer /
                        #    SPAR Produktwelt / OpenFoodFacts / exact-twin per-100g nutrition.
                        if os.environ.get('SC61_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC61', '0') != '1':
                            for _sc59_id in (860, 861, 862, 876, 1228, 1229, 1235):
                                _rsc59 = _pmm_by_id.get(_sc59_id)
                                if _rsc59 is not None and _rsc59.get('salt') is not None and _rsc59.get('sat') is not None:
                                    _rsc59['flags'] = [f for f in (_rsc59.get('flags') or []) if 'Score unvollständig' not in f]
                                    changed_uids.add(_rsc59['uid'])

                            _r860 = _pmm_by_id.get(860)
                            if _r860 is not None and _r860.get('store') == 'Hofer':
                                _r860['cprot'] = ['vegetarisch']
                                _r860['rank_excluded_reason'] = '351 kcal/Portion < 400 (Light Meal)'
                                changed_uids.add(_r860['uid'])

                            _r861 = _pmm_by_id.get(861)
                            if _r861 is not None and _r861.get('store') == 'Hofer':
                                _pr861 = _r861.get('price') or 1.99
                                _r861['cprot'] = ['vegetarisch']
                                _r861['pliLight'] = round(0.5 * _r861['score'] + 0.5 * min((_r861['protPor'] / _pr861) / 20.0, 1.0) * 100.0, 1)
                                _r861['rankableLight'] = True
                                _r861['rank_excluded_reason'] = '12.1 g Protein/Portion < 20 (Light Meal)'
                                changed_uids.add(_r861['uid'])

                            _r862 = _pmm_by_id.get(862)
                            if _r862 is not None and _r862.get('store') == 'Hofer':
                                _r862['cprot'] = ['vegetarisch']
                                _r862['pliLight'] = None
                                _r862['rankableLight'] = False
                                _r862['rank_excluded_reason'] = '361 kcal/Portion < 400, Score 28.5 < 30 (Light Meal)'
                                changed_uids.add(_r862['uid'])

                            # #69 Spar | Hilcona Tortellini Bolognese (250 g, p/2020005979116, EAN 7610227954746)
                            _r69 = _pmm_by_id.get(69)
                            if _r69 is not None and _r69.get('store') == 'Spar':
                                _r69['ean'] = '7610227954746'
                                _r69['url'] = 'https://www.interspar.at/shop/lebensmittel/hilcona-tortellini-bolognese/p/2020005979116'
                                _r69['img'] = _r69.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/2020005979116/dt_main.jpg'
                                _r69['kcal'] = 252.0
                                _r69['p100'] = 9.7
                                _r69['fat'] = 5.4
                                _r69['sat'] = 1.9
                                _r69['carbs'] = 40.0
                                _r69['sugar'] = 2.7
                                _r69['fib'] = 2.3
                                _r69['salt'] = 1.5
                                _r69['ing'] = 'WEIZENMEHL, Wasser, Rindfleisch 12 %, HARTWEIZENGRIESS, EIER, Tomatenmarkkonzentrat 5 %, Reisgriess, Zwiebeln 2 %, Karotten 2 %, Speisesalz, Rapsöl, Knoblauch, Zucker, Petersilie, Gewürze, Zwiebeln geröstet (Zwiebeln, Rapsöl), Zitronensaftkonzentrat, Hefe.'
                                _r69['priceOnly'] = False
                                _r69['incomplete'] = False
                                _r69['nutrition_source'] = 'https://de.hilcona.com/sortiment/detail/tortellini-bolognese/ & SPAR Produktwelt (p/2020005979116, EAN 7610227954746)'
                                _x69 = {
                                    'name': _r69.get('name'), 'size_g': 250.0, 'packaging': _r69.get('pack'),
                                    'kcal_100': 252.0, 'protein_100': 9.7, 'fat_100': 5.4,
                                    'satfat_100': 1.9, 'carbs_100': 40.0, 'sugar_100': 2.7,
                                    'fiber_100': 2.3, 'salt_100': 1.5, 'ingredients': _r69['ing'], 'store': 'Spar',
                                }
                                _v69 = V2.score_v2(_x69)
                                _r69['score'] = _v69.get('health_score')
                                _r69['score_parts'] = _v69.get('score_parts')
                                _r69['day_pct'] = _v69.get('day_pct')
                                _r69['nova'] = _v69.get('nova')
                                _r69['nova_source'] = _v69.get('nova_source')
                                _r69['veg_pct'] = _v69.get('veg_pct')
                                _r69['veg_source'] = _v69.get('veg_source')
                                _r69['kcal_meal'] = 630
                                _r69['kcalPor'] = 630.0
                                _r69['kcalpack'] = 630.0
                                _r69['protPor'] = 24.2
                                _r69['protpack'] = 24.2
                                _r69['saltPor'] = 3.75
                                _r69['saltPct'] = 62
                                _pr69 = _r69.get('price') or 3.59
                                _r69['ppe'] = round(24.2 / _pr69, 1)
                                _r69['eur10p'] = round(_pr69 / 2.42, 2)
                                _r69['eur100k'] = round(_pr69 / 6.3, 2)
                                _r69['meal_class'] = 'snack_side'
                                _r69['meal_check'] = {
                                    'portion': 250, 'kcal': 630, 'protein': 24.2,
                                    'ok': False, 'cls': 'snack_side',
                                    'reason': 'Frische gefüllte Pasta (braucht Sauce) – Zutat/Beilage',
                                }
                                _r69['rank_excluded_reason'] = 'Frische gefüllte Pasta (braucht Sauce) – Zutat/Beilage'
                                _r69['flags'] = [
                                    f for f in (_r69.get('flags') or [])
                                    if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                ]
                                changed_uids.add(_r69['uid'])

                            # #79 Spar | Iglo Lasagne al Forno (700 g, por 350 g, p/577052, dupOf #1114)
                            _r79 = _pmm_by_id.get(79)
                            _r1114 = _pmm_by_id.get(1114)
                            if _r79 is not None and _r1114 is not None and _r79.get('store') == 'Spar':
                                for _k79 in ('kcal', 'p100', 'fat', 'sat', 'carbs', 'sugar', 'fib', 'salt', 'ing', 'ean',
                                             'score', 'scoreV1', 'score_parts', 'day_pct', 'nova', 'nova_source', 'veg_pct', 'veg_source',
                                             'kcal_meal', 'kcalPor', 'kcalpack', 'protPor', 'protpack', 'saltPor', 'saltPct',
                                             'ppe', 'eur10p', 'eur100k', 'meal_class', 'meal_check'):
                                    if _r1114.get(_k79) is not None:
                                        _r79[_k79] = _r1114[_k79]
                                _r79['img'] = _r79.get('img') or _r1114.get('img')
                                _r79['priceOnly'] = False
                                _r79['incomplete'] = False
                                _r79['nutrition_source'] = 'INTERSPAR Webshop (p/577052, Zwilling #1114)'
                                _r79['rankable'] = False
                                _r79['pli'] = None
                                _r79['rank_excluded_reason'] = 'Duplikat von #1114 (gleiche Shop-URL, gleiche Größe/Preis)'
                                _r79['flags'] = [
                                    f for f in (_r79.get('flags') or [])
                                    if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                ]
                                changed_uids.add(_r79['uid'])

                            # #89 Spar | Inzersdorfer Erdäpfelgulasch 400 G (p/786140, EAN 9017100003061): backfill sat=1.4 from Alfies twin #3928
                            _r89 = _pmm_by_id.get(89)
                            if _r89 is not None and _r89.get('store') == 'Spar':
                                _r89['sat'] = 1.4
                                _r89['ean'] = _r89.get('ean') or '9017100003061'
                                _r89['img'] = _r89.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/786140/dt_main.jpg'
                                _r89['incomplete'] = False
                                _r89['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/erdaepfelgulasch/ & Zwilling #3928 (400 g, EAN 9017100003061)'
                                _x89 = {
                                    'name': _r89.get('name'), 'size_g': 400.0, 'packaging': _r89.get('pack'),
                                    'kcal_100': _r89['kcal'], 'protein_100': _r89['p100'], 'fat_100': _r89['fat'],
                                    'satfat_100': 1.4, 'carbs_100': _r89['carbs'], 'sugar_100': _r89['sugar'],
                                    'fiber_100': _r89.get('fib'), 'salt_100': _r89['salt'],
                                    'ingredients': _r89.get('ing'), 'store': 'Spar',
                                }
                                _v89 = V2.score_v2(_x89)
                                _r89['score'] = _v89.get('health_score')
                                _r89['score_parts'] = _v89.get('score_parts')
                                _r89['day_pct'] = _v89.get('day_pct')
                                _r89['meal_class'] = 'light_meal'
                                _r89['rank_excluded_reason'] = '368 kcal/Portion < 400, 10.0 g Protein/Portion < 12'
                                _r89['flags'] = [f for f in (_r89.get('flags') or []) if 'Score unvollständig' not in f]
                                changed_uids.add(_r89['uid'])

                            # #90 Spar | Inzersdorfer Erdäpfelgulasch 2 Portionen (800 g, por 400 g, p/4092506, EAN 9017100004778)
                            _r90 = _pmm_by_id.get(90)
                            _r2174 = _pmm_by_id.get(2174)
                            if _r90 is not None and _r90.get('store') == 'Spar':
                                _r90['ean'] = '9017100004778'
                                _r90['img'] = _r90.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/4092506/dt_main.jpg'
                                _r90['kcal'] = 94.0
                                _r90['p100'] = 2.2
                                _r90['fat'] = 5.8
                                _r90['sat'] = 1.9
                                _r90['carbs'] = 7.7
                                _r90['sugar'] = 1.2
                                _r90['salt'] = 1.2
                                if _r2174 is not None:
                                    for _k90 in ('ing', 'allerg', 'nova', 'nova_source', 'veg_pct', 'veg_source', 'score', 'score_parts', 'day_pct', 'herst', 'ort', 'state', 'pid', 'prodSlug'):
                                        if _r2174.get(_k90) is not None and not _r90.get(_k90):
                                            _r90[_k90] = _r2174[_k90]
                                _r90['priceOnly'] = False
                                _r90['incomplete'] = False
                                _r90['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/erdaepfelgulasch/ & 800-g-Zwilling #2174 (EAN 9017100004778)'
                                _r90['portion'] = 400
                                _r90['portion_g'] = 400
                                _r90['portion_source'] = 'name_portions'
                                _pr90 = _r90.get('price') or 5.49
                                _r90['pPor'] = round(_pr90 / 2.0, 2)
                                _r90['pPorEff'] = _r90['pPor']
                                _r90['kcal_meal'] = 376
                                _r90['kcalPor'] = 376.0
                                _r90['kcalpack'] = 752.0
                                _r90['protPor'] = 8.8
                                _r90['protpack'] = 17.6
                                _r90['saltPor'] = 4.8
                                _r90['saltPct'] = 80
                                _r90['ppe'] = round(17.6 / _pr90, 1)
                                _r90['eur10p'] = round(_pr90 / 1.76, 2)
                                _r90['eur100k'] = round(_pr90 / 7.52, 2)
                                _r90['meal_class'] = 'light_meal'
                                _r90['meal_check'] = {'portion': 400, 'kcal': 376, 'protein': 8.8, 'ok': False, 'cls': 'light_meal', 'reason': '376 kcal/Portion < 400'}
                                _r90['rankable'] = False
                                _r90['rankableLight'] = False
                                _r90['rank_excluded_reason'] = '376 kcal/Portion < 400, 8.8 g Protein/Portion < 12'
                                _r90['flags'] = [
                                    f for f in (_r90.get('flags') or [])
                                    if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                ]
                                if 'Mahlzeit-Check: 376 kcal/Portion < 400' not in _r90['flags']:
                                    _r90['flags'].append('Mahlzeit-Check: 376 kcal/Portion < 400')
                                changed_uids.add(_r90['uid'])

                            # #93 Spar | Inzersdorfer Paprikahendlragout mit Nockerln (300 g, p/5442348)
                            _r93 = _pmm_by_id.get(93)
                            _r955 = _pmm_by_id.get(955)
                            if _r93 is not None and _r93.get('store') == 'Spar':
                                _r93['img'] = _r93.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/5442348/dt_main.jpg'
                                _r93['kcal'] = 158.0
                                _r93['p100'] = 7.9
                                _r93['fat'] = 7.6
                                _r93['sat'] = 2.7
                                _r93['carbs'] = 14.0
                                _r93['sugar'] = 2.3
                                _r93['salt'] = 1.5
                                if _r955 is not None:
                                    for _k93 in ('ing', 'allerg', 'score', 'scoreV1', 'score_parts', 'day_pct', 'herst', 'ort', 'state', 'pid', 'prodSlug'):
                                        if _r955.get(_k93) is not None and not _r93.get(_k93):
                                            _r93[_k93] = _r955[_k93]
                                _r93['priceOnly'] = False
                                _r93['incomplete'] = False
                                _r93['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/paprikahendlragout/ & Billa-Zwilling #955 (300 g)'
                                _r93['kcal_meal'] = 474
                                _r93['kcalPor'] = 474.0
                                _r93['kcalpack'] = 474.0
                                _r93['protPor'] = 23.7
                                _r93['protpack'] = 23.7
                                _r93['saltPor'] = 4.5
                                _r93['saltPct'] = 75
                                _pr93 = _r93.get('price') or 5.99
                                _r93['ppe'] = round(23.7 / _pr93, 1)
                                _r93['eur10p'] = round(_pr93 / 2.37, 2)
                                _r93['eur100k'] = round(_pr93 / 4.74, 2)
                                _r93['meal_class'] = 'meal'
                                _r93['meal_check'] = {'portion': 300, 'kcal': 474, 'protein': 23.7, 'ok': True, 'cls': 'meal', 'reason': None}
                                _r93['rankable'] = False
                                _r93['pli'] = None
                                _r93['rank_excluded_reason'] = 'Gesundheits-Score unter 30 (24.6)'
                                _r93['flags'] = [
                                    f for f in (_r93.get('flags') or [])
                                    if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                ]
                                changed_uids.add(_r93['uid'])

                            # #145 & #1163 Spar | Little Lunch Thai Curry Eintopf (350 g, p/2020005794535, EAN 4280000878946)
                            _r456 = _pmm_by_id.get(456)
                            for _ll_id in (145, 1163):
                                _rll = _pmm_by_id.get(_ll_id)
                                if _rll is not None and _rll.get('store') == 'Spar':
                                    _rll['ean'] = '4280000878946'
                                    _rll['img'] = _rll.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/2020005794535/dt_main.jpg'
                                    _rll['kcal'] = 60.0
                                    _rll['p100'] = 1.6
                                    _rll['fat'] = 1.9
                                    _rll['sat'] = 0.4
                                    _rll['carbs'] = 8.0
                                    _rll['sugar'] = 3.1
                                    _rll['salt'] = 1.1
                                    if _r456 is not None:
                                        for _kll in ('ing', 'allerg', 'nova', 'nova_source', 'veg_pct', 'veg_source', 'score', 'score_parts', 'day_pct'):
                                            if _r456.get(_kll) is not None and not _rll.get(_kll):
                                                _rll[_kll] = _r456[_kll]
                                    _rll['priceOnly'] = False
                                    _rll['incomplete'] = False
                                    _rll['nutrition_source'] = 'https://world.openfoodfacts.org/product/4280000878946 & dm-Zwilling #456 (350 g)'
                                    _rll['kcal_meal'] = 210
                                    _rll['kcalPor'] = 210.0
                                    _rll['kcalpack'] = 210.0
                                    _rll['protPor'] = 5.6
                                    _rll['protpack'] = 5.6
                                    _rll['saltPor'] = 3.85
                                    _rll['saltPct'] = 64
                                    _prll = _rll.get('price') or 3.49
                                    _rll['ppe'] = round(5.6 / _prll, 1)
                                    _rll['eur10p'] = round(_prll / 0.56, 2)
                                    _rll['eur100k'] = round(_prll / 2.1, 2)
                                    _rll['meal_class'] = 'snack_side'
                                    _rll['meal_check'] = {'portion': 350, 'kcal': 210, 'protein': 5.6, 'ok': False, 'cls': 'snack_side', 'reason': '210 kcal/Portion – Snack/Beilage'}
                                    _rll['rankable'] = False
                                    _rll['rankableLight'] = False
                                    _rll['rank_excluded_reason'] = '210 kcal/Portion – Snack/Beilage' if _ll_id == 1163 else 'Duplikat von #1163 (210 kcal/Portion – Snack/Beilage)'
                                    _rll['flags'] = [
                                        f for f in (_rll.get('flags') or [])
                                        if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                    ]
                                    if 'Mahlzeit-Check: 210 kcal/Portion – Snack/Beilage' not in _rll['flags']:
                                        _rll['flags'].append('Mahlzeit-Check: 210 kcal/Portion – Snack/Beilage')
                                    changed_uids.add(_rll['uid'])

                            # #493 Spar | Inzersdorfer Bohnen mit Speck 2 Portionen (800 g, por 400 g, p/6115227)
                            _r493 = _pmm_by_id.get(493)
                            _r1034 = _pmm_by_id.get(1034)
                            if _r493 is not None and _r493.get('store') == 'Spar':
                                _r493['img'] = _r493.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/6115227/dt_main.jpg'
                                _r493['kcal'] = 172.0
                                _r493['p100'] = 6.3
                                _r493['fat'] = 9.3
                                _r493['sat'] = 3.1
                                _r493['carbs'] = 13.0
                                _r493['sugar'] = 1.3
                                _r493['salt'] = 1.1
                                if _r1034 is not None:
                                    for _k493 in ('ing', 'allerg', 'herst', 'ort', 'state', 'pid', 'prodSlug'):
                                        if _r1034.get(_k493) is not None and not _r493.get(_k493):
                                            _r493[_k493] = _r1034[_k493]
                                _r493['priceOnly'] = False
                                _r493['incomplete'] = False
                                _r493['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/bohnen-mit-speck/ & Billa-800g-Zwilling #1034'
                                _x493 = {
                                    'name': _r493.get('name'), 'size_g': 800.0, 'packaging': _r493.get('pack'),
                                    'kcal_100': 172.0, 'protein_100': 6.3, 'fat_100': 9.3,
                                    'satfat_100': 3.1, 'carbs_100': 13.0, 'sugar_100': 1.3,
                                    'fiber_100': None, 'salt_100': 1.1,
                                    'ingredients': _r493.get('ing'), 'store': 'Spar',
                                }
                                _v493 = V2.score_v2(_x493)
                                _r493['score'] = _v493.get('health_score')
                                _r493['score_parts'] = _v493.get('score_parts')
                                _r493['day_pct'] = _v493.get('day_pct')
                                _r493['portion'] = 400
                                _r493['portion_g'] = 400
                                _r493['portion_source'] = 'name_portions'
                                _pr493 = _r493.get('price') or 5.49
                                _r493['pPor'] = round(_pr493 / 2.0, 2)
                                _r493['pPorEff'] = _r493['pPor']
                                _r493['kcal_meal'] = 688
                                _r493['kcalPor'] = 688.0
                                _r493['kcalpack'] = 1376.0
                                _r493['protPor'] = 25.2
                                _r493['protpack'] = 50.4
                                _r493['saltPor'] = 4.4
                                _r493['saltPct'] = 73
                                _r493['ppe'] = round(50.4 / _pr493, 1)
                                _r493['eur10p'] = round(_pr493 / 5.04, 2)
                                _r493['eur100k'] = round(_pr493 / 13.76, 2)
                                _r493['meal_class'] = 'meal'
                                _r493['meal_check'] = {'portion': 400, 'kcal': 688, 'protein': 25.2, 'ok': True, 'cls': 'meal', 'reason': None}
                                _r493['rankable'] = False
                                _r493['pli'] = None
                                _r493['rank_excluded_reason'] = 'Gesundheits-Score unter 30 (20.7)'
                                _r493['flags'] = [
                                    f for f in (_r493.get('flags') or [])
                                    if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                ]
                                changed_uids.add(_r493['uid'])

                            # #2727 Spar | Inzersdorfer Bauernschmaus (400 g, p/2020005819511)
                            _r2727 = _pmm_by_id.get(2727)
                            _r958 = _pmm_by_id.get(958)
                            if _r2727 is not None and _r2727.get('store') == 'Spar':
                                _r2727['img'] = _r2727.get('img') or 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/2020005819511/dt_main.jpg'
                                _r2727['kcal'] = 94.0
                                _r2727['p100'] = 2.1
                                _r2727['fat'] = 5.5
                                _r2727['sat'] = 2.0
                                _r2727['carbs'] = 8.3
                                _r2727['sugar'] = 1.7
                                _r2727['salt'] = 1.2
                                if _r958 is not None:
                                    for _k2727 in ('ing', 'allerg', 'herst', 'ort', 'state', 'pid', 'prodSlug'):
                                        if _r958.get(_k2727) is not None and not _r2727.get(_k2727):
                                            _r2727[_k2727] = _r958[_k2727]
                                _r2727['priceOnly'] = False
                                _r2727['incomplete'] = False
                                _r2727['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/bauernschmaus/ & Billa-Zwilling #958 (400 g)'
                                _x2727 = {
                                    'name': _r2727.get('name'), 'size_g': 400.0, 'packaging': _r2727.get('pack'),
                                    'kcal_100': 94.0, 'protein_100': 2.1, 'fat_100': 5.5,
                                    'satfat_100': 2.0, 'carbs_100': 8.3, 'sugar_100': 1.7,
                                    'fiber_100': None, 'salt_100': 1.2,
                                    'ingredients': _r2727.get('ing'), 'store': 'Spar',
                                }
                                _v2727 = V2.score_v2(_x2727)
                                _r2727['score'] = _v2727.get('health_score')
                                _r2727['score_parts'] = _v2727.get('score_parts')
                                _r2727['day_pct'] = _v2727.get('day_pct')
                                _r2727['kcal_meal'] = 376
                                _r2727['kcalPor'] = 376.0
                                _r2727['kcalpack'] = 376.0
                                _r2727['protPor'] = 8.4
                                _r2727['protpack'] = 8.4
                                _r2727['saltPor'] = 4.8
                                _r2727['saltPct'] = 80
                                _pr2727 = _r2727.get('price') or 4.99
                                _r2727['ppe'] = round(8.4 / _pr2727, 1)
                                _r2727['eur10p'] = round(_pr2727 / 0.84, 2)
                                _r2727['eur100k'] = round(_pr2727 / 3.76, 2)
                                _r2727['meal_class'] = 'light_meal'
                                _r2727['meal_check'] = {'portion': 400, 'kcal': 376, 'protein': 8.4, 'ok': False, 'cls': 'light_meal', 'reason': '376 kcal/Portion < 400'}
                                _r2727['rankable'] = False
                                _r2727['rankableLight'] = False
                                _r2727['rank_excluded_reason'] = '376 kcal/Portion < 400, 8.4 g Protein/Portion < 12'
                                _r2727['flags'] = [
                                    f for f in (_r2727.get('flags') or [])
                                    if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                ]
                                if 'Mahlzeit-Check: 376 kcal/Portion < 400' not in _r2727['flags']:
                                    _r2727['flags'].append('Mahlzeit-Check: 376 kcal/Portion < 400')
                                changed_uids.add(_r2727['uid'])

                            # sensecheck 62: P1 (P1b + P1a), P2 (P2a + P2b), P3 data hygiene & verified supermarket nutrition backfills
                            if os.environ.get('SC62_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC62', '0') != '1':
                                # --- Step A: P1b – Rescue real complete meals misclassified in stage in ('base', 'side', 'veg') BEFORE P1a ---
                                # 1. Upgrade non-ranked or already-scored real meals in ('base', 'side', 'veg') to stage='meal', gang='haupt', component=False
                                for _p1b_id in (
                                    23, 35, 561, 1484, 1723, 1755, 1783, 1788, 1797, 1847, 1891, 2119, 2314, 2317,
                                    2404, 2585, 2586, 3037, 3050, 3062, 3313, 3660, 3662, 3668, 3672,
                                    3752, 3753, 3756, 3757, 3764, 3952, 3973,
                                ):
                                    _rp1b = _pmm_by_id.get(_p1b_id)
                                    if _rp1b is not None:
                                        _rp1b['stage'] = 'meal'
                                        _rp1b['gang'] = 'haupt'
                                        _rp1b['component'] = False
                                        changed_uids.add(_rp1b['uid'])

                                # 2. Full meals rescued by P1b that now qualify for rankable=True:
                                # #23 [Billa] Iglo Lachs-Spinat-Lasagne (330 g, 4.99 €, 521 kcal, 23.8 g P, score 41.1)
                                # #3050 [bofrost] Lachs-Lasagne (800 g, por 400 g, pPorEff 8.0 €, 620 kcal, 31.6 g P, score 33.0)
                                # #3668 [FitTaste] hähnchen tikka masala (380 g, 8.99 €, pPorEff 10.49 €, 414 kcal, 38.0 g P, score 52.0)
                                # #3037 [bofrost] Moussaka Kartoffelauflauf (800 g, por 400 g, pPorEff 8.24 €, 432 kcal, 23.6 g P, score 46.1)
                                for _p1b_rk_id in (23, 1484, 3050, 3668, 3037):
                                    _rk = _pmm_by_id.get(_p1b_rk_id)
                                    if _rk is not None:
                                        _ep_rk = _rk.get('pPorEff') or _rk.get('pPor') or _rk.get('price')
                                        _rk['pPorEff'] = _ep_rk
                                        _rk['rankable'] = True
                                        _rk['rankableLight'] = False
                                        _rk['rank_excluded_reason'] = None
                                        _pe_rk = min(100.0, (_rk['protPor'] / _ep_rk) * 5.0)
                                        _rk['pli'] = round(0.5 * _rk['score'] + 0.5 * _pe_rk, 1)
                                        changed_uids.add(_rk['uid'])

                                # 3. Light meals rescued by P1b that qualify for rankableLight=True:
                                # #3660 [FitTaste] hähnchen mediterran (342 kcal, 28.9 g P, score 43.7, pPorEff 10.49)
                                # #3662 [FitTaste] hähnchengeschnetzeltes (289 kcal, 31.5 g P, score 50.2, pPorEff 10.49)
                                # #3672 [FitTaste] hähnchen kürbis-erdnuss (342 kcal, 28.1 g P, score 52.3, pPorEff 10.49)
                                # #35 [Billa] Schär glutenfreie Lasagne (384 kcal, 15.6 g P, score 38.8, pPor 5.19)
                                # #2119 [Billa] Iglo Fisch'n"Rösti (322 kcal, 16.5 g P, score 41.6, pPor 3.25)
                                for _p1b_lt_id in (3660, 3662, 3672, 35, 2119):
                                    _rlt = _pmm_by_id.get(_p1b_lt_id)
                                    if _rlt is not None:
                                        _ep_lt = _rlt.get('pPorEff') or _rlt.get('pPor') or _rlt.get('price')
                                        _rlt['pPorEff'] = _ep_lt
                                        _rlt['rankable'] = False
                                        _rlt['pli'] = None
                                        _rlt['rankableLight'] = True
                                        _pe_lt = min(100.0, (_rlt['protPor'] / _ep_lt) * 5.0)
                                        _rlt['pliLight'] = round(0.5 * _rlt['score'] + 0.5 * _pe_lt, 1)
                                        _mc_rsn = (_rlt.get('meal_check') or {}).get('reason') or f"{int(_rlt['kcalPor'])} kcal/Portion < 400"
                                        _rlt['rank_excluded_reason'] = f"{_mc_rsn} (Light Meal)"
                                        changed_uids.add(_rlt['uid'])

                                # #561 [Billa] BILLA Spinat Cannelloni (400 g, 3.19 €, 708 kcal, 23.6 g P, score 22.6 < 30)
                                _r561 = _pmm_by_id.get(561)
                                if _r561 is not None:
                                    _r561['rankable'] = False
                                    _r561['pli'] = None
                                    _r561['rank_excluded_reason'] = 'Gesundheits-Score unter 30 (22.6)'
                                    changed_uids.add(_r561['uid'])

                                # --- Step B: P2a & P2b – Linz complete meals falsely blocked as component=True or multi_portion (SC61 §3.2) ---
                                # P2a-1: #922 Billa & #2777 Spar Inzersdorfer Champignonschnitzerl mit Gemüsereis (380 g, 5.99 €)
                                _r922 = _pmm_by_id.get(922)
                                _r2777 = _pmm_by_id.get(2777)
                                if _r2777 is not None and _r922 is not None:
                                    for _k2777 in ('kcal', 'p100', 'fat', 'sat', 'carbs', 'sugar', 'fib', 'salt', 'p100k', 'kcalpack', 'protpack', 'kcalPor', 'protPor', 'saltPor', 'saltPct', 'kcal_meal', 'score', 'score_parts', 'day_pct', 'scoreV1'):
                                        _r2777[_k2777] = _r922.get(_k2777)
                                    _r2777['priceOnly'] = False
                                    _r2777['incomplete'] = False
                                    _r2777['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/champignonschnitzerl-mit-gemuesereis/ & Billa-Zwilling #922 (380 g)'
                                    _pr2777_c = _r2777.get('price') or 5.99
                                    _r2777['pPor'] = _pr2777_c
                                    _r2777['pPorEff'] = _pr2777_c
                                    _r2777['ppe'] = round(20.9 / _pr2777_c, 1)
                                    _r2777['eur10p'] = round(_pr2777_c / 2.09, 2)
                                    _r2777['eur100k'] = round(_pr2777_c / 4.18, 2)
                                    _r922['alsoAt'] = sorted(list(set((_r922.get('alsoAt') or []) + ['Spar'])))
                                    _r2777['alsoAt'] = sorted(list(set((_r2777.get('alsoAt') or []) + ['Billa'])))
                                    changed_uids.add(_r2777['uid'])

                                # P2a-2: Full complete meals upgraded from component=True -> rankable=True
                                # #626 [Billa] Omis Schmankerl Kalbsbutterschnitzel mit Erdäpfelpüree (330 g, 3.79 €, 412 kcal, 31.4 g P, score 45.8, pli 43.6)
                                # #938 [Billa] Inzersdorfer Zwiebelrindsbraten mit Hörnchen (380 g, 5.99 €, 452 kcal, 24.7 g P, score 34.5, pli 27.6)
                                # #922 [Billa] & #2777 [Spar] Inzersdorfer Champignonschnitzel mit Gemüsereis (380 g, 5.99 €, 418 kcal, 20.9 g P, score 30.1, pli 23.8)
                                # #400 [Billa] Iglo Faschierte Laibchen mit Erdäpfelpüree (350 g, 7.19 €, 448 kcal, 26.2 g P, score 42.5, pli 30.4)
                                # #598 [Billa] BILLA Backhendl Bowl (340 g, 7.99 €, 493 kcal, 34.0 g P, score 36.7, pli 29.0)
                                # #3151 [Goldblatt] Chili con Tempeh (500 g, 11.99 €, pPorEff 12.99 €, 485 kcal, 35.0 g P, score 58.4, pli 35.9)
                                for _p2a_id, _p2a_stg in (
                                    (626, 'meal'), (938, 'meal'), (922, 'meal'), (2777, 'meal'),
                                    (400, 'meal'), (598, 'meal'), (3151, 'stew'),
                                ):
                                    _rp2a = _pmm_by_id.get(_p2a_id)
                                    if _rp2a is not None:
                                        _rp2a['stage'] = _p2a_stg
                                        _rp2a['gang'] = 'haupt'
                                        _rp2a['component'] = False
                                        _rp2a['meal_class'] = 'meal'
                                        _por_p2a = int(_rp2a.get('portion') or _rp2a.get('size') or 400)
                                        _rp2a['portion'] = _por_p2a
                                        _rp2a['portion_g'] = _por_p2a
                                        _rp2a['meal_check'] = {
                                            'portion': _por_p2a,
                                            'kcal': int(round(_rp2a['kcalPor'])),
                                            'protein': float(_rp2a['protPor']),
                                            'ok': True,
                                            'cls': 'meal',
                                            'reason': None,
                                        }
                                        _rp2a['flags'] = [
                                            f for f in (_rp2a.get('flags') or [])
                                            if 'Proteinkomponente' not in f and 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                        ]
                                        _ep_p2a = _rp2a.get('pPorEff') or _rp2a.get('pPor') or _rp2a.get('price')
                                        _rp2a['pPorEff'] = _ep_p2a
                                        _rp2a['rankable'] = True
                                        _rp2a['rankableLight'] = False
                                        _rp2a['rank_excluded_reason'] = None
                                        _pe_p2a = min(100.0, (_rp2a['protPor'] / _ep_p2a) * 5.0)
                                        _rp2a['pli'] = round(0.5 * _rp2a['score'] + 0.5 * _pe_p2a, 1)
                                        changed_uids.add(_rp2a['uid'])

                                # P2a-3: Light complete meals upgraded from component=True -> rankableLight=True
                                # #612 [Billa] Omis Schmankerl Cevapcici Letscho (360 g, 2.69 €, 446 kcal, 19.8 g P, score 35.1, pliLight 36.0)
                                # #614 [Billa] Omis Schmankerl Surbraten mit Knödel (330 g, 5.29 €, 396 kcal, 25.1 g P, score 32.3, pliLight 28.0)
                                # #605 [Billa] Simply Good Kichererbsencurry mit Tofu (370 g, 6.99 €, 485 kcal, 18.1 g P, score 35.0, pliLight 24.0)
                                for _p2l_id, _p2l_rsn in (
                                    (612, '19.8 g Protein/Portion < 20'),
                                    (614, '396 kcal/Portion < 400'),
                                    (605, '18.1 g Protein/Portion < 20'),
                                ):
                                    _rp2l = _pmm_by_id.get(_p2l_id)
                                    if _rp2l is not None:
                                        _rp2l['stage'] = 'meal'
                                        _rp2l['gang'] = 'haupt'
                                        _rp2l['component'] = False
                                        _rp2l['meal_class'] = 'light_meal'
                                        _por_p2l = int(_rp2l.get('portion') or _rp2l.get('size') or 350)
                                        _rp2l['portion'] = _por_p2l
                                        _rp2l['portion_g'] = _por_p2l
                                        _rp2l['meal_check'] = {
                                            'portion': _por_p2l,
                                            'kcal': int(round(_rp2l['kcalPor'])),
                                            'protein': float(_rp2l['protPor']),
                                            'ok': False,
                                            'cls': 'light_meal',
                                            'reason': _p2l_rsn,
                                        }
                                        _rp2l['flags'] = [f"Mahlzeit-Check: {_p2l_rsn}"]
                                        _ep_p2l = _rp2l.get('pPorEff') or _rp2l.get('pPor') or _rp2l.get('price')
                                        _rp2l['pPorEff'] = _ep_p2l
                                        _rp2l['rankable'] = False
                                        _rp2l['pli'] = None
                                        _rp2l['rankableLight'] = True
                                        _pe_p2l = min(100.0, (_rp2l['protPor'] / _ep_p2l) * 5.0)
                                        _rp2l['pliLight'] = round(0.5 * _rp2l['score'] + 0.5 * _pe_p2l, 1)
                                        _rp2l['rank_excluded_reason'] = f"{_p2l_rsn} (Light Meal)"
                                        changed_uids.add(_rp2l['uid'])

                                # P2b-1: #495 Spar & #1033 Billa Inzersdorfer Linsen mit Speck (800 g, 2 Portionen à 400 g)
                                _r1033 = _pmm_by_id.get(1033)
                                _r495 = _pmm_by_id.get(495)
                                if _r495 is not None and _r1033 is not None:
                                    for _k495 in ('kcal', 'p100', 'fat', 'sat', 'carbs', 'sugar', 'fib', 'salt', 'p100k', 'kcalpack', 'protpack', 'kcalPor', 'protPor', 'saltPor', 'saltPct', 'score', 'score_parts', 'day_pct', 'scoreV1'):
                                        _r495[_k495] = _r1033.get(_k495)
                                    _r495['priceOnly'] = False
                                    _r495['incomplete'] = False
                                    _r495['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/linsen-mit-speck-800g/ & Billa-800g-Zwilling #1033'
                                    _pr495 = _r495.get('price') or 5.49
                                    _r495['ppe'] = round(44.0 / _pr495, 1)
                                    _r495['eur10p'] = round(_pr495 / 4.4, 2)
                                    _r495['eur100k'] = round(_pr495 / 10.56, 2)
                                    _r1033['alsoAt'] = sorted(list(set((_r1033.get('alsoAt') or []) + ['Spar'])))
                                    _r495['alsoAt'] = sorted(list(set((_r495.get('alsoAt') or []) + ['Billa'])))
                                    changed_uids.add(_r495['uid'])

                                # P2b-2: Set 400 g portion (2 Portionen) on #1033, #495, #2257, #1031, #395, #397
                                for _p2b_id, _p2b_psrc in (
                                    (1033, 'name_portions'), (495, 'name_portions'),
                                    (2257, 'pack_2portions'), (1031, 'pack_2portions'),
                                    (395, 'pack_2portions'), (397, 'pack_2portions'),
                                ):
                                    _rp2b = _pmm_by_id.get(_p2b_id)
                                    if _rp2b is not None:
                                        _rp2b['stage'] = 'stew'
                                        _rp2b['gang'] = 'haupt'
                                        _rp2b['component'] = False
                                        _rp2b['portion'] = 400
                                        _rp2b['portion_g'] = 400
                                        _rp2b['portion_source'] = _p2b_psrc
                                        _pr_p2b = _rp2b.get('price') or 6.49
                                        _rp2b['pPor'] = round(_pr_p2b / 2.0, 2)
                                        _rp2b['pPorEff'] = _rp2b['pPor']
                                        _rp2b['kcal_meal'] = int(round(_rp2b['kcalPor']))
                                        _rp2b['meal_class'] = 'meal'
                                        _rp2b['meal_check'] = {
                                            'portion': 400,
                                            'kcal': int(round(_rp2b['kcalPor'])),
                                            'protein': float(_rp2b['protPor']),
                                            'ok': True,
                                            'cls': 'meal',
                                            'reason': None,
                                        }
                                        _rp2b['flags'] = [
                                            f for f in (_rp2b.get('flags') or [])
                                            if 'Mehrportionen-Packung' not in f and 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                        ]
                                        _rp2b['rankable'] = True
                                        _rp2b['rankableLight'] = False
                                        _rp2b['rank_excluded_reason'] = None
                                        _pe_p2b = min(100.0, (_rp2b['protPor'] / _rp2b['pPorEff']) * 5.0)
                                        _rp2b['pli'] = round(0.5 * _rp2b['score'] + 0.5 * _pe_p2b, 1)
                                        changed_uids.add(_rp2b['uid'])

                                # Cross-store duplicate demotion on Billa #1031 (twin of Spar #2257, same price 6.49 €, same score 38.5; Spar #2257 has EAN 9000295832349)
                                _r2257_c = _pmm_by_id.get(2257)
                                _r1031_c = _pmm_by_id.get(1031)
                                if _r2257_c is not None and _r1031_c is not None:
                                    _r1031_c['rankable'] = False
                                    _r1031_c['pli'] = None
                                    _r1031_c['rank_excluded_reason'] = 'Duplikat (nahe Name/Marke, Ranking)'
                                    if 'Duplikat (nahe Name/Marke, Ranking)' not in (_r1031_c.get('flags') or []):
                                        _r1031_c['flags'] = (_r1031_c.get('flags') or []) + ['Duplikat (nahe Name/Marke, Ranking)']
                                    changed_uids.add(_r1031_c['uid'])

                                # --- Step C: P1a – Sync all remaining stage in ('base', 'side', 'veg') rows ---
                                for _r_p1a in rows:
                                    _stg_p1a = _r_p1a.get('stage')
                                    if _stg_p1a in ('base', 'side', 'veg'):
                                        _mod_p1a = False
                                        if not _r_p1a.get('component'):
                                            _r_p1a['component'] = True
                                            _mod_p1a = True
                                        _cur_mc = _r_p1a.get('meal_class')
                                        if _cur_mc not in ('dry', 'baby', 'drink', 'dessert'):
                                            _tgt_mc = 'raw_ingredient' if _stg_p1a == 'base' else 'snack_side'
                                            if _cur_mc != _tgt_mc:
                                                _r_p1a['meal_class'] = _tgt_mc
                                                _mod_p1a = True
                                        _mc_dict = dict(_r_p1a.get('meal_check') or {})
                                        _tgt_cls = _r_p1a.get('meal_class')
                                        _tgt_rsn = _mc_dict.get('reason') or ('Rohzutat (kein Fertiggericht)' if _stg_p1a == 'base' else 'Beilage/Komponente (keine vollständige Mahlzeit)')
                                        if _mc_dict.get('ok') is not False or _mc_dict.get('cls') != _tgt_cls or _mc_dict.get('reason') != _tgt_rsn:
                                            _mc_dict['ok'] = False
                                            _mc_dict['cls'] = _tgt_cls
                                            _mc_dict['reason'] = _tgt_rsn
                                            _r_p1a['meal_check'] = _mc_dict
                                            _mod_p1a = True
                                        if _r_p1a.get('rankable') or _r_p1a.get('rankableLight') or _r_p1a.get('pli') is not None or _r_p1a.get('pliLight') is not None:
                                            _r_p1a['rankable'] = False
                                            _r_p1a['rankableLight'] = False
                                            _r_p1a['pli'] = None
                                            _r_p1a['pliLight'] = None
                                            _mod_p1a = True
                                        if _mod_p1a:
                                            changed_uids.add(_r_p1a['uid'])

                                # --- Step D: P3 Data Hygiene & Verified Supermarket Nutrition Backfills ---
                                # P3-1: #2878 [LiveFresh] Tikka Masala – Vegane Bowl (400 g) fat: 0.5 -> 5.0 (Atwater 4*7.5 + 9*5.0 + 4*12.0 = 123 kcal ~ 128 kcal, sat=1.1 <= 5.0)
                                _r2878 = _pmm_by_id.get(2878)
                                if _r2878 is not None:
                                    _r2878['fat'] = 5.0
                                    if 'nut_flag' in _r2878:
                                        _r2878['nut_flag'] = None
                                    changed_uids.add(_r2878['uid'])

                                # P3-2: Gurkerl / OFF 10x decimal-shift fixes (#3265, #3282, #3317, #3357, #810, #833, #3470, #1426)
                                for _d10_id, _d10_upd in (
                                    (3265, {'p100': 4.4, 'fat': 8.6, 'sat': 0.7, 'sugar': 1.0, 'fib': 2.4, 'salt': 1.0, 'p100k': 2.44}),
                                    (3282, {'p100': 4.1, 'fat': 7.7, 'sat': 0.7, 'sugar': 5.8, 'fib': 1.5, 'salt': 1.5, 'p100k': 2.61}),
                                    (3317, {'p100': 8.5, 'sat': 2.6, 'carbs': 7.9, 'sugar': 0.5, 'fib': 5.3, 'salt': 0.97, 'p100k': 3.81}),
                                    (3357, {'sugar': 1.19, 'salt': 1.45}),
                                    (810,  {'salt': 1.07}),
                                    (833,  {'salt': 1.28}),
                                    (3470, {'salt': 1.28}),
                                    (1426, {'salt': 1.3}),
                                ):
                                    _rd10 = _pmm_by_id.get(_d10_id)
                                    if _rd10 is not None:
                                        for _k10, _v10 in _d10_upd.items():
                                            _rd10[_k10] = _v10
                                        _sz10 = _rd10.get('size')
                                        _por10 = _rd10.get('portion') or _sz10
                                        if _sz10 and _rd10.get('p100') is not None:
                                            _rd10['protpack'] = round(_rd10['p100'] * _sz10 / 100.0, 1)
                                        if _por10 and _rd10.get('p100') is not None:
                                            _rd10['protPor'] = round(_rd10['p100'] * _por10 / 100.0, 1)
                                        if _por10 and _rd10.get('salt') is not None:
                                            _rd10['saltPor'] = round(_rd10['salt'] * _por10 / 100.0, 2)
                                            _rd10['saltPct'] = round(_rd10['saltPor'] / 6.0 * 100)
                                        if _rd10.get('price') and _rd10.get('protpack'):
                                            _rd10['ppe'] = round(_rd10['protpack'] / _rd10['price'], 1)
                                            _rd10['eur10p'] = round(_rd10['price'] / (_rd10['protpack'] / 10.0), 2)
                                        _xd10 = {
                                            'name': _rd10.get('name'), 'size_g': _sz10, 'packaging': _rd10.get('pack'),
                                            'kcal_100': _rd10.get('kcal'), 'protein_100': _rd10.get('p100'), 'fat_100': _rd10.get('fat'),
                                            'satfat_100': _rd10.get('sat'), 'carbs_100': _rd10.get('carbs'), 'sugar_100': _rd10.get('sugar'),
                                            'fiber_100': _rd10.get('fib'), 'salt_100': _rd10.get('salt'), 'ingredients': _rd10.get('ing'),
                                            'store': _rd10.get('store'),
                                        }
                                        _vd10 = V2.score_v2(_xd10)
                                        _rd10['score'] = _vd10.get('health_score')
                                        _rd10['score_parts'] = _vd10.get('score_parts')
                                        _rd10['day_pct'] = _vd10.get('day_pct')
                                        _rd10['flags'] = [f for f in (_rd10.get('flags') or []) if 'Großpackung (>100 g Protein/Pkg)' not in f]
                                        if _d10_id in (3265, 3282, 3317) and _por10:
                                            _k_d10 = int(round(_rd10['kcalPor']))
                                            _p_d10 = float(_rd10['protPor'])
                                            _rsn_d10 = f"{_k_d10} kcal/Portion < 400" if _k_d10 >= 300 else f"{_k_d10} kcal/Portion – Snack/Beilage"
                                            _rd10['meal_check'] = {'portion': int(_por10), 'kcal': _k_d10, 'protein': _p_d10, 'ok': False, 'cls': 'snack_side', 'reason': _rsn_d10}
                                        changed_uids.add(_rd10['uid'])

                                # P3-3: Dry soup cubes (#199, #246, #1379) -> meal_class='dry'
                                for _dry_id in (199, 246, 1379):
                                    _rdry = _pmm_by_id.get(_dry_id)
                                    if _rdry is not None:
                                        _rdry['meal_class'] = 'dry'
                                        _mcdry = dict(_rdry.get('meal_check') or {})
                                        _mcdry['ok'] = False
                                        _mcdry['cls'] = 'dry'
                                        _mcdry['reason'] = 'Trockenprodukt/Pulver (Nährwerte unzubereitet)'
                                        _rdry['meal_check'] = _mcdry
                                        changed_uids.add(_rdry['uid'])

                                # P3-4: Verified Supermarket Nutrition Backfills
                                # (a) #453 Spar Youcook Tikka Huhn India Style (420 g, 4.99 €) from #1830 MPreis / #3322 Gurkerl (EAN 4260334165042)
                                _r453 = _pmm_by_id.get(453)
                                _r1830 = _pmm_by_id.get(1830)
                                _r3322 = _pmm_by_id.get(3322)
                                if _r453 is not None and _r1830 is not None:
                                    for _k453 in ('ean', 'kcal', 'p100', 'fat', 'sat', 'carbs', 'sugar', 'fib', 'salt', 'p100k', 'kcalpack', 'protpack', 'kcalPor', 'protPor', 'saltPor', 'saltPct', 'kcal_meal', 'veg_pct', 'veg_source', 'nova', 'nova_source', 'score', 'score_parts', 'day_pct', 'scoreV1'):
                                        if _r1830.get(_k453) is not None:
                                            _r453[_k453] = _r1830[_k453]
                                    _r453['priceOnly'] = False
                                    _r453['incomplete'] = False
                                    _r453['nutrition_source'] = 'Youcook Indian Style Chicken Tikka (EAN 4260334165042, Zwilling #1830/#3322)'
                                    _pr453 = _r453.get('price') or 4.99
                                    _r453['pPor'] = _pr453
                                    _r453['pPorEff'] = _pr453
                                    _r453['ppe'] = round(29.0 / _pr453, 1)
                                    _r453['eur10p'] = round(_pr453 / 2.9, 2)
                                    _r453['eur100k'] = round(_pr453 / 5.42, 2)
                                    _r453['stage'] = 'meal'
                                    _r453['gang'] = 'haupt'
                                    _r453['component'] = False
                                    _r453['meal_class'] = 'meal'
                                    _r453['meal_check'] = {'portion': 420, 'kcal': 542, 'protein': 29.0, 'ok': True, 'cls': 'meal', 'reason': None}
                                    _r453['flags'] = []
                                    _r453['rankable'] = True
                                    _r453['rankableLight'] = False
                                    _r453['rank_excluded_reason'] = None
                                    _pe453 = min(100.0, (29.0 / _pr453) * 5.0)
                                    _r453['pli'] = round(0.5 * _r453['score'] + 0.5 * _pe453, 1)
                                    _r453['alsoAt'] = ['Gurkerl', 'MPreis']
                                    if _r1830 is not None:
                                        _r1830['alsoAt'] = sorted(list(set((_r1830.get('alsoAt') or []) + ['Spar'])))
                                    if _r3322 is not None:
                                        _r3322['alsoAt'] = sorted(list(set((_r3322.get('alsoAt') or []) + ['Spar'])))
                                    changed_uids.add(_r453['uid'])

                                # (b) #2663 Spar Inzersdorfer Bohnensuppe (400 g, 2.99 €) sat/salt from #101 (800 g twin) & inzersdorfer.at
                                _r2663 = _pmm_by_id.get(2663)
                                _r101 = _pmm_by_id.get(101)
                                if _r2663 is not None and _r101 is not None:
                                    _r2663['sat'] = 1.4
                                    _r2663['salt'] = 1.2
                                    _r2663['saltPor'] = 4.8
                                    _r2663['saltPct'] = 80
                                    _r2663['incomplete'] = False
                                    _r2663['score'] = _r101.get('score')  # 32.7
                                    _r2663['score_parts'] = dict(_r101.get('score_parts') or {})
                                    _r2663['day_pct'] = {'kcal': 22, 'protein': 36, 'salt': 80, 'satfat': 28, 'sugar': 5, 'fiber': None}
                                    _r2663['flags'] = [f for f in (_r2663.get('flags') or []) if 'Score unvollständig' not in f]
                                    _r2663['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/bohnensuppe/ & Billa-Zwilling #101'
                                    changed_uids.add(_r2663['uid'])

                                # (c) #496 Spar Inzersdorfer Paprikahendl (400 g, 5.29 €) sat/salt from inzersdorfer.at
                                _r496 = _pmm_by_id.get(496)
                                if _r496 is not None:
                                    _r496['sat'] = 1.3
                                    _r496['salt'] = 1.8
                                    _r496['saltPor'] = 7.2
                                    _r496['saltPct'] = 120
                                    _r496['incomplete'] = False
                                    _x496 = {
                                        'name': _r496.get('name'), 'size_g': 400.0, 'packaging': _r496.get('pack'),
                                        'kcal_100': 93.0, 'protein_100': 7.5, 'fat_100': 4.9,
                                        'satfat_100': 1.3, 'carbs_100': 4.4, 'sugar_100': 2.0,
                                        'fiber_100': None, 'salt_100': 1.8, 'store': 'Spar',
                                    }
                                    _v496 = V2.score_v2(_x496)
                                    _r496['score'] = _v496.get('health_score')
                                    _r496['score_parts'] = _v496.get('score_parts')
                                    _r496['day_pct'] = _v496.get('day_pct')
                                    _r496['flags'] = [f for f in (_r496.get('flags') or []) if 'Score unvollständig' not in f]
                                    _r496['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/paprikahendl/ (EAN 9002600632699)'
                                    changed_uids.add(_r496['uid'])

                                # (d) #102 Spar Inzersdorfer Suppentopf Bohnensuppe 12 Portionen (2900 g, 14.99 €) from inzersdorfer.at
                                _r102 = _pmm_by_id.get(102)
                                if _r102 is not None:
                                    _r102['kcal'] = 122.0
                                    _r102['p100'] = 4.4
                                    _r102['fat'] = 6.8
                                    _r102['sat'] = 2.3
                                    _r102['carbs'] = 9.2
                                    _r102['sugar'] = 1.1
                                    _r102['salt'] = 1.1
                                    _r102['p100k'] = round(4.4 / 122.0 * 100, 2)
                                    _r102['kcalpack'] = 3538.0
                                    _r102['protpack'] = 127.6
                                    _r102['portion'] = 242
                                    _r102['portion_g'] = 242
                                    _r102['portion_source'] = 'name_portions'
                                    _r102['kcalPor'] = 295.0
                                    _r102['kcal_meal'] = 295
                                    _r102['protPor'] = 10.6
                                    _r102['saltPor'] = 2.66
                                    _r102['saltPct'] = 44
                                    _pr102 = _r102.get('price') or 14.99
                                    _r102['pPor'] = round(_pr102 / 12.0, 2)
                                    _r102['pPorEff'] = _r102['pPor']
                                    _r102['ppe'] = round(127.6 / _pr102, 1)
                                    _r102['eur10p'] = round(_pr102 / 12.76, 2)
                                    _r102['eur100k'] = round(_pr102 / 35.38, 2)
                                    _r102['priceOnly'] = False
                                    _r102['incomplete'] = False
                                    _r102['nutrition_source'] = 'https://www.inzersdorfer.at/produkte/bohnensuppe-2900g/'
                                    _x102 = {
                                        'name': _r102.get('name'), 'size_g': 2900.0, 'packaging': _r102.get('pack'),
                                        'kcal_100': 122.0, 'protein_100': 4.4, 'fat_100': 6.8,
                                        'satfat_100': 2.3, 'carbs_100': 9.2, 'sugar_100': 1.1,
                                        'fiber_100': None, 'salt_100': 1.1, 'store': 'Spar',
                                    }
                                    _v102 = V2.score_v2(_x102)
                                    _r102['score'] = _v102.get('health_score')
                                    _r102['score_parts'] = _v102.get('score_parts')
                                    _r102['day_pct'] = _v102.get('day_pct')
                                    _r102['meal_class'] = 'snack_side'
                                    _r102['meal_check'] = {'portion': 242, 'kcal': 295, 'protein': 10.6, 'ok': False, 'cls': 'snack_side', 'reason': '295 kcal/Portion – Snack/Beilage'}
                                    _r102['flags'] = ['Mahlzeit-Check: 295 kcal/Portion – Snack/Beilage']
                                    changed_uids.add(_r102['uid'])

                                # (e) Cross-store & same-store twin nutrition backfills
                                # Format: (target_id, donor_id, hide_donor_dupOf)
                                for _bf_tid, _bf_did, _bf_hide_donor in (
                                    (212, 1471, True),
                                    (1087, 185, True),
                                    (1091, 240, True),
                                    (1092, 237, True),
                                    (235, 3411, True),
                                    (236, 3439, True),
                                    (1125, 1370, True),
                                    (51, 390, False),
                                    (52, 391, False),
                                    (2660, 1979, False),
                                    (2765, 2418, False),
                                    (502, 1995, False),
                                    (2750, 925, False),
                                    (2761, 940, False),
                                    (121, 1003, False),
                                    (2762, 1658, False),
                                    (3492, 1982, False),
                                    (3493, 1981, False),
                                    (3494, 1983, False),
                                ):
                                    _rt = _pmm_by_id.get(_bf_tid)
                                    _rd = _pmm_by_id.get(_bf_did)
                                    if _rt is not None and _rd is not None:
                                        for _kbf in ('kcal', 'p100', 'fat', 'sat', 'carbs', 'sugar', 'fib', 'salt', 'p100k', 'score', 'score_parts', 'day_pct', 'scoreV1', 'dry', 'nutrition_basis'):
                                            if _rd.get(_kbf) is not None:
                                                _rt[_kbf] = _rd[_kbf]
                                        if not _rt.get('size') and _rd.get('size'):
                                            _rt['size'] = _rd['size']
                                            if _rt.get('price') and _rt['size']:
                                                _rt['ppk'] = round(_rt['price'] / _rt['size'] * 1000.0, 2)
                                                _rt['p100g'] = round(_rt['price'] / _rt['size'] * 100.0, 2)
                                        _szt = _rt.get('size')
                                        _port = _rt.get('portion') or _rd.get('portion') or _szt
                                        _rt['portion'] = _port
                                        _rt['portion_g'] = _rd.get('portion_g') or _port
                                        if _szt and _rt.get('kcal') is not None:
                                            _rt['kcalpack'] = round(_rt['kcal'] * _szt / 100.0, 1)
                                        if _szt and _rt.get('p100') is not None:
                                            _rt['protpack'] = round(_rt['p100'] * _szt / 100.0, 1)
                                        if _port and _rt.get('kcal') is not None:
                                            _rt['kcalPor'] = round(_rt['kcal'] * _port / 100.0, 1)
                                            _rt['kcal_meal'] = int(round(_rt['kcalPor']))
                                        if _port and _rt.get('p100') is not None:
                                            _rt['protPor'] = round(_rt['p100'] * _port / 100.0, 1)
                                        if _port and _rt.get('salt') is not None:
                                            _rt['saltPor'] = round(_rt['salt'] * _port / 100.0, 2)
                                            _rt['saltPct'] = round(_rt['saltPor'] / 6.0 * 100)
                                        if _rt.get('price') and _rt.get('protpack'):
                                            _rt['ppe'] = round(_rt['protpack'] / _rt['price'], 1)
                                            _rt['eur10p'] = round(_rt['price'] / (_rt['protpack'] / 10.0), 2)
                                        if _rt.get('price') and _rt.get('kcalpack'):
                                            _rt['eur100k'] = round(_rt['price'] / (_rt['kcalpack'] / 100.0), 2)
                                        _rt['priceOnly'] = False
                                        _rt['incomplete'] = False
                                        _rt['nutrition_source'] = _rd.get('nutrition_source') or f"Zwilling #{_bf_did} ({_rd.get('store')})"
                                        if _rt.get('stage') not in ('base', 'side', 'veg'):
                                            _rt['meal_class'] = _rd.get('meal_class')
                                            _rt['meal_check'] = dict(_rd.get('meal_check') or {})
                                        else:
                                            # Keep P1a invariants on stage='base' rows (#502, #2750, #2761, #121, #2762, #3492-3494)
                                            if _rt.get('dry'):
                                                _rt['meal_class'] = 'dry'
                                                _rt['meal_check'] = {'portion': _port, 'kcal': _rt.get('kcal_meal'), 'protein': _rt.get('protPor'), 'ok': False, 'cls': 'dry', 'reason': 'Trockenprodukt/Pulver (Nährwerte unzubereitet)'}
                                            else:
                                                _rt['meal_class'] = 'raw_ingredient'
                                                _rt['meal_check'] = {'portion': _port, 'kcal': _rt.get('kcal_meal'), 'protein': _rt.get('protPor'), 'ok': False, 'cls': 'raw_ingredient', 'reason': 'Rohzutat (kein Fertiggericht)'}
                                        _rt['flags'] = [
                                            f for f in (_rt.get('flags') or [])
                                            if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f
                                        ]
                                        if _bf_hide_donor:
                                            _rd['dupOf'] = _bf_tid
                                            _rd['dupOfUid'] = _rt.get('uid')
                                            _rd['rankable'] = False
                                            _rd['rankableLight'] = False
                                            _rd['pli'] = None
                                            _rd['pliLight'] = None
                                            changed_uids.add(_rd['uid'])
                                        else:
                                            if _rt.get('store') != _rd.get('store'):
                                                _rt['alsoAt'] = sorted(list(set((_rt.get('alsoAt') or []) + [_rd['store']])))
                                                _rd['alsoAt'] = sorted(list(set((_rd.get('alsoAt') or []) + [_rt['store']])))
                                                changed_uids.add(_rd['uid'])
                                        changed_uids.add(_rt['uid'])

                                # #1399 Billa Gemüsecreme Suppe (duplicate of #1005 Billa Knorr Keiserteller Gemüsecreme Suppe)
                                _r1399 = _pmm_by_id.get(1399)
                                _r1005 = _pmm_by_id.get(1005)
                                if _r1399 is not None and _r1005 is not None:
                                    for _k1399 in ('kcal', 'p100', 'fat', 'sat', 'carbs', 'sugar', 'fib', 'salt', 'p100k', 'kcalpack', 'protpack', 'kcalPor', 'protPor', 'saltPor', 'saltPct', 'kcal_meal', 'score', 'score_parts', 'day_pct', 'scoreV1'):
                                        if _r1005.get(_k1399) is not None:
                                            _r1399[_k1399] = _r1005[_k1399]
                                    _r1399['priceOnly'] = False
                                    _r1399['incomplete'] = False
                                    _r1399['dupOf'] = 1005
                                    _r1399['dupOfUid'] = _r1005.get('uid')
                                    _r1399['flags'] = [f for f in (_r1399.get('flags') or []) if 'Score unvollständig' not in f and 'Nährwerte fehlen' not in f]
                                    changed_uids.add(_r1399['uid'])

                                # Light meals unlocked by twin nutrition backfill (#1091, #51, #52)
                                for _lt_bf_id in (1091, 51, 52):
                                    _rltb = _pmm_by_id.get(_lt_bf_id)
                                    if _rltb is not None and _rltb.get('score') is not None and _rltb.get('protPor') and _rltb.get('price'):
                                        _ep_ltb = _rltb.get('pPorEff') or _rltb.get('pPor') or _rltb.get('price')
                                        _rltb['pPorEff'] = _ep_ltb
                                        _rltb['rankable'] = False
                                        _rltb['pli'] = None
                                        _rltb['rankableLight'] = True
                                        _pe_ltb = min(100.0, (_rltb['protPor'] / _ep_ltb) * 5.0)
                                        _rltb['pliLight'] = round(0.5 * _rltb['score'] + 0.5 * _pe_ltb, 1)
                                        _rsn_ltb = (_rltb.get('meal_check') or {}).get('reason') or f"{int(_rltb['kcalPor'])} kcal/Portion < 400"
                                        _rltb['rank_excluded_reason'] = f"{_rsn_ltb} (Light Meal)"
                                        if f"Mahlzeit-Check: {_rsn_ltb}" not in (_rltb.get('flags') or []):
                                            _rltb['flags'] = (_rltb.get('flags') or []) + [f"Mahlzeit-Check: {_rsn_ltb}"]
                                        changed_uids.add(_rltb['uid'])

                                # sensecheck 63 (P1b, P2b, P2c, P3.2):
                                # 1. P1b: Rescue 29 real ready meals that were misclassified into stage in ('base', 'side', 'veg', 'prot')
                                #    (Gnocchi & Spätzle ready meals #1489/#3054/#3015/#4005/#4025, dishes in sauce #2931/#2335/#2336/#2345/#2346,
                                #    bofrost Chinesische Bratnudeln #2948, sushi boxes #887/#873, Bonduelle Kichererbsentopf #3356,
                                #    NENI Kichererbsen-Tahina-Salat #3317, Ben's Original Street Food Noodle pouches #2327/#2572/#2573,
                                #    canned Ravioli #61/#902/#958/#1586/#1763/#1781/#1823/#2005, and #3467/#3728/#3763).
                                # 2. P2b.1: Demote 33 non-meal items with stage in ('meal', 'stew') (nonfood #321, curry spices/pastes
                                #    #162/#207/#272/#275/#276/#277/#412, soup greens/bones #179/#250/#198/#73/#18, broth/tahina #3178/#3960,
                                #    popcorn #316/#317/#318, Back-Camembert/Brie/Mozzarella #3923/#3623-#3626, milk desserts #3258/#3329/#3365/#3366/#3381/#3395/#3396/#3399-#3401).
                                # 3. P2b.2: Sync all remaining stage == 'prot' rows to meal_class = 'protein_component'.
                                # 4. P2c: Fold single-pack duplicate #2416 into 2-pack #2670 (Spar Dr. Oetker Ristorante Pizza Tonno).
                                # 5. P3.2: Align #530 Billa Clever Lasagne Bolognese (1000 g) meal_class to 'multi_portion'.
                                if os.environ.get('SC63_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC63', '0') != '1':
                                    # --- P1b.1: Gnocchi & Spätzle Ready Meals (#1489, #3054, #3015, #4005, #4025) ---
                                    for _gn_id, _gn_por, _gn_kcal, _gn_prot, _gn_rsn in (
                                        (1489, 450, 662, 19.8, '19.8 g Protein/Portion < 20'),
                                        (3054, 300, 474, 12.6, '12.6 g Protein/Portion < 20'),
                                        (3015, 300, 435, 17.1, '17.1 g Protein/Portion < 20'),
                                        (4005, 450, 468, 15.8, '15.8 g Protein/Portion < 20'),
                                        (4025, 500, 430, 11.0, '11.0 g Protein/Portion < 20'),
                                    ):
                                        _rgn = _pmm_by_id.get(_gn_id)
                                        if _rgn is not None:
                                            _rgn['stage'] = 'meal'
                                            _rgn['gang'] = 'haupt'
                                            _rgn['component'] = False
                                            _rgn['meal_class'] = 'light_meal'
                                            _rgn['meal_check'] = {
                                                'portion': _gn_por, 'kcal': _gn_kcal, 'protein': _gn_prot,
                                                'ok': False, 'cls': 'light_meal', 'reason': _gn_rsn,
                                            }
                                            if _gn_id == 1489:
                                                _ep1489 = _rgn.get('pPorEff') or _rgn.get('pPor') or _rgn.get('price') or 4.99
                                                _rgn['pPorEff'] = _ep1489
                                                _rgn['rankable'] = False
                                                _rgn['pli'] = None
                                                _rgn['rankableLight'] = True
                                                _pe1489 = min(100.0, (_gn_prot / _ep1489) * 5.0)
                                                _rgn['pliLight'] = round(0.5 * _rgn['score'] + 0.5 * _pe1489, 1)
                                                _rgn['rank_excluded_reason'] = f"{_gn_rsn} (Light Meal)"
                                            changed_uids.add(_rgn['uid'])

                                    # --- P1b.2: Dishes in Sauce & Bratnudeln (#2931, #2335, #2336, #2345, #2346, #2948) ---
                                    _r2931 = _pmm_by_id.get(2931)
                                    if _r2931 is not None:
                                        _r2931['stage'] = 'meal'
                                        _r2931['gang'] = 'haupt'
                                        _r2931['component'] = False
                                        _r2931['meal_class'] = 'light_meal'
                                        _r2931['meal_check'] = {
                                            'portion': 300, 'kcal': 279, 'protein': 27.3,
                                            'ok': False, 'cls': 'light_meal', 'reason': '279 kcal/Portion < 400',
                                        }
                                        _r2931['flags'] = [
                                            'Mahlzeit-Check: 279 kcal/Portion < 400' if 'Proteinkomponente' in f else f
                                            for f in (_r2931.get('flags') or [])
                                        ]
                                        changed_uids.add(_r2931['uid'])

                                    for _ym_billa, _ym_gurkerl, _ym_ean, _ym_kcal, _ym_prot, _ym_rsn in (
                                        (2335, 2345, '9008615514241', 393, 33.0, '393 kcal/Portion < 400'),
                                        (2336, 2346, '9008615514234', 360, 33.0, '360 kcal/Portion < 400'),
                                    ):
                                        _rb_ym = _pmm_by_id.get(_ym_billa)
                                        _rg_ym = _pmm_by_id.get(_ym_gurkerl)
                                        if _rb_ym is not None and _rg_ym is not None:
                                            for _k_ym in ('sat', 'salt', 'sugar', 'fat', 'carbs', 'score', 'score_parts', 'day_pct', 'scoreV1'):
                                                if _rb_ym.get(_k_ym) is None and _rg_ym.get(_k_ym) is not None:
                                                    _rb_ym[_k_ym] = _rg_ym[_k_ym]
                                            _rb_ym['ean'] = _rb_ym.get('ean') or _ym_ean
                                            _rb_ym['incomplete'] = False
                                            _rb_ym['alsoAt'] = sorted(list(set((_rb_ym.get('alsoAt') or []) + ['Gurkerl'])))
                                            _rg_ym['alsoAt'] = sorted(list(set((_rg_ym.get('alsoAt') or []) + ['Billa'])))
                                            for _rym in (_rb_ym, _rg_ym):
                                                _rym['stage'] = 'meal'
                                                _rym['gang'] = 'haupt'
                                                _rym['component'] = False
                                                _rym['meal_class'] = 'light_meal'
                                                _rym['meal_check'] = {
                                                    'portion': 330, 'kcal': _ym_kcal, 'protein': _ym_prot,
                                                    'ok': False, 'cls': 'light_meal', 'reason': _ym_rsn,
                                                }
                                                changed_uids.add(_rym['uid'])
                                            _ep_ym = _rb_ym.get('pPorEff') or _rb_ym.get('pPor') or _rb_ym.get('price') or 12.99
                                            _rb_ym['pPorEff'] = _ep_ym
                                            _rb_ym['rankable'] = False
                                            _rb_ym['pli'] = None
                                            _rb_ym['rankableLight'] = True
                                            _pe_ym = min(100.0, (_ym_prot / _ep_ym) * 5.0)
                                            _rb_ym['pliLight'] = round(0.5 * _rb_ym['score'] + 0.5 * _pe_ym, 1)
                                            _rb_ym['rank_excluded_reason'] = f"{_ym_rsn} (Light Meal)"

                                    _r2948 = _pmm_by_id.get(2948)
                                    if _r2948 is not None:
                                        _r2948['stage'] = 'meal'
                                        _r2948['gang'] = 'haupt'
                                        _r2948['component'] = False
                                        _r2948['meal_class'] = 'light_meal'
                                        _r2948['meal_check'] = {
                                            'portion': 333, 'kcal': 360, 'protein': 10.3,
                                            'ok': False, 'cls': 'light_meal', 'reason': '360 kcal/Portion < 400',
                                        }
                                        _ep2948 = _r2948.get('pPorEff') or _r2948.get('pPor') or 3.99
                                        _r2948['pPorEff'] = _ep2948
                                        _r2948['rankable'] = False
                                        _r2948['pli'] = None
                                        _r2948['rankableLight'] = True
                                        _pe2948 = min(100.0, (10.3 / _ep2948) * 5.0)
                                        _r2948['pliLight'] = round(0.5 * _r2948['score'] + 0.5 * _pe2948, 1)
                                        _r2948['rank_excluded_reason'] = '360 kcal/Portion < 400 (Light Meal)'
                                        changed_uids.add(_r2948['uid'])

                                    # --- P1b.3: Sushi Boxes, Stews, Salads, Pouches & Canned Ravioli ---
                                    _r887 = _pmm_by_id.get(887)
                                    if _r887 is not None:
                                        _r887['stage'] = 'meal'
                                        _r887['gang'] = 'haupt'
                                        _r887['component'] = False
                                        _r887['meal_class'] = 'light_meal'
                                        _r887['meal_check'] = {
                                            'portion': 245, 'kcal': 375, 'protein': 15.2,
                                            'ok': False, 'cls': 'light_meal', 'reason': '375 kcal/Portion < 400',
                                        }
                                        _ep887 = _r887.get('pPorEff') or _r887.get('pPor') or _r887.get('price') or 8.99
                                        _r887['pPorEff'] = _ep887
                                        _r887['rankable'] = False
                                        _r887['pli'] = None
                                        _r887['rankableLight'] = True
                                        _pe887 = min(100.0, (15.2 / _ep887) * 5.0)
                                        _r887['pliLight'] = round(0.5 * _r887['score'] + 0.5 * _pe887, 1)
                                        _r887['rank_excluded_reason'] = '375 kcal/Portion < 400 (Light Meal)'
                                        changed_uids.add(_r887['uid'])

                                    _r873 = _pmm_by_id.get(873)
                                    if _r873 is not None:
                                        _r873['stage'] = 'meal'
                                        _r873['gang'] = 'haupt'
                                        _r873['component'] = False
                                        _r873['meal_class'] = 'meal'
                                        _r873['meal_check'] = {
                                            'portion': 330, 'kcal': 502, 'protein': 24.1,
                                            'ok': True, 'cls': 'meal', 'reason': None,
                                        }
                                        _r873['rankable'] = False
                                        _r873['rankableLight'] = False
                                        _r873['rank_excluded_reason'] = 'Gesundheits-Score unter 30 (26.0)'
                                        changed_uids.add(_r873['uid'])

                                    _r3356 = _pmm_by_id.get(3356)
                                    if _r3356 is not None:
                                        _r3356['stage'] = 'stew'
                                        _r3356['gang'] = 'haupt'
                                        _r3356['component'] = False
                                        _r3356['meal_class'] = 'light_meal'
                                        _r3356['meal_check'] = {
                                            'portion': 400, 'kcal': 312, 'protein': 16.8,
                                            'ok': False, 'cls': 'light_meal', 'reason': '312 kcal/Portion < 400',
                                        }
                                        changed_uids.add(_r3356['uid'])

                                    _r3317 = _pmm_by_id.get(3317)
                                    if _r3317 is not None:
                                        _r3317['stage'] = 'meal'
                                        _r3317['gang'] = 'haupt'
                                        _r3317['component'] = False
                                        _r3317['meal_class'] = 'light_meal'
                                        _r3317['meal_check'] = {
                                            'portion': 200, 'kcal': 446, 'protein': 17.0,
                                            'ok': False, 'cls': 'light_meal', 'reason': '17.0 g Protein/Portion < 20',
                                        }
                                        changed_uids.add(_r3317['uid'])

                                    for _bens_id in (2327, 2572, 2573):
                                        _rbens = _pmm_by_id.get(_bens_id)
                                        if _rbens is not None:
                                            _rbens['stage'] = 'meal'
                                            _rbens['gang'] = 'haupt'
                                            _rbens['component'] = False
                                            _rbens['dry'] = False
                                            _rbens['pack'] = 'Beutel/Standbeutel'
                                            _rbens['meal_class'] = 'light_meal'
                                            _k_b = int(round(_rbens.get('kcalPor') or 0))
                                            _p_b = float(_rbens.get('protPor') or 0)
                                            _rsn_b = f"{_k_b} kcal/Portion < 400" if _k_b < 400 else f"{_p_b} g Protein/Portion < 20"
                                            _rbens['meal_check'] = {
                                                'portion': int(_rbens.get('portion') or 250),
                                                'kcal': _k_b, 'protein': _p_b,
                                                'ok': False, 'cls': 'light_meal', 'reason': _rsn_b,
                                            }
                                            _rbens['flags'] = [
                                                f for f in (_rbens.get('flags') or [])
                                                if 'Trockenprodukt' not in f
                                            ]
                                            changed_uids.add(_rbens['uid'])

                                    for _rav_id in (61, 902, 958, 1586, 1763, 1781, 1823, 2005):
                                        _rrav = _pmm_by_id.get(_rav_id)
                                        if _rrav is not None:
                                            _rrav['stage'] = 'meal'
                                            _rrav['gang'] = 'haupt'
                                            _rrav['component'] = False
                                            _rrav['meal_class'] = 'light_meal'
                                            _mc_rav = dict(_rrav.get('meal_check') or {})
                                            _mc_rav['ok'] = False
                                            _mc_rav['cls'] = 'light_meal'
                                            if _rav_id == 958:
                                                _mc_rav['reason'] = '15.2 g Protein/Portion < 20'
                                            elif not _mc_rav.get('reason') or 'Beilage/Komponente' in str(_mc_rav.get('reason')):
                                                _k_r = int(round(_rrav.get('kcalPor') or 0))
                                                _p_r = float(_rrav.get('protPor') or 0)
                                                _mc_rav['reason'] = f"{_k_r} kcal/Portion < 400" if _k_r < 400 else f"{_p_r} g Protein/Portion < 20"
                                            _rrav['meal_check'] = _mc_rav
                                            changed_uids.add(_rrav['uid'])

                                    for _prot_meal_id, _pm_mc in ((3467, 'meal'), (3728, 'light_meal'), (3763, 'light_meal')):
                                        _rpm = _pmm_by_id.get(_prot_meal_id)
                                        if _rpm is not None:
                                            _rpm['stage'] = 'meal'
                                            _rpm['gang'] = 'haupt'
                                            _rpm['component'] = False
                                            _rpm['meal_class'] = _pm_mc
                                            _mc_pm = dict(_rpm.get('meal_check') or {})
                                            _mc_pm['cls'] = _pm_mc
                                            if _mc_pm.get('reason'):
                                                _mc_pm['reason'] = str(_mc_pm['reason']).replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').strip() or None
                                            _rpm['meal_check'] = _mc_pm
                                            _rpm['flags'] = [
                                                f.replace(' Proteinkomponente (keine vollständige Mahlzeit)', '')
                                                for f in (_rpm.get('flags') or [])
                                            ]
                                            changed_uids.add(_rpm['uid'])

                                    # --- P2b.1: Demote Non-Food, Curry Spices, Soup Greens/Bones, Popcorn, Tahina, Back-Camembert & Desserts ---
                                    _r321 = _pmm_by_id.get(321)
                                    if _r321 is not None:
                                        _r321['nonfood'] = True
                                        _r321['stage'] = 'base'
                                        _r321['gang'] = 'zutat'
                                        _r321['component'] = True
                                        _r321['meal_class'] = 'raw_ingredient'
                                        _r321['meal_check'] = {'ok': False, 'cls': 'raw_ingredient', 'reason': 'Kein Lebensmittel (Non-Food)'}
                                        changed_uids.add(_r321['uid'])

                                    for _sp_id in (162, 207, 272, 275, 276, 277, 412):
                                        _rsp = _pmm_by_id.get(_sp_id)
                                        if _rsp is not None:
                                            _rsp['stage'] = 'base'
                                            _rsp['gang'] = 'zutat'
                                            _rsp['component'] = True
                                            _rsp['dry'] = True
                                            _rsp['meal_class'] = 'dry'
                                            _rsp['meal_check'] = {'ok': False, 'cls': 'dry', 'reason': 'Gewürz/Currypaste (kein Fertiggericht)'}
                                            changed_uids.add(_rsp['uid'])

                                    for _sg_id in (179, 250, 198, 73, 18):
                                        _rsg = _pmm_by_id.get(_sg_id)
                                        if _rsg is not None:
                                            _rsg['stage'] = 'base'
                                            _rsg['gang'] = 'zutat'
                                            _rsg['component'] = True
                                            _rsg['meal_class'] = 'raw_ingredient'
                                            _rsg['meal_check'] = {'ok': False, 'cls': 'raw_ingredient', 'reason': 'Rohzutat / Suppengemüse / Suppenfleisch (kein Fertiggericht)'}
                                            changed_uids.add(_rsg['uid'])

                                    for _cb_id in (3178, 3960):
                                        _rcb = _pmm_by_id.get(_cb_id)
                                        if _rcb is not None:
                                            _rcb['stage'] = 'base'
                                            _rcb['gang'] = 'zutat'
                                            _rcb['component'] = True
                                            _rcb['meal_class'] = 'condiment_or_base'
                                            _rcb['meal_check'] = {'ok': False, 'cls': 'condiment_or_base', 'reason': 'Basis/Zutat (kein Fertiggericht)'}
                                            changed_uids.add(_rcb['uid'])

                                    for _pop_id in (316, 317, 318):
                                        _rpop = _pmm_by_id.get(_pop_id)
                                        if _rpop is not None:
                                            _rpop['stage'] = 'side'
                                            _rpop['gang'] = 'snack'
                                            _rpop['component'] = True
                                            _rpop['meal_class'] = 'snack_side'
                                            _rpop['meal_check'] = {'ok': False, 'cls': 'snack_side', 'reason': 'Snack (kein Hauptgericht)'}
                                            changed_uids.add(_rpop['uid'])

                                    for _bc_id in (3923, 3623, 3624, 3625, 3626):
                                        _rbc = _pmm_by_id.get(_bc_id)
                                        if _rbc is not None:
                                            _rbc['stage'] = 'prot'
                                            _rbc['gang'] = 'haupt'
                                            _rbc['component'] = True
                                            _rbc['meal_class'] = 'protein_component'
                                            _rbc['meal_check'] = {'ok': False, 'cls': 'protein_component', 'reason': 'Proteinkomponente/Snack ohne Beilage'}
                                            changed_uids.add(_rbc['uid'])

                                    for _des_id in (3258, 3329, 3399, 3400, 3401, 3365, 3366, 3381, 3395, 3396):
                                        _rdes = _pmm_by_id.get(_des_id)
                                        if _rdes is not None:
                                            _rdes['gang'] = 'dessert'
                                            _rdes['meal_class'] = 'dessert'
                                            _rdes['component'] = False
                                            _rdes['rankable'] = False
                                            _rdes['rankableLight'] = False
                                            _rdes['pli'] = None
                                            _rdes['pliLight'] = None
                                            _mc_des = dict(_rdes.get('meal_check') or {})
                                            _mc_des['ok'] = False
                                            _mc_des['cls'] = 'dessert'
                                            _mc_des['reason'] = 'Dessert/Süßspeise (kein Hauptgericht)'
                                            _rdes['meal_check'] = _mc_des
                                            changed_uids.add(_rdes['uid'])

                                    # --- P2b.2: Sync all remaining stage == 'prot' rows with meal_class = 'protein_component' ---
                                    for _r_prot in rows:
                                        if _r_prot.get('stage') == 'prot':
                                            _mod_prot = False
                                            if not _r_prot.get('component'):
                                                _r_prot['component'] = True
                                                _mod_prot = True
                                            if _r_prot.get('meal_class') not in ('raw_ingredient', 'dry', 'baby', 'dessert', 'protein_component'):
                                                _r_prot['meal_class'] = 'protein_component'
                                                _mod_prot = True
                                            _mc_p = dict(_r_prot.get('meal_check') or {})
                                            _tgt_p_cls = _r_prot.get('meal_class')
                                            _tgt_p_rsn = _mc_p.get('reason') or 'Proteinkomponente (keine vollständige Mahlzeit)'
                                            if _mc_p.get('ok') is not False or _mc_p.get('cls') != _tgt_p_cls or _mc_p.get('reason') != _tgt_p_rsn:
                                                _mc_p['ok'] = False
                                                _mc_p['cls'] = _tgt_p_cls
                                                _mc_p['reason'] = _tgt_p_rsn
                                                _r_prot['meal_check'] = _mc_p
                                                _mod_prot = True
                                            if _r_prot.get('rankable') or _r_prot.get('rankableLight') or _r_prot.get('pli') is not None or _r_prot.get('pliLight') is not None:
                                                _r_prot['rankable'] = False
                                                _r_prot['rankableLight'] = False
                                                _r_prot['pli'] = None
                                                _r_prot['pliLight'] = None
                                                _mod_prot = True
                                            if _mod_prot:
                                                changed_uids.add(_r_prot['uid'])

                                    # --- P2c: Multi-Pack vs Single-Pack Duplicate (#2670 vs #2416 Spar Dr. Oetker Ristorante Pizza Tonno) ---
                                    _r2670 = _pmm_by_id.get(2670)
                                    _r2416 = _pmm_by_id.get(2416)
                                    if _r2670 is not None and _r2416 is not None:
                                        _r2670['variant_note'] = 'auch als Einzelpackung (355 g)'
                                        _r2670['variantIds'] = [2416]
                                        _r2416['rankable'] = False
                                        _r2416['pli'] = None
                                        _r2416['badge'] = None
                                        _r2416['rank_excluded_reason'] = 'Duplikat (nahe Name/Marke, Ranking)'
                                        if 'Duplikat (nahe Name/Marke, Ranking)' not in (_r2416.get('flags') or []):
                                            _r2416['flags'] = (_r2416.get('flags') or []) + ['Duplikat (nahe Name/Marke, Ranking)']
                                        changed_uids.add(_r2670['uid'])
                                        changed_uids.add(_r2416['uid'])

                                    # --- P3.2: #530 Billa Clever Lasagne Bolognese (1000 g) -> meal_class = 'multi_portion' ---
                                    _r530 = _pmm_by_id.get(530)
                                    if _r530 is not None:
                                        _r530['meal_class'] = 'multi_portion'
                                        _mc530 = dict(_r530.get('meal_check') or {})
                                        _mc530['ok'] = False
                                        _mc530['cls'] = 'multi_portion'
                                        _r530['meal_check'] = _mc530
                                        changed_uids.add(_r530['uid'])

                                    # sensecheck 64 (SC63 P1.2, P2.2, P2.3 & SC62 P3.2):
                                    # 1. SC63 P1.2:
                                    #    - Exclude incomplete rows (#1447, #1454) from rankable / rankableLight (pliLight = None),
                                    #      and align #1447 (gang='dessert') meal_class to 'dessert'.
                                    #    - Demote fingerfood/snack items #564 (BILLA Mini Samosas mit Gemüse) and #650 (BILLA Bio Quinoa Ecken)
                                    #      to stage='side', gang='snack', component=True, meal_class='snack_side'.
                                    #    - Rescue the 14 dead-zone light_meal ready meals (400 <= kcalPor <= 684, 15.8 <= protPor < 20 g,
                                    #      score >= 30.3, pstat == 'live 2026') into rankableLight = True with computed pliLight:
                                    #      Billa (#5, #587, #863, #864, #1336, #1497, #2198, #3385), bofrost (#2933, #2935, #2943),
                                    #      Kernbeißer (#3140, #3144), and myProduct (#3207).
                                    # 2. SC63 P2.2:
                                    #    - Deduplicate variantIds across all rows (#2809 [2838, 2838, 2838] -> [2838], #2850 [2855, 2855, 2855] -> [2855]).
                                    #    - Link and demote the 7 same-store pack-size duplicate pairs (#432/#431, #1114/#1113, #2809/#2838,
                                    #      #2850/#2855, #1162/#96, #495/#2256, #1033/#959) so each product occupies at most one ranking slot per store.
                                    # 3. SC63 P2.3:
                                    #    - Mark bofrost & Alfies non-complete meal components (#2940, #2941, #2643, #2647, #2958, #3201,
                                    #      #2642, #3200, #3203, #3956, #3964, #4008, #4009) with component=True and proper stage/meal_class.
                                    # 4. SC62 P3.2:
                                    #    - Give #172 Spar S-BUDGET Lasagne Bolognese (1000 g) the same 250 g label_portion / multi_portion fields
                                    #      as #530 Billa Clever Lasagne Bolognese (1000 g), and set 400 g (2 Portionen) on remaining 800 g cans
                                    #      in Linz (#936, #1002, #1014, #396, #1034, #1469).
                                    if os.environ.get('SC64_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC64', '0') != '1':
                                        # --- 1a. Incomplete Guard on rankable / rankableLight (#1447, #1454) ---
                                        for _r_inc in rows:
                                            if _r_inc.get('incomplete') and (_r_inc.get('rankable') or _r_inc.get('rankableLight') or _r_inc.get('pli') is not None or _r_inc.get('pliLight') is not None):
                                                _r_inc['rankable'] = False
                                                _r_inc['rankableLight'] = False
                                                _r_inc['pli'] = None
                                                _r_inc['pliLight'] = None
                                                if _r_inc.get('id') == 1447:
                                                    _r_inc['meal_class'] = 'dessert'
                                                    _r_inc['meal_check'] = {
                                                        'portion': 300, 'kcal': 384, 'protein': 29.4,
                                                        'ok': False, 'cls': 'dessert', 'reason': 'Dessert/Süßspeise (kein Hauptgericht)',
                                                    }
                                                _r_inc['rank_excluded_reason'] = 'Gesundheits-Score unvollständig (ges. Fettsäuren, Salz fehlen)'
                                                changed_uids.add(_r_inc['uid'])

                                        # --- 1b. Demote Fingerfood/Snacks (#564 BILLA Mini Samosas, #650 BILLA Bio Quinoa Ecken) ---
                                        for _snk_id in (564, 650):
                                            _rsnk = _pmm_by_id.get(_snk_id)
                                            if _rsnk is not None:
                                                _rsnk['stage'] = 'side'
                                                _rsnk['gang'] = 'snack'
                                                _rsnk['component'] = True
                                                _rsnk['meal_class'] = 'snack_side'
                                                _por_snk = int(_rsnk.get('portion') or _rsnk.get('size') or 200)
                                                _kcal_snk = int(round(_rsnk.get('kcalPor') or 0))
                                                _prot_snk = float(_rsnk.get('protPor') or 0.0)
                                                _rsnk['meal_check'] = {
                                                    'portion': _por_snk, 'kcal': _kcal_snk, 'protein': _prot_snk,
                                                    'ok': False, 'cls': 'snack_side', 'reason': 'Snack/Fingerfood (keine vollständige Mahlzeit)',
                                                }
                                                _rsnk['flags'] = ['Mahlzeit-Check: Snack/Fingerfood (keine vollständige Mahlzeit)']
                                                _rsnk['rankable'] = False
                                                _rsnk['rankableLight'] = False
                                                _rsnk['pli'] = None
                                                _rsnk['pliLight'] = None
                                                changed_uids.add(_rsnk['uid'])

                                        # --- 1c. Rescue 14 Dead-Zone light_meal Ready Meals (400-684 kcal, 15.8-19.6 g P, score >= 30.3) ---
                                        for _dz_id in (5, 587, 863, 864, 1336, 1497, 2198, 3385, 2933, 2935, 2943, 3140, 3144, 3207):
                                            _rdz = _pmm_by_id.get(_dz_id)
                                            if _rdz is not None and _rdz.get('score') is not None and _rdz.get('protPor') and _rdz.get('price'):
                                                _sz_dz = _rdz.get('size') or _rdz.get('portion')
                                                _por_dz = _rdz.get('portion_g') or _rdz.get('portion') or _sz_dz
                                                if _rdz.get('pPor') is None:
                                                    _rdz['pPor'] = round(_rdz['price'] * (_por_dz / _sz_dz), 2) if (_sz_dz and _por_dz and _por_dz < _sz_dz) else _rdz['price']
                                                _ep_dz = _rdz.get('pPorEff') or round(_rdz['pPor'] + (_rdz.get('shipPor') or 0.0), 2)
                                                _rdz['pPorEff'] = _ep_dz
                                                _rdz['rankable'] = False
                                                _rdz['pli'] = None
                                                _rdz['rankableLight'] = True
                                                _pe_dz = min(100.0, (_rdz['protPor'] / _ep_dz) * 5.0)
                                                _rdz['pliLight'] = round(0.5 * _rdz['score'] + 0.5 * _pe_dz, 1)
                                                _rsn_dz = (_rdz.get('meal_check') or {}).get('reason') or f"{_rdz['protPor']} g Protein/Portion < 20"
                                                _rdz['rank_excluded_reason'] = f"{_rsn_dz} (Light Meal)"
                                                if f"Mahlzeit-Check: {_rsn_dz}" not in (_rdz.get('flags') or []):
                                                    _rdz['flags'] = [f for f in (_rdz.get('flags') or []) if not f.startswith('Mahlzeit-Check:')] + [f"Mahlzeit-Check: {_rsn_dz}"]
                                                changed_uids.add(_rdz['uid'])

                                        # --- 2. SC63 P2.2: Deduplicate variantIds & Link/Demote 7 Same-Store Pack-Size Duplicate Pairs ---
                                        for _r_vid in rows:
                                            if _r_vid.get('variantIds'):
                                                _ded_vids = list(dict.fromkeys(_r_vid['variantIds']))
                                                if _ded_vids != _r_vid['variantIds']:
                                                    _r_vid['variantIds'] = _ded_vids
                                                    changed_uids.add(_r_vid['uid'])

                                        for _win_id, _los_id, _vnote in (
                                            (432,  431,  'auch als Einzelportion (400 g)'),
                                            (1114, 1113, 'auch als Einzelportion (350 g)'),
                                            (2809, 2838, 'auch als Einzelportion (500 g)'),
                                            (2850, 2855, 'auch als Einzelportion (500 g)'),
                                            (1162, 96,   'auch als Einzelportion (400 g)'),
                                            (495,  2256, 'auch als Einzelportion (400 g)'),
                                            (1033, 959,  'auch als Einzelportion (400 g)'),
                                        ):
                                            _rwin = _pmm_by_id.get(_win_id)
                                            _rlos = _pmm_by_id.get(_los_id)
                                            if _rwin is not None and _rlos is not None:
                                                _rwin['variant_note'] = _vnote
                                                _rwin['variantIds'] = list(dict.fromkeys((_rwin.get('variantIds') or []) + [_los_id]))
                                                _rlos['rankable'] = False
                                                _rlos['rankableLight'] = False
                                                _rlos['pli'] = None
                                                _rlos['pliLight'] = None
                                                _rlos['badge'] = None
                                                _rlos['rank_excluded_reason'] = 'Duplikat (nahe Name/Marke, Ranking)'
                                                if 'Duplikat (nahe Name/Marke, Ranking)' not in (_rlos.get('flags') or []):
                                                    _rlos['flags'] = (_rlos.get('flags') or []) + ['Duplikat (nahe Name/Marke, Ranking)']
                                                changed_uids.add(_rwin['uid'])
                                                changed_uids.add(_rlos['uid'])

                                        # --- 3. SC63 P2.3: Pipeline bofrost & Alfies Non-Complete Meal Components ---
                                        for _p23_id, _p23_stg, _p23_gang, _p23_mc, _p23_rsn in (
                                            (2940, 'prot', 'haupt',   'protein_component', 'Proteinkomponente ohne Beilage (keine vollständige Mahlzeit)'),
                                            (2941, 'prot', 'haupt',   'protein_component', 'Proteinkomponente ohne Beilage (keine vollständige Mahlzeit)'),
                                            (2643, 'prot', 'haupt',   'protein_component', 'Proteinkomponente ohne Beilage (keine vollständige Mahlzeit)'),
                                            (2647, 'prot', 'haupt',   'protein_component', 'Proteinkomponente ohne Beilage (keine vollständige Mahlzeit)'),
                                            (3964, 'prot', 'vorspeise', 'protein_component', 'Proteinkomponente/Aufschnitt ohne Beilage (keine vollständige Mahlzeit)'),
                                            (2958, 'side', 'haupt',   'snack_side',        'Beilage/Komponente (keine vollständige Mahlzeit)'),
                                            (3201, 'veg',  'haupt',   'snack_side',        'Beilage/Komponente (keine vollständige Mahlzeit)'),
                                            (2642, 'side', 'snack',   'snack_side',        'Snack/Fingerfood (keine vollständige Mahlzeit)'),
                                            (3200, 'side', 'snack',   'snack_side',        'Snack/Fingerfood (keine vollständige Mahlzeit)'),
                                            (3203, 'side', 'snack',   'snack_side',        'Snack/Fingerfood (keine vollständige Mahlzeit)'),
                                            (4008, 'side', 'snack',   'snack_side',        'Beilage/Snack (keine vollständige Mahlzeit)'),
                                            (4009, 'side', 'snack',   'snack_side',        'Beilage/Snack (keine vollständige Mahlzeit)'),
                                            (3956, 'side', 'dessert', 'dessert',           'Dessert/Süßspeise (kein Hauptgericht)'),
                                        ):
                                            _rp23 = _pmm_by_id.get(_p23_id)
                                            if _rp23 is not None:
                                                _rp23['stage'] = _p23_stg
                                                _rp23['gang'] = _p23_gang
                                                _rp23['component'] = True
                                                _rp23['meal_class'] = _p23_mc
                                                _mc23 = dict(_rp23.get('meal_check') or {})
                                                _mc23['ok'] = False
                                                _mc23['cls'] = _p23_mc
                                                _mc23['reason'] = _p23_rsn
                                                _rp23['meal_check'] = _mc23
                                                _rp23['flags'] = [f for f in (_rp23.get('flags') or []) if not f.startswith('Mahlzeit-Check:')] + [f"Mahlzeit-Check: {_p23_rsn}"]
                                                _rp23['rankable'] = False
                                                _rp23['rankableLight'] = False
                                                _rp23['pli'] = None
                                                _rp23['pliLight'] = None
                                                changed_uids.add(_rp23['uid'])

                                        # --- 4. SC62 P3.2: #172 Spar S-BUDGET Lasagne Bolognese (1000 g) & Remaining 800 g 2-Portionen Cans ---
                                        _r172 = _pmm_by_id.get(172)
                                        if _r172 is not None:
                                            _r172['portion'] = 250
                                            _r172['portion_g'] = 250
                                            _r172['portion_source'] = 'label_portion'
                                            _r172['kcalPor'] = 347.5
                                            _r172['kcal_meal'] = 348
                                            _r172['protPor'] = 14.5
                                            _r172['saltPor'] = 2.42
                                            _r172['saltPct'] = 40
                                            _pr172 = _r172.get('price') or 3.99
                                            _r172['pPor'] = round(_pr172 / 4.0, 2)
                                            _r172['pPorEff'] = _r172['pPor']
                                            _r172['meal_class'] = 'multi_portion'
                                            _r172['meal_check'] = {
                                                'portion': 250, 'kcal': 348, 'protein': 14.5,
                                                'ok': False, 'cls': 'multi_portion', 'reason': '348 kcal/Portion < 400',
                                            }
                                            _r172['flags'] = ['Mahlzeit-Check: 348 kcal/Portion < 400']
                                            _r172['day_pct'] = {'kcal': 17, 'protein': 29, 'salt': 40, 'satfat': 35, 'sugar': 7, 'fiber': 12}
                                            _sp172 = dict(_r172.get('score_parts') or {})
                                            _sp172['portion_salt'] = -0.0
                                            _r172['score_parts'] = _sp172
                                            _r172['rankable'] = False
                                            _r172['rankableLight'] = False
                                            _r172['pli'] = None
                                            _r172['pliLight'] = None
                                            changed_uids.add(_r172['uid'])

                                        for _c8_id, _c8_mc, _c8_rsn in (
                                            (936,  'light_meal', '376 kcal/Portion < 400'),
                                            (1002, 'light_meal', '324 kcal/Portion < 400'),
                                            (1014, 'light_meal', '320 kcal/Portion < 400'),
                                            (396,  'light_meal', '12.4 g Protein/Portion < 20'),
                                            (1034, 'meal',       None),
                                            (1469, 'light_meal', '304 kcal/Portion < 400'),
                                        ):
                                            _rc8 = _pmm_by_id.get(_c8_id)
                                            if _rc8 is not None:
                                                _rc8['portion'] = 400
                                                _rc8['portion_g'] = 400
                                                _rc8['portion_source'] = 'pack_2portions'
                                                _rc8['kcalPor'] = round((_rc8.get('kcal') or 0.0) * 4.0, 1)
                                                _rc8['kcal_meal'] = int(round(_rc8['kcalPor']))
                                                _rc8['protPor'] = round((_rc8.get('p100') or 0.0) * 4.0, 1)
                                                if _rc8.get('salt') is not None:
                                                    _rc8['saltPor'] = round(_rc8['salt'] * 4.0, 2)
                                                    _rc8['saltPct'] = round(_rc8['saltPor'] / 6.0 * 100)
                                                if _rc8.get('price'):
                                                    _rc8['pPor'] = round(_rc8['price'] / 2.0, 2)
                                                    _rc8['pPorEff'] = _rc8['pPor']
                                                _xc8 = {
                                                    'name': (_rc8.get('name') or '') + ' 2 Portionen',
                                                    'size_g': 800.0, 'packaging': _rc8.get('pack'),
                                                    'kcal_100': _rc8.get('kcal'), 'protein_100': _rc8.get('p100'),
                                                    'fat_100': _rc8.get('fat'), 'satfat_100': _rc8.get('sat'),
                                                    'carbs_100': _rc8.get('carbs'), 'sugar_100': _rc8.get('sugar'),
                                                    'fiber_100': _rc8.get('fib'), 'salt_100': _rc8.get('salt'),
                                                    'ingredients': _rc8.get('ing'), 'store': _rc8.get('store'),
                                                }
                                                _vc8 = V2.score_v2(_xc8)
                                                _rc8['score'] = _vc8.get('health_score')
                                                _rc8['score_parts'] = _vc8.get('score_parts')
                                                _rc8['day_pct'] = _vc8.get('day_pct')
                                                _rc8['meal_class'] = _c8_mc
                                                _rc8['meal_check'] = {
                                                    'portion': 400,
                                                    'kcal': _rc8['kcal_meal'],
                                                    'protein': _rc8['protPor'],
                                                    'ok': _c8_mc == 'meal',
                                                    'cls': _c8_mc,
                                                    'reason': _c8_rsn,
                                                }
                                                _rc8['flags'] = [f"Mahlzeit-Check: {_c8_rsn}"] if _c8_rsn else []
                                                _rc8['rankable'] = False
                                                _rc8['rankableLight'] = False
                                                _rc8['pli'] = None
                                                _rc8['pliLight'] = None
                                                if _c8_id == 1034 and _rc8.get('score') is not None and _rc8['score'] < 30:
                                                    _rc8['rank_excluded_reason'] = f"Gesundheits-Score unter 30 ({_rc8['score']})"
                                                changed_uids.add(_rc8['uid'])

                                        # SC66 (from Sensecheck 65 P1.1 + P1.2 + P3.1):
                                        # - P1.1: Rescue second light_meal dead-zone (250 <= kcalPor < 300, protPor >= 15 g)
                                        #         + 5 Linz/Online hearty soups (308-440 kcal, >= 15 g P) -> +32 rankableLight ready meals.
                                        # - P1.2: 100% sync rankableLight === passesLightRank (demote 5 legacy < 11 g P rows #51, #52, #860, #1091, #2948)
                                        #         and rescue 2 false-positive _NOISE duplicate rows (#2820 PrepMyMeal Veggie Bolognese, #877 BILLA Lasagne Rind)
                                        #         plus clean stale self-twin Duplikat flag on keepers #212, #222, #1087.
                                        # - P3.1: Populate rank_excluded_reason on HelloFresh meal-kit rows and unranked light_meal rows (< 15 g P / Score < 30).
                                        if os.environ.get('SC66_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC66', '0') != '1':
                                            # P1.1: Promote all eligible light_meal ready meals & stews (250 <= kcalPor < 685, protPor >= 15, score >= 30, live 2026, delivers_4020)
                                            for _r66a in rows:
                                                if (
                                                    _r66a.get('meal_class') == 'light_meal'
                                                    and not _r66a.get('rankableLight')
                                                    and 250 <= (_r66a.get('kcalPor') or 0) < 685
                                                    and (_r66a.get('protPor') or 0) >= 15
                                                    and (_r66a.get('score') or 0) >= 30
                                                    and bool(_r66a.get('price'))
                                                    and not _r66a.get('price_stale')
                                                    and _r66a.get('stage') in ('meal', 'stew')
                                                    and _r66a.get('segment') == 'ready_meal'
                                                    and _r66a.get('pstat') == 'live 2026'
                                                    and _r66a.get('delivers_4020') is True
                                                    and not _r66a.get('component')
                                                    and not _r66a.get('incomplete')
                                                    and not _r66a.get('sold_out')
                                                    and _r66a.get('dupOf') is None
                                                    and not any('Duplikat' in f for f in (_r66a.get('flags') or []))
                                                    and _r66a.get('store') != 'HelloFresh'
                                                ):
                                                    if _r66a.get('stage') == 'stew' and _r66a.get('gang') == 'vorspeise':
                                                        _r66a['gang'] = 'haupt'
                                                    _r66a['rankable'] = False
                                                    _r66a['pli'] = None
                                                    _r66a['rankableLight'] = True
                                                    _eff66a = _r66a.get('pPorEff') or (
                                                        round((_r66a.get('pPor') or 0) + (_r66a.get('shipPor') or 0), 2)
                                                        if _r66a.get('pPor') else None
                                                    )
                                                    if _eff66a:
                                                        _r66a['pPorEff'] = _eff66a
                                                        _pe66a = min(100.0, (_r66a['protPor'] / _eff66a) * 5.0)
                                                        _r66a['pliLight'] = round(0.5 * _r66a['score'] + 0.5 * _pe66a, 1)
                                                    _r66a['rank_excluded_reason'] = None
                                                    changed_uids.add(_r66a['uid'])

                                            # P1.2(a): Demote 5 legacy < 11 g P rows (#51, #52, #860, #1091, #2948) so rankableLight === passesLightRank (148 === 148)
                                            for _r66b in rows:
                                                if _r66b.get('rankableLight') and (_r66b.get('protPor') or 0) < 11:
                                                    _r66b['rankableLight'] = False
                                                    _r66b['pliLight'] = None
                                                    _r66b['rank_excluded_reason'] = '< 11 g Protein/Portion'
                                                    changed_uids.add(_r66b['uid'])

                                            # P1.2(b): Clean stale self-twin Duplikat flag on keepers #212, #222, #1087 and rescue #2820 & #877 into rankable=True
                                            for _clean_id in (212, 222, 1087, 2820, 877):
                                                _rc = _pmm_by_id.get(_clean_id)
                                                if _rc is not None:
                                                    _rc['flags'] = [f for f in (_rc.get('flags') or []) if f != 'Duplikat (nahe Name/Marke, Ranking)']
                                                    changed_uids.add(_rc['uid'])

                                            for _rescue_id in (2820, 877):
                                                _rr = _pmm_by_id.get(_rescue_id)
                                                if _rr is not None and _sc50_rank_guard(_rr):
                                                    _eff66r = _rr.get('pPorEff') or (
                                                        round((_rr.get('pPor') or 0) + (_rr.get('shipPor') or 0), 2)
                                                        if _rr.get('pPor') else None
                                                    )
                                                    if _eff66r:
                                                        _rr['pPorEff'] = _eff66r
                                                        _pe66r = min(100.0, (_rr['protPor'] / _eff66r) * 5.0)
                                                        _rr['pli'] = round(0.5 * _rr['score'] + 0.5 * _pe66r, 1)
                                                    _rr['rankable'] = True
                                                    _rr['rankableLight'] = False
                                                    _rr['pliLight'] = None
                                                    _rr['rank_excluded_reason'] = None
                                                    changed_uids.add(_rr['uid'])

                                            # P3.1: Populate rank_excluded_reason on HelloFresh meal kits and unranked light_meal rows (< 15 g P / Score < 30)
                                            for _r66c in rows:
                                                if _r66c.get('store') == 'HelloFresh' and not _r66c.get('rank_excluded_reason'):
                                                    _r66c['rank_excluded_reason'] = 'Kochbox zum Selbstkochen (30–45 Min.) – nicht im Fertiggericht-Ranking'
                                                    changed_uids.add(_r66c['uid'])
                                                elif (
                                                    _r66c.get('meal_class') == 'light_meal'
                                                    and not _r66c.get('rankable')
                                                    and not _r66c.get('rankableLight')
                                                    and not _r66c.get('rank_excluded_reason')
                                                    and _r66c.get('dupOf') is None
                                                ):
                                                    if _r66c.get('score') is not None and _r66c['score'] < 30:
                                                        _r66c['rank_excluded_reason'] = 'Health-Score < 30'
                                                        changed_uids.add(_r66c['uid'])
                                                    elif _r66c.get('protPor') is not None and _r66c['protPor'] < 15:
                                                        _r66c['rank_excluded_reason'] = '< 15 g Protein/Portion'
                                                        changed_uids.add(_r66c['uid'])

                                            # SC67 (from Sensecheck 66/67 P1.1 + P2.1 + P2.2 + P3.1):
                                            # - P1.1: Rescue 3 real meals in Linz (#1277 dmBio Chili con Tofu High Protein -> rankableLight=True, pliLight=53.5;
                                            #         #1031 Billa Felix Linsen mit Speck 800 g -> rankable=True, pli=37.4;
                                            #         #496 Spar Inzersdorfer Paprikahendl 400 g -> rankableLight=True, pliLight=31.7)
                                            #         and clean false Tofu Proteinkomponente flag on #568 and #3168.
                                            # - P2.1: Reclassify 36 screw-jar meals (dmBio, Nabio, Alnatura, Tressbrüder, etc.) from pack='Dose/Konserve' to pack='Glas'
                                            #         and #1266 dmBio Nudel-Tasse 68 g to pack='Trocken/Instant'.
                                            # - P2.2: Normalize multi-portion packs to 2 portions: #1020 Billa Felix Gefüllte Paprika 800 g (portion=400 g, light_meal)
                                            #         and 4 bofrost multi-portion bags (#3020 Fischsuppe Cacciucco 750 g -> 375 g light_meal, #2956 Broccoli-Nudelauflauf 800 g -> 400 g light_meal,
                                            #         #2980 Kärntner Kasnudeln 770 g -> 385 g meal, #3071 Krautrouladen 1000 g -> 500 g meal).
                                            # - P3.1: Generic rank_excluded_reason fallback from flags (and score/class for remaining unranked live 2026 rows).
                                            if os.environ.get('SC67_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC67', '0') != '1':
                                                # P1.1(a): Clean false Tofu Proteinkomponente flag on #1277, #568, #3168 and promote #1277 to rankableLight=True (pliLight=53.5)
                                                for _tf_id in (1277, 568, 3168):
                                                    _rtf = _pmm_by_id.get(_tf_id)
                                                    if _rtf is not None:
                                                        _rtf['component'] = False
                                                        if _rtf.get('pPorEff') is None and _rtf.get('pPor') is not None:
                                                            _rtf['pPorEff'] = round(_rtf['pPor'] + (_rtf.get('shipPor') or 0.0), 2)
                                                        if isinstance(_rtf.get('meal_check'), dict) and _rtf['meal_check'].get('reason'):
                                                            _rtf['meal_check'] = dict(_rtf['meal_check'])
                                                            _rtf['meal_check']['reason'] = _rtf['meal_check']['reason'].replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').strip()
                                                        _rtf['flags'] = [
                                                            f.replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').strip()
                                                            for f in (_rtf.get('flags') or [])
                                                            if f != 'Mahlzeit-Check: Proteinkomponente (keine vollständige Mahlzeit)'
                                                        ]
                                                        changed_uids.add(_rtf['uid'])

                                                _r1277 = _pmm_by_id.get(1277)
                                                if _r1277 is not None:
                                                    _r1277['stage'] = 'meal'
                                                    _r1277['segment'] = 'ready_meal'
                                                    _r1277['meal_class'] = 'light_meal'
                                                    _r1277['gang'] = 'haupt'
                                                    _r1277['component'] = False
                                                    _r1277['pPorEff'] = 2.75
                                                    _r1277['rankable'] = False
                                                    _r1277['pli'] = None
                                                    _r1277['rankableLight'] = True
                                                    _r1277['pliLight'] = 53.5
                                                    _r1277['rank_excluded_reason'] = None
                                                    changed_uids.add(_r1277['uid'])

                                                # P1.1(b): Rescue #1031 [Billa] Felix Linsen mit Speck 800 g from false _NOISE collision
                                                _r1031 = _pmm_by_id.get(1031)
                                                if _r1031 is not None:
                                                    _r1031['flags'] = [f for f in (_r1031.get('flags') or []) if f != 'Duplikat (nahe Name/Marke, Ranking)']
                                                    _r1031['pPorEff'] = 3.25
                                                    _r1031['rankable'] = True
                                                    _r1031['rankableLight'] = False
                                                    _r1031['pliLight'] = None
                                                    _r1031['pli'] = 37.4
                                                    _r1031['rank_excluded_reason'] = None
                                                    changed_uids.add(_r1031['uid'])

                                                # P1.1(c): Rescue #496 [Spar] Inzersdorfer Paprikahendl 400 g to light_meal / rankableLight=True (pliLight=31.7)
                                                _r496 = _pmm_by_id.get(496)
                                                if _r496 is not None:
                                                    _r496['stage'] = 'meal'
                                                    _r496['segment'] = 'ready_meal'
                                                    _r496['meal_class'] = 'light_meal'
                                                    _r496['gang'] = 'haupt'
                                                    _r496['component'] = False
                                                    _r496['pPorEff'] = 5.29
                                                    _r496['meal_check'] = {
                                                        'portion': 400,
                                                        'kcal': 372,
                                                        'protein': 30.0,
                                                        'ok': False,
                                                        'cls': 'light_meal',
                                                        'reason': '372 kcal/Portion < 400',
                                                    }
                                                    _r496['flags'] = ['Mahlzeit-Check: 372 kcal/Portion < 400']
                                                    _r496['rankable'] = False
                                                    _r496['pli'] = None
                                                    _r496['rankableLight'] = True
                                                    _r496['pliLight'] = 31.7
                                                    _r496['rank_excluded_reason'] = None
                                                    changed_uids.add(_r496['uid'])

                                                # P2.1: Reclassify 36 screw-jar meals (plus hidden twin #3448) from pack='Dose/Konserve' to pack='Glas'
                                                # and #1266 [dm] dmBio Fertiggericht Nudel-Tasse Tomatensauce 68 g to pack='Trocken/Instant'
                                                _r1266 = _pmm_by_id.get(1266)
                                                if _r1266 is not None:
                                                    _r1266['pack'] = 'Trocken/Instant'
                                                    changed_uids.add(_r1266['uid'])
                                                _jar_re = re.compile(r'im glas|glas|dmbio|nabio|alnatura|tressbr[üu]der', re.I)
                                                for _r67p in rows:
                                                    if (
                                                        _r67p['id'] != 1266
                                                        and _r67p.get('pack') == 'Dose/Konserve'
                                                        and (_r67p.get('store') == 'dm' or _jar_re.search((_r67p.get('name') or '') + ' ' + (_r67p.get('brand') or '')))
                                                    ):
                                                        _r67p['pack'] = 'Glas'
                                                        changed_uids.add(_r67p['uid'])

                                                # P2.2: Normalize multi-portion packs (#1020 Billa Felix Gefüllte Paprika 800 g + 4 bofrost multi-portion bags) to 2 portions
                                                _r1020 = _pmm_by_id.get(1020)
                                                if _r1020 is not None:
                                                    _r1020['portion'] = 400
                                                    _r1020['portion_g'] = 400
                                                    _r1020['portion_source'] = 'pack_2portions'
                                                    _r1020['kcalPor'] = 352.0
                                                    _r1020['kcal_meal'] = 352
                                                    _r1020['protPor'] = 10.4
                                                    _r1020['saltPor'] = 4.0
                                                    _r1020['saltPct'] = 67
                                                    _r1020['pPor'] = 3.25
                                                    _r1020['pPorEff'] = 3.25
                                                    _r1020['ppe'] = 3.2
                                                    _r1020['meal_class'] = 'light_meal'
                                                    _r1020['meal_check'] = {
                                                        'portion': 400,
                                                        'kcal': 352,
                                                        'protein': 10.4,
                                                        'ok': False,
                                                        'cls': 'light_meal',
                                                        'reason': '352 kcal/Portion < 400',
                                                    }
                                                    _r1020['flags'] = ['Mahlzeit-Check: 352 kcal/Portion < 400']
                                                    _r1020['rankable'] = False
                                                    _r1020['rankableLight'] = False
                                                    _r1020['pli'] = None
                                                    _r1020['pliLight'] = None
                                                    _r1020['rank_excluded_reason'] = '< 15 g Protein/Portion'
                                                    changed_uids.add(_r1020['uid'])

                                                for _bf_id, _bf_por, _bf_kpor, _bf_kmeal, _bf_ppor, _bf_spor, _bf_spct, _bf_prpor, _bf_ppe, _bf_mcls, _bf_ok, _bf_rsn, _bf_rk, _bf_rkl, _bf_pli, _bf_plil in (
                                                    (3020, 375, 270.0, 270, 34.9, 1.73, 29, 9.24, 3.8, 'light_meal', False, '270 kcal/Portion < 400', False, True, None, 41.3),
                                                    (2956, 400, 496.0, 496, 19.6, 3.12, 52, 6.25, 3.1, 'light_meal', False, '19.6 g Protein/Portion < 20', False, True, None, 27.3),
                                                    (2980, 385, 604.5, 605, 28.9, 5.78, 96, 7.89, 3.7, 'meal', True, None, True, False, 26.9, None),
                                                    (3071, 500, 470.0, 470, 30.5, 5.0, 83, 11.89, 2.6, 'meal', True, None, True, False, 28.4, None),
                                                ):
                                                    _rbf = _pmm_by_id.get(_bf_id)
                                                    if _rbf is not None:
                                                        _rbf['portion'] = _bf_por
                                                        _rbf['portion_g'] = _bf_por
                                                        _rbf['portion_source'] = 'pack_2portions'
                                                        _rbf['kcalPor'] = _bf_kpor
                                                        _rbf['kcal_meal'] = _bf_kmeal
                                                        _rbf['protPor'] = _bf_ppor
                                                        _rbf['saltPor'] = _bf_spor
                                                        _rbf['saltPct'] = _bf_spct
                                                        _rbf['pPor'] = _bf_prpor
                                                        _rbf['pPorEff'] = _bf_prpor
                                                        _rbf['ppe'] = _bf_ppe
                                                        _rbf['meal_class'] = _bf_mcls
                                                        _rbf['gang'] = 'haupt'
                                                        _rbf['meal_check'] = {
                                                            'portion': _bf_por,
                                                            'kcal': _bf_kmeal,
                                                            'protein': _bf_ppor,
                                                            'ok': _bf_ok,
                                                            'cls': _bf_mcls,
                                                            'reason': _bf_rsn,
                                                        }
                                                        if _bf_rsn:
                                                            _rbf['flags'] = [f'Mahlzeit-Check: {_bf_rsn}']
                                                        else:
                                                            _rbf['flags'] = [f for f in (_rbf.get('flags') or []) if 'Mehrportionen-Packung' not in f]
                                                        _rbf['rankable'] = _bf_rk
                                                        _rbf['rankableLight'] = _bf_rkl
                                                        _rbf['pli'] = _bf_pli
                                                        _rbf['pliLight'] = _bf_plil
                                                        _rbf['rank_excluded_reason'] = None
                                                        changed_uids.add(_rbf['uid'])

                                                # P3.1: Generic rank_excluded_reason fallback from flags (and score/class for remaining unranked live 2026 rows)
                                                for _r67f in rows:
                                                    if not _r67f.get('rankable') and not _r67f.get('rankableLight') and not _r67f.get('rank_excluded_reason'):
                                                        if _r67f.get('flags'):
                                                            _r67f['rank_excluded_reason'] = _r67f['flags'][0].replace('Mahlzeit-Check: ', '')
                                                            changed_uids.add(_r67f['uid'])
                                                        elif _r67f.get('pstat') == 'live 2026' and _r67f.get('dupOf') is None:
                                                            if _r67f.get('meal_class') == 'raw_ingredient' or _r67f.get('stage') == 'base':
                                                                _r67f['rank_excluded_reason'] = 'Rohzutat / Basiskomponente'
                                                            elif _r67f.get('meal_class') == 'protein_component' or _r67f.get('component'):
                                                                _r67f['rank_excluded_reason'] = 'Proteinkomponente (keine vollständige Mahlzeit)'
                                                            elif _r67f.get('meal_class') == 'snack_side':
                                                                _r67f['rank_excluded_reason'] = 'Snack / Beilage (keine Hauptmahlzeit)'
                                                            elif _r67f.get('score') is not None and _r67f['score'] < 30:
                                                                _r67f['rank_excluded_reason'] = 'Health-Score < 30'
                                                            if _r67f.get('rank_excluded_reason'):
                                                                changed_uids.add(_r67f['uid'])

                                                # sensecheck 68 (SC68):
                                                # 1. P1.1: Rescue 2 Billa meals in Linz (#1067 Omis Schmankerl Eiernockerl 330 g -> pli=31.6,
                                                #    #1478 Amlacher Kärntner Käsnudeln 600 g -> 2 portions à 300 g, pli=28.7) + bidirectional
                                                #    sameStore size alsoPack between #431 (400 g) and #432 (800 g) Spar Inzersdorfer Weinbeuschel.
                                                # 2. P2.1: Resolve stage='meal' vs component=True contradiction on 25 active live 2026 rows:
                                                #    - 13 pure meat/fish/veggie components -> stage='prot', meal_class='protein_component'
                                                #    - 7 complete meals/bowls + 5 snack/baguette/dumpling rows -> component=False & strip false
                                                #      'Proteinkomponente (keine vollständige Mahlzeit)' suffix.
                                                # 3. P2.2: Normalize 5 bofrost twin-pack pizzas (740-838 g = 2 Pizzen) to 1 pizza per portion
                                                #    (#2968 -> pli=34.1, #2966 -> pli=33.9, #2967 -> pli=30.8, #2970 -> pli=30.7, #3052 -> pli=27.8).
                                                # 4. P3.1: Whitespace trim/collapse in rank_excluded_reason, flags, and meal_check['reason'],
                                                #    and check stage in ('side', 'veg') or meal_class == 'snack_side' before component=True
                                                #    for #44, #660, #1282, #1284, #1339, #3159, #3379, #3669.
                                                if os.environ.get('SC68_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC68', '0') != '1':
                                                    # P1.1(a): Rescue #1067 [Billa] Omis Schmankerl Eiernockerl (330 g, €3.49, 492 kcal, 21.4 g P, Score 32.5)
                                                    _r1067 = _pmm_by_id.get(1067)
                                                    if _r1067 is not None:
                                                        _r1067['stage'] = 'meal'
                                                        _r1067['segment'] = 'ready_meal'
                                                        _r1067['meal_class'] = 'meal'
                                                        _r1067['gang'] = 'haupt'
                                                        _r1067['component'] = False
                                                        _r1067['pPorEff'] = 3.49
                                                        _r1067['meal_check'] = {
                                                            'portion': 330,
                                                            'kcal': 492,
                                                            'protein': 21.4,
                                                            'ok': True,
                                                            'cls': 'meal',
                                                            'reason': None,
                                                        }
                                                        _r1067['flags'] = []
                                                        _r1067['rankable'] = True
                                                        _r1067['rankableLight'] = False
                                                        _r1067['pli'] = 31.6
                                                        _r1067['pliLight'] = None
                                                        _r1067['rank_excluded_reason'] = None
                                                        changed_uids.add(_r1067['uid'])

                                                    # P1.1(b): Normalize #1478 [Billa] Amlacher Kärntner Käsnudeln (600 g, €8.49, Score 30.3) to 2 portions à 300 g
                                                    _r1478 = _pmm_by_id.get(1478)
                                                    if _r1478 is not None:
                                                        _r1478['portion'] = 300
                                                        _r1478['portion_g'] = 300
                                                        _r1478['portion_source'] = 'pack_2portions'
                                                        _r1478['kcalPor'] = 456.0
                                                        _r1478['kcal_meal'] = 456
                                                        _r1478['protPor'] = 23.1
                                                        _r1478['saltPor'] = 4.2
                                                        _r1478['saltPct'] = 70
                                                        _r1478['pPor'] = 4.25
                                                        _r1478['pPorEff'] = 4.25
                                                        _r1478['ppe'] = 5.4
                                                        _r1478['stage'] = 'meal'
                                                        _r1478['segment'] = 'ready_meal'
                                                        _r1478['meal_class'] = 'meal'
                                                        _r1478['gang'] = 'haupt'
                                                        _r1478['component'] = False
                                                        _r1478['meal_check'] = {
                                                            'portion': 300,
                                                            'kcal': 456,
                                                            'protein': 23.1,
                                                            'ok': True,
                                                            'cls': 'meal',
                                                            'reason': None,
                                                        }
                                                        _r1478['flags'] = []
                                                        _r1478['rankable'] = True
                                                        _r1478['rankableLight'] = False
                                                        _r1478['pli'] = 28.7
                                                        _r1478['pliLight'] = None
                                                        _r1478['rank_excluded_reason'] = None
                                                        changed_uids.add(_r1478['uid'])

                                                    # P1.1(c): Bidirectional sameStore size alsoPack on #431 (400 g) <-> #432 (800 g) [Spar] Inzersdorfer Weinbeuschel
                                                    _r431 = _pmm_by_id.get(431)
                                                    _r432 = _pmm_by_id.get(432)
                                                    if _r431 is not None and _r432 is not None:
                                                        _r431['alsoPack'] = [{
                                                            'store': 'Spar', 'kind': 'size', 'n': None,
                                                            'size': 800.0, 'label': '800 g', 'id': 432,
                                                            'sameStore': True, 'uid': _r432['uid'],
                                                        }]
                                                        _r432['alsoPack'] = [{
                                                            'store': 'Spar', 'kind': 'size', 'n': None,
                                                            'size': 400.0, 'label': '400 g', 'id': 431,
                                                            'sameStore': True, 'uid': _r431['uid'],
                                                        }]
                                                        changed_uids.add(_r431['uid'])
                                                        changed_uids.add(_r432['uid'])

                                                    # P2.1(a): Reclassify 13 pure meat/fish/veggie components from stage='meal' to stage='prot', meal_class='protein_component'
                                                    for _p21_prot_id in (662, 867, 1288, 1332, 2082, 2440, 2503, 2504, 2506, 2535, 2952, 3387, 3896):
                                                        _rp21p = _pmm_by_id.get(_p21_prot_id)
                                                        if _rp21p is not None:
                                                            _rp21p['stage'] = 'prot'
                                                            _rp21p['meal_class'] = 'protein_component'
                                                            _rp21p['component'] = True
                                                            changed_uids.add(_rp21p['uid'])

                                                    # P2.1(b): Clean component=False and strip false 'Proteinkomponente (keine vollständige Mahlzeit)' suffix
                                                    # on 7 complete meals/bowls (#438, #1337, #1517, #1546, #1676, #1807, #3251) and 5 snack/baguette/dumpling rows (#594, #1279, #1748, #2502, #3540)
                                                    for _p21_clean_id in (438, 1337, 1517, 1546, 1676, 1807, 3251, 594, 1279, 1748, 2502, 3540):
                                                        _rp21c = _pmm_by_id.get(_p21_clean_id)
                                                        if _rp21c is not None:
                                                            _rp21c['component'] = False
                                                            _mc21c = dict(_rp21c.get('meal_check') or {})
                                                            if isinstance(_mc21c.get('reason'), str):
                                                                _mc21c['reason'] = _mc21c['reason'].replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').replace('Proteinkomponente (keine vollständige Mahlzeit)', '').strip() or None
                                                                _rp21c['meal_check'] = _mc21c
                                                            if _rp21c.get('flags'):
                                                                _rp21c['flags'] = [
                                                                    f.replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').replace('Proteinkomponente (keine vollständige Mahlzeit)', '').strip()
                                                                    for f in _rp21c['flags']
                                                                ]
                                                            if isinstance(_rp21c.get('rank_excluded_reason'), str):
                                                                _rp21c['rank_excluded_reason'] = _rp21c['rank_excluded_reason'].replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').replace('Proteinkomponente (keine vollständige Mahlzeit)', '').strip()
                                                            changed_uids.add(_rp21c['uid'])

                                                    # P2.2: Normalize 5 bofrost twin-pack pizzas (740-838 g = 2 Pizzen) to 1 pizza per portion (2 portions)
                                                    for _pz_id, _pz_por, _pz_kpor, _pz_kmeal, _pz_ppor, _pz_spor, _pz_spct, _pz_prpor, _pz_ppe, _pz_pli in (
                                                        (2968, 376, 778.5, 778, 39.5, 3.76, 63, 6.75, 5.9, 34.1),
                                                        (2966, 419, 884.0, 884, 46.1, 5.03, 84, 6.75, 6.8, 33.9),
                                                        (2967, 416, 844.5, 844, 40.0, 4.58, 76, 6.75, 5.9, 30.8),
                                                        (2970, 370, 766.0, 766, 37.8, 4.44, 74, 6.5,  5.8, 30.7),
                                                        (3052, 397, 774.0, 774, 33.4, 5.16, 86, 6.75, 4.9, 27.8),
                                                    ):
                                                        _rpz = _pmm_by_id.get(_pz_id)
                                                        if _rpz is not None:
                                                            _rpz['portion'] = _pz_por
                                                            _rpz['portion_g'] = _pz_por
                                                            _rpz['portion_source'] = 'pack_2portions'
                                                            _rpz['kcalPor'] = _pz_kpor
                                                            _rpz['kcal_meal'] = _pz_kmeal
                                                            _rpz['protPor'] = _pz_ppor
                                                            _rpz['saltPor'] = _pz_spor
                                                            _rpz['saltPct'] = _pz_spct
                                                            _rpz['pPor'] = _pz_prpor
                                                            _rpz['pPorEff'] = _pz_prpor
                                                            _rpz['ppe'] = _pz_ppe
                                                            _rpz['meal_class'] = 'meal'
                                                            _rpz['gang'] = 'haupt'
                                                            _rpz['component'] = False
                                                            _rpz['meal_check'] = {
                                                                'portion': _pz_por,
                                                                'kcal': _pz_kmeal,
                                                                'protein': _pz_ppor,
                                                                'ok': True,
                                                                'cls': 'meal',
                                                                'reason': None,
                                                            }
                                                            _rpz['flags'] = [f for f in (_rpz.get('flags') or []) if 'Mehrportionen-Packung' not in f]
                                                            _rpz['rankable'] = True
                                                            _rpz['rankableLight'] = False
                                                            _rpz['pli'] = _pz_pli
                                                            _rpz['pliLight'] = None
                                                            _rpz['rank_excluded_reason'] = None
                                                            changed_uids.add(_rpz['uid'])

                                                    # P3.1: Check stage in ('side', 'veg') or meal_class == 'snack_side' before component=True
                                                    # (including #44, #660, #1282, #1284, #1339, #3159, #3379, #3669) and trim/collapse whitespace
                                                    for _s68_id in (3159, 3669):
                                                        _rs68 = _pmm_by_id.get(_s68_id)
                                                        if _rs68 is not None:
                                                            _mcs68 = dict(_rs68.get('meal_check') or {})
                                                            if isinstance(_mcs68.get('reason'), str):
                                                                _mcs68['reason'] = _mcs68['reason'].replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').strip()
                                                                _rs68['meal_check'] = _mcs68
                                                            if _rs68.get('flags'):
                                                                _rs68['flags'] = [f.replace(' Proteinkomponente (keine vollständige Mahlzeit)', '').strip() for f in _rs68['flags']]
                                                            _rs68['rank_excluded_reason'] = 'Snack / Beilage (keine Hauptmahlzeit)'
                                                            changed_uids.add(_rs68['uid'])

                                                    for _r68w in rows:
                                                        if (
                                                            not _r68w.get('rankable')
                                                            and not _r68w.get('rankableLight')
                                                            and _r68w.get('dupOf') is None
                                                            and not _r68w.get('rank_excluded_reason')
                                                            and (_r68w.get('live') is None or _r68w.get('price') is None)
                                                        ):
                                                            _r68w['rank_excluded_reason'] = 'Kein aktueller Preis 2026'
                                                            changed_uids.add(_r68w['uid'])
                                                        if (
                                                            (_r68w.get('stage') in ('side', 'veg') or _r68w.get('meal_class') == 'snack_side')
                                                            and _r68w.get('rank_excluded_reason') == 'Proteinkomponente (keine vollständige Mahlzeit)'
                                                        ):
                                                            _r68w['rank_excluded_reason'] = 'Snack / Beilage (keine Hauptmahlzeit)'
                                                            changed_uids.add(_r68w['uid'])
                                                        if isinstance(_r68w.get('rank_excluded_reason'), str):
                                                            _clean_rer = re.sub(r'\s{2,}', ' ', _r68w['rank_excluded_reason']).strip()
                                                            if _clean_rer != _r68w['rank_excluded_reason']:
                                                                _r68w['rank_excluded_reason'] = _clean_rer
                                                                changed_uids.add(_r68w['uid'])
                                                        if _r68w.get('flags'):
                                                            _clean_flgs = [re.sub(r'\s{2,}', ' ', f).strip() if isinstance(f, str) else f for f in _r68w['flags']]
                                                            if _clean_flgs != _r68w['flags']:
                                                                _r68w['flags'] = _clean_flgs
                                                                changed_uids.add(_r68w['uid'])
                                                        if isinstance((_r68w.get('meal_check') or {}).get('reason'), str):
                                                            _clean_mck = re.sub(r'\s{2,}', ' ', _r68w['meal_check']['reason']).strip()
                                                            if _clean_mck != _r68w['meal_check']['reason']:
                                                                _mc_w = dict(_r68w['meal_check'])
                                                                _mc_w['reason'] = _clean_mck
                                                                _r68w['meal_check'] = _mc_w
                                                                changed_uids.add(_r68w['uid'])

    # Check latest online_availability_*.json
    av_files = sorted(glob.glob(os.path.join(base_dir, 'analysis/online_availability_*.json')))
    if os.environ.get('GOOD_CHOICE_AVAILABILITY'):  # sensecheck 52 P1: tests pin the snapshot the canonical baseline was built from
        av_files = [os.path.join(base_dir, 'analysis', os.environ['GOOD_CHOICE_AVAILABILITY'])]
    if av_files:
        av = json.load(open(av_files[-1]))
        av_fn = os.path.basename(av_files[-1])
        unav = set(av.get('unavailable_uids') or [])
        if not _sc54_pmm_on and av_fn == 'online_availability_2026-10-24.json':
            unav = (unav - {'mumdjo42mt'}) | {'honb7zkubm', 'd1u0iuvtkz'}
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
        global _XL
        _sc63_xl_on = _sc54_pmm_on and os.environ.get('SC63_FIXES', '1') != '0' and os.environ.get('GOOD_CHOICE_DISABLE_SC63', '0') != '1'
        if _sc63_xl_on:
            _XL = re.compile(r'\(\s*xl[^)]*\)|\bxl\b|\(\s*\d+[.,]?\d*\s*(g|kg)\s*\)|\(?\s*\b\d+\s*portion(en)?\b\s*\)?|\b\d+\s*(stück|stk)\b|\b\d+er[- ]?(packung|pack)\b', re.I)
        else:
            _XL = re.compile(r'\(\s*xl[^)]*\)|\bxl\b|\(\s*\d+[.,]?\d*\s*(g|kg)\s*\)|\(?\s*\b\d+\s*portion(en)?\b\s*\)?', re.I)
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
