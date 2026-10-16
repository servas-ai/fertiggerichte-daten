"""Good Choice health score v2 (see analysis/score_v2.md). Pure functions, no I/O except load_off()."""
import re, json, os
DAY = dict(kcal=2000, protein=50, salt=6, satfat=20, sugar=90, fiber=30)   # EU RI (Reg. 1169/2011 Anh. XIII), fiber 30 g DGE
SUGAR_PTS = [3.4,6.8,10,14,17,20,24,27,31,34,37,41,44,48,51]                # Nutri-Score 2023 sugar thresholds (g/100 g)
MEAL_MIN, MEAL_MAX, SNACK_MAX = 300, 1000, 250
NOVA4 = re.compile(r'isolat|protein-?isolat|hydrolys|modifizierte stärke|maltodextrin|dextrose|glukose-?sirup|glucose-?sirup|fruktose-?sirup|invertzucker|aroma(?!tisch)|geschmacksverstärker|mononatriumglutamat|glutamat|emulgator|verdickungsmittel|stabilisator|farbstoff|süßungsmittel|sucralose|acesulfam|aspartam|carrageen|xanthan|guarkernmehl|phosphat|\be ?\d{3}[a-z]?\b|isolate|flavou?ring|modified starch|emulsifier|thickener|sweetener|hydrolysed',re.I)
VEG_ING = re.compile(r'gemüse|tomate|karotte|möhre|zwiebel|paprika|zucchini|spinat|brokkoli|broccoli|kohl|kraut|erbse|bohne|linse|kichererbse|kürbis|aubergine|pilz|champignon|lauch|sellerie|mais|kartoffel(?!stärke)|süßkartoffel|rote rübe|rote bete|fenchel|blumenkohl|karfiol|mangold|rucola|salat|gurke|vegetable|tomato|carrot|onion|pepper|lentil|bean|chickpea|pea\b|spinach|mushroom',re.I)
NOT_VEG = re.compile(r'pulver|extrakt|stärke|aroma|fett|öl\b|mehl|eiweiß|protein|sirup',re.I)
PREP_WATER = re.compile(r'(\d{2,4})\s*ml\s*(\w+\s+)?(wasser|milch)',re.I)
DRY_NAME = re.compile(r'lasagne(blätter|platten|-?platten)?$|lasagne hartweizen|suppe-(abc|gerstl|sternderl|mini hörnchen|hörnchen)|suppeneinlage|backerbsen|risottoreis|pulver|terrine|bouillon|\bfix\b|instant|cup\b|5 ?min|sojaschnetzel|soja geschnetzel|sojagranulat',re.I)

