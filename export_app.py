import json,re
exec(open('build.py').read().split('E=html.escape')[0])
src={(x.get('name') or '').strip():x for x in d}
SRCU={x.get('url'):x for x in d if x.get('url')}
for i,r in enumerate(R):
    x=SRCU.get(r.get('url')) or src.get(r['name'],{}); r['id']=i
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
MEALPREP_ONLY={'PrepMyMeal','Juit','every.','LiveFresh','FitTaste','Fit to Go'}
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
    raw=re.search(r'faschiert|hackfleisch|\bhack\b|filet|brust|keule|unterkeul|oberkeul|flügel|wings|steak|schnitzel|leber|gulaschfleisch|geschnetzeltes|würfel|minute|ganzes|ganzer|hendl\b|hähnchen|kotelett|karree|schopf|bauch|lachs|forelle|garnelen|shrimps|kabeljau|seelachs|zander|saibling|thunfisch.*steak',t) and not re.search(r'gegart|gebraten|gebacken|schlemmerfilet|bordelaise|backfisch|backteig|paniert|gegrillt|mariniert|sous|knusper|nugget|backhendl|cordon|fertig|gekocht|geräuchert|räucher|mit |sauce|soße|in |menü|curry|gulasch\b|suppe|topf|salat|knödel|reis|bowl|wrap|sandwich|pizza|burger|stäbchen|sticks|chili|bbq|grill|pulled|rahm|natur\*pur bio hendl mini',t) and not r['pack'].startswith('Dose')
    if raw or ((r.get('kcal') or 0)>=300 and re.search(r'suppe|nudel|pulver|teigwar|einlage|abc|sternderl|gerstl|hörnchen|fadennudel|buchstaben|instant|terrine|cup|reis\b|couscous|bulgur|polenta|grieß',t) and (r.get('fat') or 0)<15) or re.search(r'barilla lasagne|collezione lasagne|recheis lasagne|lasagne hartweizen|glutenfreie lasagne|lasagneblätter|lasagne-?platten',t) or ('lasagne' in t and (r.get('kcal') or 0)>=300): stg='base'
    elif re.search(r'erdbeer|marillen|zwetschk|nougat|germknödel|topfenknödel|mehlspeis|kaiserschmarr|powidl|mohn|vanille|schoko',t): stg='base'
    elif r.get('dry') or re.search(r'sauce|soße|fix\b|fix |pesto|gewürz|würfel|pulver|bouillon|fond|dressing|mehl|paniermehl|brühe(?!.*einlage)',t) and not re.search(r'suppe|topf|\bin \w*(sauce|soße)|mit \w*(sauce|soße)|\bpizza\b|ristorante|intermezzo|tradizionale|ravioli|tortell|nudel|spaghetti|cannelloni|gnocchi|reis|fleisch|würstel|huhn|hendl|rind',t): stg='base'
    elif re.search(r'suppe|eintopf|\\btopf|topf\\b|chili con|gulasch.*dose|linsen|bohnen.*eintopf|ragout|consommé|ramen',t): stg='stew'
    elif not hasMit and re.search(r'ripperl|spare ?rib|spie(ß|ss)|schnitzel|cordon|nugget|stäbchen|sticks|filet|laibchen|cevap|burger|frikadell|fleischlaibchen|leberkäs|steak|hendl(?!.*mit)|chicken wings|drumstick|keule|grillwurst|bratwurst|kebab|gyros|pulled|tofu|tempeh|falafel|fischburger|backfisch|lachs',t): stg='prot'
    elif not hasMit and re.search(r'knödel|reis\b|basmati|püree|kroketten|pommes|frites|rösti|gnocchi|spätzle|nockerl|kartoffel|erdäpfel|couscous|bulgur|polenta|nudeln',t): stg='side'
    elif not hasMit and re.search(r'gemüse|brokkoli|spinat|erbsen|karotte|fisolen|rahmspinat|kohl|bohnen|mais|kaiserschoten|zucchini|blattspinat|salat',t): stg='veg'
    else: stg='meal'
    if r.get('nonfood') or r.get('dry'): stg='base'
    elif re.search(r'backerbsen|fertigmischung|nockerlgrieß|pastina|naturreis|spätzlekäse|kartoffelpüree|sugo|party-spies|suppengemüse|suppeneinlage',t): stg='base'
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
    sweet=re.search(r'kaiserschmarr|germknödel|topfenstrudel|apfelstrudel|milchreis|marillenknödel|zwetschk|erdbeerknödel|topfenknödel|himbeerknödel|heidelbeerknödel|milchrahmstrudel|mohnnudel|buchtel|palatschink|grießbrei|pudding|nougat|powidl|dessert|mehlspeis|scheiterhaufen|schoko|tiramisu|panna cotta',t)
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
    _x=SRCU.get(r.get('url')) or src.get(r['name'],{})
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
    if _x.get('segment')=='grocery': r['segment']='grocery'
    if r.get('dry') or r.get('nutrition_basis')=='dry' or stg not in ('meal','stew') or r.get('gang')=='dessert' or r.get('segment')=='grocery' or r.get('meal_class')!='meal' or not (_x.get('meal_check') or {}).get('ok'): r['rankable']=False
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
    r['pli']=round(0.5*r['score']+0.5*min((_ppor/_epor)/20,1)*100,1) if r['rankable'] and _epor else None
    if r['pli'] is None: r['rankable']=False
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
_light=[]
for _r in R:
    if _r.get('meal_class') in ('baby','dessert','dry','snack_side'): continue
    if _r.get('segment')=='baby_food' or _r.get('nonfood'): continue
    if _r.get('meal_class')!='light_meal': continue
    _mc=_r.get('meal_check') or {}; _k,_p=_mc.get('kcal'),_mc.get('protein')
    if not (_k and 300<=_k<400): continue
    if _r.get('dry') or _r.get('nutrition_basis')=='dry' or _r.get('gang')=='dessert': continue
    if _r.get('segment') in ('grocery','meal_kit','baby_food') or _r.get('component') or _r.get('stage') not in ('meal','stew'): continue
    if not _r.get('score') or _r['score']<30 or not _r.get('price') or not _r.get('store'): continue
    if str(_r['store']).startswith('unbekannt') or _r.get('pstat') not in ('live 2026','aktuell'): continue
    if _BABY.search(_r.get('name') or '') or _DRYFIX.search(_r.get('name') or ''): continue
    _ep=(_r['price']*_mc['portion']/_r['size']) if _r.get('size') and _mc.get('portion') else _r['price']
    if not _ep or _p is None: continue
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
def _collapse(cands,score_fn,n=30):
    ordered=sorted(cands,key=score_fn,reverse=True); seen={}; kept=[]; collapsed=0; also={}
    for r in ordered:
        ks=_twin_keys(r); hit=next((seen[k] for k in ks if k in seen),None)
        if hit is not None:
            collapsed+=1; also.setdefault(hit['id'],set()).add(r['store'])
            for k in ks: seen.setdefault(k,hit)
            continue
        for k in ks: seen[k]=r
        kept.append(r)
        if len(kept)>=n: break
    for r in kept:
        o=sorted(s for s in also.get(r['id'],()) if s and s!=r.get('store'))
        if o: r['alsoAt']=o
    return kept,collapsed