def n(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def load_off(path='off_v2_cache.json', legacy='nutri_off_cache.json'):
    c = {}
    if os.path.exists(legacy):
        for e, v in json.load(open(legacy)).items():
            if isinstance(v, dict): c[e] = {'nova_group': v.get('nova'), 'fvl_pct': v.get('fvl_pct')}
    if os.path.exists(path):
        for e, v in json.load(open(path)).items():
            if isinstance(v, dict) and not v.get('_error') and not v.get('_missing'): c[e] = {**c.get(e, {}), **v}
    return c

def ingredients_text(x, off):
    t = x.get('ingredients') or (off or {}).get('ingredients_text_de') or (off or {}).get('ingredients_text')
    if isinstance(t, list): t = ', '.join(str(i.get('text') if isinstance(i, dict) else i) for i in t)
    return t or None

def nova_of(x, off):
    """(nova, source). No packaging-based guess."""
    if off and off.get('nova_group'): return int(off['nova_group']), 'off'
    if x.get('nova') and x.get('nova_source'): return int(x['nova']), 'off'  # nutri_enrich (OFF)
    t = ingredients_text(x, off)
    if t:
        return (4 if NOVA4.search(t) else 3), 'ingredients_markers'
    return None, 'unknown'

def veg_share(x, off):
    """(pct, source) of vegetables/legumes in ingredients."""
    if n((off or {}).get('fvl_pct')) is not None: return round(n(off['fvl_pct']), 1), 'off_fvl'
    ing = (off or {}).get('ingredients') or []
    if ing:
        tot = 0.0
        for g in ing:
            txt = str(g.get('text') or g.get('id') or '')
            pct = n(g.get('percent')) or n(g.get('percent_estimate'))
            if pct and (g.get('vegetable') == 'yes' or VEG_ING.search(txt)) and not NOT_VEG.search(txt): tot += pct
        return round(min(tot, 100), 1), 'off_percent'
    t = ingredients_text(x, off)
    if not t: return None, 'unknown'
    parts = [p.strip() for p in re.split(r',(?![^()]*\))', t) if p.strip()]
    tot = 0.0
    for i, p in enumerate(parts[:12]):
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*%', p)
        if VEG_ING.search(p) and not NOT_VEG.search(p):
            tot += float(m.group(1).replace(',', '.')) if m else max(30 - 6 * i, 3)  # order-based estimate
    return round(min(tot, 100), 1), 'ingredients_order'

def nutrition_basis(x, off):
    """Return (basis, factor, note). factor converts as-sold /100 g into prepared /100 g."""
    k, fat = n(x.get('kcal_100')), n(x.get('fat_100')) or 0
    tk = x.get('packaging') == 'Tiefkühl (TK)'
    dryish = bool(k and ((k >= 300 and fat < 10 and not tk) or (x.get('packaging') == 'Trocken/Instant' and k >= 250)
              or (k >= 300 and DRY_NAME.search(x.get('name') or ''))))
    if not dryish: return 'as_sold', 1.0, None
    nm = (off or {}).get('nutriments') or {}
    if n(nm.get('energy-kcal_prepared_100g')):
        return 'prepared', n(nm['energy-kcal_prepared_100g']) / k, 'OFF prepared values'
    m = PREP_WATER.search(str(x.get('prep') or '') + ' ' + str(x.get('prep_hint') or ''))
    sz = n(x.get('size_g'))
    if m and sz:
        f = sz / (sz + float(m.group(1)))
        return 'prepared', f, f'preparation ratio {sz:g} g + {m.group(1)} ml'
    return 'dry', None, None

def portion(x, off, stage=None):
    """(portion_g, source). Never 100 g placeholder."""
    sz = n(x.get('size_g')); nm = (x.get('name') or '').lower()
    m = re.search(r'(\d+)\s*(portionen|port\.|portions)', nm)
    if m and sz and int(m.group(1)) > 1: return round(sz / int(m.group(1))), 'name_portions'
    # Sensecheck 10: family-size packs that apps treated as 1 portion (Gurkerl Iglo Lasagne 700 g → 868 kcal;
    # M&S 4 Breaded Haddock Fillets 500 g → 870 kcal). Split into 2 portions when size matches.
    # Sensecheck 11: any 650–800 g lasagne (Hofer 'IGLO Lasagne 700g' had OFF serving 400 g) = 2 portions, before off_serving
    if sz and (sz >= 650 and re.search(r'lasagne al forno', nm) or 650 <= sz <= 800 and re.search(r'\blasagne\b(?!bl|-?platt)', nm)): return round(sz / 2), 'family_pack'
    if sz and 450 <= sz <= 550 and re.search(r'\d+\s*breaded haddock', nm): return round(sz / 2), 'family_pack'
    # Sensecheck 9: bofrost* publishes the portion count per pack ('2 x 250 g' → portions 2) → per-portion
    # price/kcal/protein instead of the whole 500 g pack (Tafelspitz 22.99 €/855 kcal 'per portion' was 2 portions).
    # Limited to bofrost* (verified grammage line); other providers' 'portions' fields are not verified yet.
    pv = n(x.get('portions'))
    if pv and pv > 1 and sz and 'bofrost' in str(x.get('store') or '').lower(): return round(sz / pv), 'provider_portions'
    _pp = piece_portion(nm, sz)  # review 13 B: before off_serving (Goldschatz 600 g had OFF 100 g)
    if _pp: return _pp, 'piece_x2'
    sq = n((off or {}).get('serving_quantity'))
    # an OFF serving larger than the pack is impossible for a ready-to-eat pack (followfood pizza 300 g, serving 339 g
    # → pPor > pack price) → ignore it. Instant/dry packs (serving = prepared weight with water, >300 kcal/100 g) keep it.
    k100 = n(x.get('kcal_100'))
    big = bool(sz and sq and sq > sz * 1.05 and x.get('packaging') != 'Trocken/Instant' and k100 is not None and k100 <= 300)
    if sq and 50 <= sq <= 1000 and not big and not (sq == 100 and not (off or {}).get('serving_size')): return round(sq), 'off_serving'
    if sz and 150 <= sz <= 700 and stage in (None, 'meal', 'stew'): return round(sz), 'pack_single'
    return None, 'unknown'

def sugar_points(s):
    return 0 if s is None else sum(s > t for t in SUGAR_PTS)

def meal_class(kcal_meal):
    if kcal_meal is None: return 'unknown'
    if kcal_meal < SNACK_MAX: return 'snack_side'
    if kcal_meal < MEAL_MIN: return 'light_meal'
    if kcal_meal <= MEAL_MAX: return 'meal'
    return 'multi_portion'

def score_v2(x, off=None, stage=None):
    """Returns dict of new fields incl. health_score (0-100) or None."""
    out = {}
    basis, fac, note = nutrition_basis(x, off)
    out.update(nutrition_basis=basis, nutrition_note=note)
    f = fac or 1.0
    g = lambda a: (n(x.get(a)) * f) if n(x.get(a)) is not None else None
    p, k, s, sf, fi, su = g('protein_100'), g('kcal_100'), g('salt_100'), g('satfat_100'), g('fiber_100'), g('sugar_100')
    nova, nsrc = nova_of(x, off); out.update(nova=nova, nova_source=nsrc)
    vp, vsrc = veg_share(x, off); out.update(veg_pct=vp, veg_source=vsrc)
    pg, psrc = portion(x, off, stage)
    sz = n(x.get('size_g'))
    if basis == 'prepared' and pg and fac: pg = round(pg / fac); psrc += '+prepared'
    out.update(portion_g=pg, portion_source=psrc)
    ref = pg or sz
    kmeal = round(k * ref / 100) if k is not None and ref else None
    out['kcal_meal'] = kmeal
    out['meal_class'] = meal_class(kmeal) if basis != 'dry' else 'dry'
    if pg:
        out['per_portion'] = {kk: (round(v * pg / 100, 2) if v is not None else None) for kk, v in
                              dict(kcal=k, protein=p, salt=s, satfat=sf, sugar=su, fiber=fi).items()}
        out['day_pct'] = {kk: (round(v / DAY[kk] * 100) if v is not None else None) for kk, v in out['per_portion'].items()}
    else:
        out['per_portion'] = None; out['day_pct'] = None
    if basis == 'dry' or p is None or not k or k <= 0:
        out['health_score'] = None; out['score_parts'] = None; return out
    pd = p / k * 100
    sp = sugar_points(su)
    parts = {
        'base': 30.0,
        'protein': min(pd / 10, 1) * 35 * (0.5 if sp >= 3 else 1),         # sweet products: protein bonus halved
        'salt': 0 if s is None else -min(max(s - 0.6, 0) / 1.4, 1) * 20,
        'satfat': 0 if sf is None else -min(max(sf - 1.5, 0) / 4.5, 1) * 15,
        'sugar': -min(sp, 10) * 2.0,                                        # up to -20 (≥34 g)
        'fiber': 0 if fi is None else min(fi / 6, 1) * 10,
        'veg': 0 if vp is None else min(vp / 40, 1) * 10,
        'nova': {4: -10, 3: 0, 2: 3, 1: 5}.get(nova, -3),                  # unknown NOVA: small uncertainty malus
    }
    pp = out['day_pct']
    if pp:   # portion vs. daily target
        if pp.get('salt') and pp['salt'] > 40: parts['portion_salt'] = -min((pp['salt'] - 40) / 30, 1) * 8
        if pp.get('satfat') and pp['satfat'] > 40: parts['portion_satfat'] = -min((pp['satfat'] - 40) / 30, 1) * 5
        if pp.get('protein') and pp['protein'] >= 40 and sp < 3: parts['portion_protein'] = 5
    out['score_parts'] = {kk: round(v, 1) for kk, v in parts.items()}
    out['health_score'] = round(max(0, min(100, sum(parts.values()))), 1)
    return out

# --- Sensecheck 2: hard meal check, dessert + grocery labels ---
MEAL_KCAL_MIN, MEAL_KCAL_MAX, MEAL_PROT_MIN = 400, 900, 20
DESSERT = re.compile(r'dessert|crème brûlée|creme brulee|brûlée|lavakuchen|lava cake|schokokuchen|kuchen\b|torte\b|mousse|pudding|panna cotta|tiramisu|cheesecake|topfencreme|grießbrei|milchreis|kaiserschmarr|germknödel|strudel(?!teig)|marillenknödel|zwetschk|erdbeerknödel|topfenknödel|himbeerknödel|heidelbeerknödel|waldbeerknödel|nougatknödel|topfennockerl|apfelringe im backteig|mohnnudel|buchtel|palatschink|scheiterhaufen|\beis\b|eiscreme|sorbet|muffin|brownie|waffel|crêpe|tarte|profiterol|soufflé|fondant',re.I)
DESSERT_NOT = re.compile(r'apfelstrudel.*?(gemüse|spinat)|gemüsestrudel|spinatstrudel|krautstrudel|fleischstrudel|lachsstrudel|blätterteigstrudel.*(gemüse|spinat|fleisch|lachs)|pizzastrudel|flammkuchen|zwiebelkuchen|quiche|palatschink\w*.*(schinken|käse|lauch|spinat|fleisch)',re.I)
GROCERY = re.compile(r'toastkäse|käse ?scheiben|scheibenkäse|schmelzkäse|streichkäse|frischkäse|\bgouda\b|emmentaler|mozzarella$|\bfeta\b|hartkäse|bergkäse|camembert|\bbrot\b|protein ?brot|eiweißbrot|toastbrot|\btoast\b(?!.*(hawaii|schinken-käse))|vollkornbrot|semmel$|gebäck|brötchen|aufstrich|streichwurst|leberwurst|pastete|\bwurst(aufschnitt)?\b|aufschnitt|salami|schinken ?scheiben|wurstsalat|fleischsalat|eiersalat|thunfischsalat|\bbutter\b(?!\s*-?\s*chicken)|margarine|honig|marmelade|konfitüre|nutella|pesto|sugo|ramyun|ramen nudel|instant ?nudel|nudelsuppe instant|cup noodle|noodle cup|yum yum|mama nudel',re.I)

def labels(x):
    nm = ' '.join(str(x.get(k) or '') for k in ('name',))
    dessert = bool(DESSERT.search(nm)) and not DESSERT_NOT.search(nm)
    grocery = bool(GROCERY.search(nm)) and not dessert
    return dessert, grocery

def meal_check(x, v2):
    """Hard ready-meal gate: per portion 400-900 kcal and >=20 g protein.
    Portion = portion_g (known source); if unknown, the pack counts only when 150-700 g."""
    k, p = n(x.get('kcal_100')), n(x.get('protein_100'))
    psrc = v2.get('portion_source') or 'unknown'
    pg = v2.get('portion_g') if psrc not in ('unknown',) else None
    sz = n(x.get('size_g'))
    if v2.get('nutrition_basis') == 'dry': return dict(ok=False, cls='dry', reason='Trockenprodukt')
    if not pg:
        if sz and 150 <= sz <= 700: pg = sz
        elif sz and sz > 700: return dict(ok=False, cls='multi_portion', reason=f'Mehrportionen-Packung ({sz:g} g), Portionszahl nicht angegeben')
        else: return dict(ok=False, cls='unknown', reason='Portion unbekannt')
    f = 1.0
    if v2.get('nutrition_basis') == 'prepared' and k and v2.get('kcal_meal') and v2.get('portion_g'):
        f = v2['kcal_meal'] / (k * v2['portion_g'] / 100) if pg == v2['portion_g'] else 1.0
    if k is None or p is None: return dict(ok=False, cls='unknown', reason='Nährwerte fehlen', portion=pg)
    kp, pp = round(k * f * pg / 100), round(p * f * pg / 100, 1)
    d = dict(portion=pg, kcal=kp, protein=pp)
    if kp < 250: return dict(d, ok=False, cls='snack_side', reason=f'{kp} kcal/Portion – Snack/Beilage')
    if kp < MEAL_KCAL_MIN: return dict(d, ok=False, cls='light_meal', reason=f'{kp} kcal/Portion < {MEAL_KCAL_MIN}')
    if kp > MEAL_KCAL_MAX: return dict(d, ok=False, cls='multi_portion', reason=f'{kp} kcal/Portion > {MEAL_KCAL_MAX}')
    if pp < MEAL_PROT_MIN: return dict(d, ok=False, cls='light_meal', reason=f'{pp} g Protein/Portion < {MEAL_PROT_MIN}')
    return dict(d, ok=True, cls='meal', reason=None)

SNACK = re.compile(r'\bbrot\b|brötchen|semmel|weckerl|sandwich|burger|baguette|\btoast|toastkäse|wurstsalat|ramyun|ramen nudel|instant ?nudel|cup noodle|noodle cup|yum yum|mama nudel|nudelsnack|bistro baguette|piccolini|wrap\b(?!.*bowl)|hot ?dog|pizzaschnitte|leberkässemmel',re.I)
# Sensecheck 11: breaded/fried protein without a side-dish word is a component ('Zum Kombinieren'), not a main-ranking meal
BREADED = re.compile(r'paniert|panade|\bcrispy\b|crispy|knusper|karaage|tempura|katsu|popcorn.?chicken|\bcrunch\b|\bbreaded\b|backfisch|backhendl|nuggets?\b|\bsticks?\b|stäbchen|schnitzel|cordon bleu|gebacken\w*\s+(hendl|huhn|hühner|fisch|champignon)',re.I)
SIDE_WORD = re.compile(r'reis\b|naturreis|kartoffel|erdäpfel|püree|pueree|nudel|pasta|spaghetti|penne|gemüse|pommes|fritten|wedges|rösti|kroketten|salat|salad|spätzle|knödel|bowl|couscous|bulgur|quinoa|\bmit\b|pizza|burger|wrap|sandwich|toast|baguette|menü|teller',re.I)
def breaded_component(nm): return bool(BREADED.search(nm or '')) and not SIDE_WORD.search(nm or '')
# hourly T06: plain sous-vide meat pieces (no sauce dish like Gulasch, no side) and plain vegan Köttbullar are protein components, not complete meals
SOUSVIDE_PIECE = re.compile(r'^(?!.*\b(gulasch|curry|asia|mit|und|dazu|auf)\b).*\b(entenbrust|rinderbacken|backerl|roastbeef|ribs|keule|huhn|hendl|beef\b.*)\b.*sous.?vide|^(?!.*\b(mit|dazu|auf|sauce|soße|püree|reis)\b).*köttbullar',re.I)
def plain_component(nm): return bool(SOUSVIDE_PIECE.search(nm or ''))
BREAKFAST = re.compile(r'frühstück|porridge|overnight ?oats|\bmüsli|\bmuesli|haferbrei|\bbrei\b',re.I)
COMPONENT = re.compile(r'suppenfleisch|lachsfilet|backhendl|keulen?\b|falafel|laibchen|fischstäbchen|nuggets?\b|cordon bleu|schnitzel(?!.*(mit|püree|reis|erdäpfel|kartoffel|pommes))|filet(?!.*(mit|reis|püree|gemüse))|tofu(?!.*(mit|curry|bowl))|tempeh|bratwurst|grillwurst|cevapcici|frikadell',re.I)
# Sensecheck 13: a component word ('Hühnerfilet', 'Laibchen', 'Lachsfilet') next to a separate carb word is a dish, not a component:
#  Iglo 'Französische Art Penne, Gemüse & Hühnerfilet', 'Faschierte Laibchen mit Kartoffelpüree', HelloFresh 'Miso-Lachsfilet auf … Reis'.
#  Whole words only, so 'Erdäpfellaibchen' / 'Kartoffelrösti' style compounds keep their component status.
CARB_WORD = re.compile(r'\b(penne|spaghetti\w*|pasta|nudeln?|tagliatelle|fusilli|rigatoni|makkaroni|reis|basmati(?:reis)?|risotto|kartoffeln?|kartoffelpüree|kartoffelspalten|erdäpfeln?|erdäpfelpüree|püree|pueree|gnocchi|spätzle|nockerl|couscous|bulgur|quinoa|pommes|rösti|knödeln?|polenta|tarhonya)\b',re.I)
def component_name(nm):
    nm=nm or ''; m=COMPONENT.search(nm)
    if not m: return False
    ws=m.start()
    while ws>0 and nm[ws-1].isalnum(): ws-=1
    we=m.end()
    while we<len(nm) and nm[we].isalnum(): we+=1
    return not any(c.end()<=ws or c.start()>=we for c in CARB_WORD.finditer(nm))
# Sensecheck 13: oven fish with sauce/topping but no side (Iglo Polar-Dorsch Mediterrane/Serbische Art/Müllerin, Schlemmerfilet,
#  Filegro, Ofenfisch) is a protein component ('Zum Kombinieren'), like breaded fish (sc11) — not a complete ready meal.
TOPPED_FISH = re.compile(r'schlemmerfilet|ofenfisch|filegro|\b(polar.?dorsch|seelachs\w*|alaska.?seelachs\w*|kabeljau|dorsch|lachsfilet|fischfilet|pangasius\w*|zander\w*)\b.*\b(art|müllerin|bordelaise|mexicana|toscana|kräuter\w*|gratin|champignon|broccoli|brokkoli|provence|italiana|limone|zitrone|rotes curry)\b',re.I)
NOT_COMPONENT_DISH = re.compile(r'pizza|burger|wrap|sandwich|baguette|bowl|salat|salad|suppe|menü|teller|eintopf|lasagne|bolognese|pfanne|gemüse',re.I)
def topped_fish(nm): return bool(TOPPED_FISH.search(nm or '')) and not CARB_WORD.search(nm or '') and not NOT_COMPONENT_DISH.search(nm or '')
# Sensecheck 13: pure Planted meat-substitute pieces ('Chicken Kräuter & Zitrone' 160 g, Steak, Kebab) are components; Planted inside
#  a dish (Juit 'Planted Chicken BBQ' 500 g, PrepMyMeal 'Planted Grünes Curry', BILLA 'Wrap Gyros Planted') stays a meal.
def meat_sub_piece(nm, brand='', size=None):
    t=(nm or '')+' '+(brand or '')
    if not re.search(r'\bplanted\b',t,re.I): return False
    if CARB_WORD.search(nm or '') or NOT_COMPONENT_DISH.search(nm or '') or re.search(r'curry|kebab-style|gyros|chili|risotto|ragout|tajine',nm or '',re.I): return False
    try: sz=float(size) if size not in (None,'') else None
    except (TypeError,ValueError): sz=None
    return sz is None or sz<=300

# Sensecheck 13 review (D/A): plain meat/fish pieces without own carb word are components ('Zum Kombinieren'), also as word part
#  ('Rindsbackerl Sous Vide', 'Schweinsbraten', 'Spareripperl'); Iglo Goldschatz = overbaked fish fillet line.
MEAT_PIECE = re.compile(r'sous.?vide|braten(?!wurst|sauce|soße|saft)|backerl|wangerl|ripperl|stelze|filet|steak|medaillon|goldschatz',re.I)
MEAT_PIECE_DISH = re.compile(r'gulasch|curry|chili|ragout|ragù|eintopf|geschnetzel|frikassee|tajine|stroganoff|teriyaki|süß.?sauer|tikka|masala|pfanne|knödel|semmel|nudel|reis|kartoffel|erdäpfel|tarhonya|spiralen|\bdazu\b|sauerkraut|rotkraut|blaukraut|bohnen|fisolen|spätzle|püree',re.I)
def meat_piece(nm):
    nm=nm or ''
    if not MEAT_PIECE.search(nm) or re.search(r'\bgebraten',nm,re.I) and not re.search(r'braten\b',nm,re.I): return False
    return not CARB_WORD.search(nm) and not NOT_COMPONENT_DISH.search(nm) and not MEAT_PIECE_DISH.search(nm)
# Review 13 (B): multi-piece fillet packs → portion = piece weight × 2, same for every size of the line.
PIECE_LINE = {'goldschatz': 100}
def piece_portion(nm, sz):
    nm=(nm or '').lower()
    for k,w in PIECE_LINE.items():
        if k in nm: return 2*w
    m=re.search(r'(\d+)\s*(stück|stk)\b',nm)
    if m and sz and int(m.group(1))>=3 and re.search(r'filet|schlemmer|dorsch|schnitzel|cordon|goldschatz|laibchen',nm): return round(sz/int(m.group(1))*2)
    return None
# Review 13 (E): age statement / OFF baby category → baby_food
AGE = re.compile(r'\bab\s+(dem\s+)?\d{1,2}\.?\s*(monat|monate|monaten)\b|altersstufe',re.I)
def baby_age(text, off_cats=''):
    return bool(AGE.search(text or '')) or 'en:baby-food' in (off_cats or '')
def _npkey(nm, sz=None):
    k=re.sub(r'^.*?natur\*?\s?pur\s*','',(nm or '').lower()); k=re.sub(r'\s*\d+\s*g\b','',k); k=re.sub(r'[^a-z0-9äöüß]+','',k)
    try: return (k, int(round(float(sz)))) if sz is not None else k
    except (TypeError,ValueError): return k
def _load_spar_baby():
    try:
        J=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'spar_baby_menus.json')))
    except Exception: return set(), set()
    full=set(); names=set()
    for it in J.get('items',[]):
        m=re.search(r'(\d+)\s*G',str(it.get('pack') or ''),re.I)
        names.add(_npkey(it['name']))
        if m: full.add(_npkey(it['name'],m.group(1)))
    return full, names
SPAR_BABY, SPAR_BABY_NAMES = _load_spar_baby()
def naturpur_baby(nm, sz, price):
    """(is_baby, verified). Verified = listed in SPAR category 'Babynahrung & Getränke|Baby|Menüs' (spar_baby_menus.json,
    search-spar API 16.10.; Bolognese 190/220 g also 'ab 5/8 Monate' on interspar.at). Otherwise heuristic: Natur*pur Bio-
    jar ≤250 g and ≤1.50 € = suspect (flag 'Verdacht'). Review 14: the blanket risotto exclusion (orch 17:41) dropped the
    verified baby jar Bio-Gemüse-Risotto 250 g/1,35 €; Steinpilz-/Tomaten-Risotto 2,49 € (SPAR: Reis|Rundkornreis) fail the price rule anyway."""
    nm=nm or ''
    if not re.search(r'natur\*?\s?pur\b.*\bbio-',nm,re.I): return (False,False)
    if _npkey(nm,sz) in SPAR_BABY: return (True,True)
    if re.search(r'steinpilz-risotto|tomaten-risotto',nm,re.I): return (False,False)
    try: sz=float(sz); price=float(price)
    except (TypeError,ValueError): return (False,False)
    if not (sz<=250 and price<=1.50): return (False,False)
    return (True, _npkey(nm) in SPAR_BABY_NAMES)