topPLI,_c_pli=_collapse([r for r in R if r.get('rankable') and r.get('pli') is not None],lambda r:r['pli'])
top_h,_c_h=_collapse([r for r in R if r.get('rankable') and r.get('score') is not None],lambda r:r['score'])
top_pe,_c_pe=_collapse([r for r in R if r.get('rankable') and r.get('ppe') and r.get('pstat')=='live 2026' and r.get('pack')!='Trocken/Instant'],lambda r:r['ppe'])
topLight,_c_light=_collapse(_light,lambda r:r['pliLight'])
print('rankings: light',len(_light),'baby',_n_baby,'exact_dup',_n_exact,'ean_dup',_n_ean,'near_dup',_n_near,'collapsed pli/h/pe/light',_c_pli,_c_h,_c_pe,_c_light)
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
out=dict(producers=producers,companyLogos=companyLogos,qaStats=qa,catIcon=CATICON,catProt=[n for n,_,_ in PROT]+['vegan','vegetarisch'],catDish=[n for n,_,_ in DISH]+['Beilage/Gemüse'],topPLI=[r['id'] for r in topPLI],topLight=[r['id'] for r in topLight],rows=R,sides=sides,topHealth=[idx[id(r)] for r in top_h],topPE=[idx[id(r)] for r in top_pe],stats=S,
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
json.dump(out,open('/workspace/fertig-app/public/data.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(R),len(sides),len(combos),len(veg),len(sal),len(sd))
for c in combos[:6]: print(R[c['main']]['name'],'|',sides[c['veg']]['name'] if False else [s['name'] for s in sides if s['id']==c['veg']],'|',[s['name'] for s in sides if s['id']==c['side']],c)
