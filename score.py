import json,re,statistics as st
import os
src=(['expand.json'] if os.path.exists('expand.json') else [])+(['classics.json'] if os.path.exists('classics.json') else [])+(['classics_ext.json'] if os.path.exists('classics_ext.json') else [])+(['brandfam_products.json'] if os.path.exists('brandfam_products.json') else [])+['billa.json','spar.json','spar_live.json','hofer_lidl.json','hofer_goodchoice.json','dm_live.json','frozen_quick.json','other.json','spar_browser_norm.json','more_meals_norm.json']+(['connectors_new.json'] if os.path.exists('connectors_new.json') else [])+(['online_mealprep.json'] if os.path.exists('online_mealprep.json') else [])+(['expand_v5.json'] if os.path.exists('expand_v5.json') else [])+(['hofer_off_meals.json'] if os.path.exists('hofer_off_meals.json') else [])+(['mpreis_new_2026-10-13.json'] if os.path.exists('mpreis_new_2026-10-13.json') else [])+(['ownbrands_meals.json'] if os.path.exists('ownbrands_meals.json') else [])+(['linz_providers_src.json'] if os.path.exists('linz_providers_src.json') else [])+(['mealkits_src.json'] if os.path.exists('mealkits_src.json') else [])
LIVE=('spar_live.json','dm_live.json')
items=[]
for f in src:
    try: d=json.load(open(f))
    except Exception as e: print('skip',f,e); continue
    d=d if isinstance(d,list) else d.get('products',[])
    for x in d:
        x=dict(x); x['source_file']=f
        if f=='spar_live.json': x.setdefault('store','INTERSPAR (live)')
        items.append(x)
def n(v):
    try: return float(v)
    except: return None
def _store_key(x):
    s=str(x.get('store') or '').lower()
    for a,b in (('gurkerl','gurkerl'),('interspar','spar'),('spar','spar'),('billa','billa'),('merkur','billa'),('hofer','hofer'),('aldi','hofer'),('lidl','lidl'),('penny','penny'),('dm','dm'),('mpreis','mpreis'),('prepmymeal','prepmymeal'),('livefresh','livefresh'),('fit to go','fit2go'),('fittaste','fittaste'),('nordsee','nordsee'),('subway','subway')):
        if a in s: return b
    return s or 'unk'
def key(x):
    # 2026-10-13T13: include store so same product at Billa/Spar/Gurkerl stays as separate rows (feeds PriceCompare / Dashboard 'Gleiches Produkt')
    k=re.sub(r'[^a-z0-9]','',re.sub(r'\s\d+\s?(g|kg|ml)\s*$','',(x.get('name') or '').lower().strip()))
    return (k, round(n(x.get('size_g')) or 0), _store_key(x))
cnt=lambda x: sum(v is not None for v in x.values())
best={}
for x in items:
    k=key(x)
    if k not in best: best[k]=x
    else:
        a=best[k]
        if x['source_file'] in LIVE:  # live overrides
            for kk,v in x.items():
                if v is not None: a[kk]=v
        else:
            for kk,v in x.items():
                if a.get(kk) is None and v is not None: a[kk]=v
items=list(best.values())
# apply_fixes: QA-Korrekturen
import glob
DERIVED={'dry','is_meal','price_status','protein_pack','kcal_pack','store'}
def apply_fixes(items):
    st={'files':0,'fixes':0,'applied':0,'by_field':{},'by_file':{}}
    byurl={x.get('url'):x for x in items if x.get('url')}; byname={(x.get('name') or '').strip().lower():x for x in items}
    for f in sorted(glob.glob('qa/*_fixes.json')):
        try: L=json.load(open(f))
        except Exception: continue
        L=L if isinstance(L,list) else L.get('fixes',[])
        st['files']+=1; k=f.split('/')[-1]; st['by_file'][k]={'fixes':len(L),'applied':0}
        for fx in L:
            st['fixes']+=1
            t=byurl.get(fx.get('url')) or byurl.get(fx.get('id')) or byname.get(str(fx.get('name') or fx.get('id') or '').strip().lower())
            fld=fx.get('field')
            if not t or not fld: continue
            if fld=='exclude' or fx.get('new')=='__exclude__': t['_excluded']=True
            else:
                t[fld]=fx.get('new')
                if fld in DERIVED: t.setdefault('_ov',{})[fld]=fx.get('new')
            t.setdefault('qa_fixes',[]).append({'field':fld,'old':fx.get('old'),'new':fx.get('new'),'reason':fx.get('reason')})
            st['applied']+=1; st['by_field'][fld]=st['by_field'].get(fld,0)+1; st['by_file'][k]['applied']+=1
    json.dump(st,open('qa_stats.json','w'),ensure_ascii=False,indent=1)
    return [x for x in items if not x.get('_excluded')]
items=apply_fixes(items)
# Hofer fill overlay (hofer.at product pages / OFF Hofer store tag / heisse-preise; see hofer_full/fill.py)
if os.path.exists("hofer_fill_2026-10-13.json"):
    _HF={re.sub(r"[^a-z0-9]+","",(f.get("app_name") or "").lower()):f for f in json.load(open("hofer_fill_2026-10-13.json"))}
    for x in items:
        if not re.search(r"hofer",str(x.get("store") or ""),re.I): continue
        f=_HF.get(re.sub(r"[^a-z0-9]+","",(x.get("name") or "").lower()))
        if not f: continue
        for k in ("price_eur","size_g","price_per_kg","price_source","price_date","image_url","ingredients","allergens","kcal_100","protein_100","fat_100","satfat_100","carbs_100","sugar_100","fiber_100","salt_100","nutriscore"):
            if f.get(k) is not None and x.get(k) in (None,"",[]):
                x[k]=f[k]
        if f.get("price_old"): x.setdefault("notes",""); x["price_live"]=False
# Schweiz-only Good Choice (Open Food Facts countries_tags nur switzerland)
CH={'4099200420783','4099200422855','4061459487848'}
def ean(x):
    m=re.search(r'product/(\d{8,14})',str(x.get('url'))+str(x.get('off_url'))); return x.get('ean') or (m and m.group(1))
excluded=[x['name'] for x in items if ean(x) in CH]
items=[x for x in items if ean(x) not in CH]
# SPAR live overlay (food-connectors spar-shop: public SPAR search API, exact article number; see fertiggerichte-daten/raw/spar_live_*.json)
if os.path.exists("spar_live_overlay.json"):
    _SL=json.load(open("spar_live_overlay.json")).get("articles",{})
    def _g(s):
        m=re.search(r"(\d+(?:[.,]\d+)?)\s*(G|KG|ML|L)\b",str(s or "").upper())
        return None if not m else float(m.group(1).replace(",","."))*(1000 if m.group(2) in("KG","L") else 1)
    _spar_live_stats={"applied":0,"size_mismatch":[]}
    for x in items:
        if "spar" not in str(x.get("store") or "").lower(): continue
        m=re.search(r"/p/(\d{4,})",str(x.get("url") or "")) or re.search(r"articleImage\.dam/at/(\d{4,})/",str(x.get("image_url") or ""))
        o=_SL.get(m.group(1)) if m else None
        if not o and not m:
            o=next((v for v in _SL.values() if re.sub(r"[^a-z0-9]","",(v.get("spar_name") or "").lower())==re.sub(r"[^a-z0-9]","",(x.get("name") or "").lower())),None)
        if not o or not o.get("price_eur"): continue
        g=_g(o.get("pack"))
        if g and x.get("size_g") and abs(g-float(x["size_g"]))/float(x["size_g"])>0.05:
            _spar_live_stats["size_mismatch"].append({"name":x.get("name"),"size_g":x.get("size_g"),"spar_pack":o.get("pack")}); continue
        x["price_eur"]=o["price_eur"]; x["price_source"]=o["price_source"].split(", Artikel")[0]+")"; x["price_date"]=o["fetched_at"][:10]
        x["price_live"]=True; x["spar_article"]=m.group(1) if m else None
        if o.get("regular_price_eur") and o["regular_price_eur"]!=o["price_eur"]: x["price_regular_eur"]=o["regular_price_eur"]
        if o.get("unit")=="kg" and o.get("price_per_unit"): x["price_per_kg"]=o["price_per_unit"]
        if not x.get("size_g") and g: x["size_g"]=g
        _spar_live_stats["applied"]+=1
    json.dump(_spar_live_stats,open("spar_live_stats.json","w"),ensure_ascii=False,indent=1)
# PENNY live overlay (food-connectors penny-shop: penny.at public online-assortment JSON; see fertiggerichte-daten/raw/penny_*.json)
if os.path.exists("penny_live_overlay.json"):
    _PL=json.load(open("penny_live_overlay.json")).get("articles",{})
    _penny_live_stats={"applied":0,"size_mismatch":[]}
    for x in items:
        if "penny" not in str(x.get("store") or "").lower(): continue
        m=re.search(r"penny\.at/produkte/[^?#]*-78(\d{5,7})\b",str(x.get("url") or ""))
        o=_PL.get(m.group(1)) if m else None
        if not o or not o.get("price_eur"): continue
        g=parse_g(o.get("pack")) if "parse_g" in globals() else None
        if g is None:
            mm=re.search(r"(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l)\b",str(o.get("pack") or "").lower())
            g=None if not mm else float(mm.group(1).replace(",","."))*(1000 if mm.group(2) in("kg","l") else 1)
        if g and x.get("size_g") and abs(g-float(x["size_g"]))/float(x["size_g"])>0.05:
            _penny_live_stats["size_mismatch"].append({"name":x.get("name"),"size_g":x.get("size_g"),"penny_pack":o.get("pack")}); continue
        x["price_eur"]=o["price_eur"]; x["price_source"]=o["price_source"]; x["price_date"]=o["fetched_at"][:10]; x["price_live"]=True
        x["penny_article"]=m.group(1)
        if o.get("price_regular_eur"): x["price_regular_eur"]=o["price_regular_eur"]
        if o.get("offer_price_eur"): x["offer_price_eur"]=o["offer_price_eur"]; x["offer_text"]=o.get("offer_text")
        if o.get("price_per_kg"): x["price_per_kg"]=o["price_per_kg"]
        if not x.get("image_url") and o.get("image_url"): x["image_url"]=o["image_url"]
        if not x.get("size_g") and g: x["size_g"]=g
        _penny_live_stats["applied"]+=1
    json.dump(_penny_live_stats,open("penny_live_stats.json","w"),ensure_ascii=False,indent=1)
# OFF-only store overlay (exact GTIN = OFF barcode vs. food-connectors gurkerl / mpreis-shop / dm; see fertiggerichte-daten/raw/offonly_match_*.json)
# + drop store-less OFF rows whose barcode already exists as a store row (same product twice)
if os.path.exists("offonly_store_overlay.json"):
    _OO=json.load(open("offonly_store_overlay.json")).get("articles",{})
    _oo_stats={"applied":0,"dup_dropped":[],"size_mismatch":[]}
    _se={str(ean(x)).lstrip("0") for x in items if x.get("store") and ean(x)}
    _su={x.get("url"):x for x in items if x.get("store") and x.get("url")}
    _keep=[]
    for x in items:
        if not x.get("store") and ean(x):
            k=str(ean(x)).lstrip("0")
            if k in _se: _oo_stats["dup_dropped"].append(x.get("name")); continue
            o=_OO.get(k)
            if o and o.get("url") in _su:  # store row for this GTIN already exists (store rows often carry no ean) -> fill gaps, drop OFF twin
                t=_su[o["url"]]
                for kk,v in x.items():
                    if t.get(kk) in (None,"",[]) and v not in (None,"",[]) and kk not in ("store","url","price_eur","price_source","price_date","source_file","name","brand","size_g"): t[kk]=v
                t["ean"]=t.get("ean") or k; _oo_stats["dup_dropped"].append(x.get("name")+" (=store url)"); continue
            if o and o.get("price_eur"):
                if o.get("size_g") and x.get("size_g") and abs(float(o["size_g"])-float(x["size_g"]))/float(x["size_g"])>0.05:
                    _oo_stats["size_mismatch"].append({"name":x.get("name"),"size_g":x.get("size_g"),"store_size":o.get("size_g")})
                    x["size_g"]=o["size_g"]  # same GTIN -> store pack size is authoritative (OFF size often per portion)
                x["store"]=o["store"]; x["price_eur"]=o["price_eur"]; x["price_date"]=o["fetched_at"][:10]; x["price_live"]=True
                x["price_source"]=f"{o['store']} live {o['fetched_at'][:10]} (food-connectors, GTIN {k})"
                x["off_url"]=x.get("off_url") or x.get("url"); x["url"]=o["url"]; x["ean"]=x.get("ean") or k; x["store_match"]="gtin-exact"
                if not x.get("image_url") and o.get("image_url"): x["image_url"]=o["image_url"]
                if not x.get("size_g") and o.get("size_g"): x["size_g"]=o["size_g"]
                if x.get("size_g") and x.get("price_eur"): x["price_per_kg"]=round(x["price_eur"]/float(x["size_g"])*1000,2)
                _oo_stats["applied"]+=1
        _keep.append(x)
    items=_keep
    json.dump(_oo_stats,open("offonly_store_stats.json","w"),ensure_ascii=False,indent=1)
# OFF–OFF same-GTIN collapse (two store-less OFF rows, same barcode → keep richest nutrition)
_oo2={"dropped":[]}
_seen_ean={}; _keep2=[]
for x in items:
    if (not x.get("store") or str(x.get("store")).lower().startswith("unbekannt")) and ean(x):
        k=str(ean(x)).lstrip("0")
        if k in _seen_ean:
            prev=_seen_ean[k]
            def _rich(z): return sum(z.get(f) is not None for f in ("kcal_100","protein_100","fat_100","size_g","image_url"))
            if _rich(x)>_rich(prev):
                _oo2["dropped"].append(prev.get("name")); _keep2=[y for y in _keep2 if y is not prev]; _seen_ean[k]=x; _keep2.append(x)
            else:
                _oo2["dropped"].append(x.get("name"))
            continue
        _seen_ean[k]=x
    _keep2.append(x)
if _oo2["dropped"]:
    items=_keep2
    _oo_stats["off_off_dropped"]=_oo2["dropped"]
    json.dump(_oo_stats,open("offonly_store_stats.json","w"),ensure_ascii=False,indent=1)
# Preise: live vs. alt
for x in items:
    ps=str(x.get('price_source') or '')+str(x.get('price_date') or '')
    if not x.get('price_eur'): x['price_status']=None
    elif re.search(r'2025|Altpreis|kein aktueller',ps): x['price_status']='Preis 2025'
    elif x.get('price_live') is False and x['source_file'] in('hofer_lidl.json','hofer_goodchoice.json'): x['price_status']='Preis unbestätigt'
    else: x['price_status']='live 2026'
# Hersteller-Join
P=json.load(open('producers_resolved.json'))['producers']
normid=lambda c: re.sub(r'[^A-Z0-9]','',str(c).upper().replace('EU','EG')) if c else None
PM={normid(p['code']):p for p in P if p.get('code')}
for x in items:
    p=PM.get(normid(x.get('producer_id')))
    if p:
        x['producer_company']=p.get('company'); x['producer_town']=p.get('town'); x['producer_state']=p.get('state')
    x['ooe']= bool(p and p.get('state')=='Oberösterreich') or bool(re.search(r'\b4\d{3} ',str(x.get('manufacturer') or '')))
json.dump(excluded,open('excluded_ch.json','w'),ensure_ascii=False)
NONMEAL=re.compile(r'ramyun|instant ?nudel|crème brûlée|brûlée|lavakuchen|toastkäse|protein ?brot|eiweißbrot|wurstsalat|topfencreme|protein ?mousse|mousse\b|pudding|dessert|cheesecake|tiramisu|panna cotta|^(?!.*(ravioli|tortell|nudel|pasta|gnocchi|spaghetti|penne|lasagne|\bmit\b)).*\b(pesto|sugo)\b|suppeneinlage|backerbsen|frittaten|suppe-(abc|gerstl|sternderl|mini hörnchen)|leberknödel einlage|^\S+ lasagne$|lasagne hartweizen|teigblätter|lasagne-blätter|lasagneblätter|pasta per lasagne|teig\b|strudelteig|pizzateig|blätterteig|hummus|bruschetta|sandwich|streufertig|paste\b|currypaste|lasagneblätter|lasagne teig|lasagneblätter|bio-dinkel lasagne$|^curry$|drink|tuc|teigbl|lasagneblätter|(?<!fish & )chips|keks|cracker|müsli|joghurt|milch\b|aufstrich|sirup|getränk|schokolade',re.I)
def classify(x):
    t=' '.join(str(x.get(k) or '') for k in ['category','name','prep','brand']).lower()
    nm=(x.get('name') or '').lower(); cat=(x.get('category') or '').lower()
    pk=(x.get('packaging_raw') or '').lower()
    if pk:
        if pk.startswith('tk'): return 'Tiefkühl (TK)'
        if pk.startswith('dose'): return 'Dose/Konserve'
        if pk.startswith('trocken'): return 'Trocken/Instant'
        if pk.startswith('kühl'): return 'Kühlregal (Menüschale/frisch)'
    if 'sous' in t and 'vide' in t: return 'Sous-vide (vakuum)'
    if cat.startswith('frozen') or re.search(r'iglo|curly fries|nuggets|cordon bleu|tiefk|\btk\b|gefror|frozen|tiefgek',t) or x.get('source_file')=='ftg_items.json': return 'Tiefkühl (TK)'
    if re.search(r'\bglas\b|im glas|einmach',t): return 'Glas'
    if re.search(r'instant|5 ?min|terrine|cup|becher|pulver|trocken|beutelsuppe|fix für|nudelsnack|ramen|noodle',nm) or 'instant' in cat: return 'Trocken/Instant'
    if re.search(r'little lunch|langbein|steirerkraft|auinger|im glas',t): return 'Glas'
    if re.search(r'mikrowell|pouch',nm): return 'Beutel ungekühlt (Retort-Pouch)'
    if cat=='beutel' or re.search(r'knorr|maggi|kochbeutel|bouillon|\bfix\b|clever (nudel|buchstaben)suppe|vorratsschrank',t): return 'Trocken/Instant'
    if re.search(r'dosensuppe|konserv|\bdose\b',t): return 'Dose/Konserve'
    if cat=='dose' or re.search(r'\bdose\b|konserve|inzersdorfer|eintopf|ravioli in|s-budget rindsgulasch|chili con carne|erasco|sonnen bassermann',t): return 'Dose/Konserve'
    if cat=='beutel' or 'ungekühlt' in cat or re.search(r'beutel|pouch|mikrowellen',t): return 'Beutel ungekühlt (Retort-Pouch)'
    if cat.startswith('fertiggerichte gek') or cat in ('menüschalen','frische pasta & beilagen','asien','suppen') or re.search(r'good choice|omis|menü|schale|gekühlt|frisch|kühl',t) or cat in('ready_meal','dumpling','fish','leberkaese','breaded','marinated','skewer','ribs','sausage','raw_meat'):
        return 'Kühlregal (Menüschale/frisch)'
    if x.get('source_file') in ('frozen_quick.json',): return 'Kühlregal (Menüschale/frisch)'
    return 'Unklar (keine Lagerangabe)'
NOVA={'Dose/Konserve':4,'Trocken/Instant':4,'Beutel ungekühlt (Retort-Pouch)':4,'Tiefkühl (TK)':3.5,'Kühlregal (Menüschale/frisch)':3.5,'Glas':3.5,'Sous-vide (vakuum)':3,'Unklar (keine Lagerangabe)':3.5}
RAW=re.compile(r'ripperl|spieß|spiess|filet|marinier|roh|natur\b',re.I)
def score(x):
    p,k,s,sf,fi=(n(x.get(a)) for a in ['protein_100','kcal_100','salt_100','satfat_100','fiber_100'])
    if p is None or k is None or k<=0: return None
    pd=p/k*100  # g protein per 100 kcal
    s_prot=min(pd/10,1)*40                     # 10 g/100 kcal = Maximum
    s_salt=0 if s is None else -min(max(s-0.6,0)/1.4,1)*20   # ab 0,6 g; 2,0 g = -20
    s_sat=0 if sf is None else -min(max(sf-1.5,0)/4.5,1)*15  # ab 1,5 g; 6 g = -15
    veg=bool(re.search(r'gemüse|linsen|bohnen|kichererb|spinat|brokkoli|curry|chili|erbsen|paprika|kürbis',(x.get('name') or '').lower()))
    s_fib=(min(fi/6,1)*15 if fi is not None else 0)+(5 if veg else 0)
    nova=NOVA[x['packaging']]
    if RAW.search(x.get('name') or '') and x['packaging']!='Dose/Konserve': nova=min(nova,3)
    s_proc=-(nova-3)*10                         # NOVA 3 → 0, 4 → -10
    sc=30+s_prot+s_salt+s_sat+s_fib+s_proc
    return round(max(0,min(100,sc)),1)
out=[]
for x in items:
    if x.get('packaging') and 'packaging_raw' not in x: x['packaging_raw']=x['packaging']
    x['packaging']=classify(x)
    x['is_meal']=not NONMEAL.search(x.get('name') or '')
    flags=[]
    kc0=n(x.get('kcal_100'))
    x['dry']= x['packaging']=='Trocken/Instant' or bool(kc0 and kc0>300 and re.search(r'soja geschnetzel|sojaschnetzel|pulver|terrine|fix\b|bouillon',x.get('name') or '',re.I))
    pr0,ppk0,sz0=n(x.get('price_eur')),n(x.get('price_per_kg')),n(x.get('size_g'))
    if pr0 and ppk0 and sz0 and not x['dry']:
        imp=pr0/ppk0*1000
        if 0.25<abs(imp-sz0)/sz0 and imp/sz0<5:
            x['size_g_original']=sz0; x['size_g']=round(imp); flags.append(f'Packgröße korrigiert ({sz0:g} g → {imp:.0f} g aus €/kg)')
            if n(x.get('protein_100')) is not None: x['protein_pack']=round(n(x['protein_100'])*imp/100,1)
            if n(x.get('kcal_100')) is not None: x['kcal_pack']=round(n(x['kcal_100'])*imp/100)
    if not x['dry'] and kc0 and kc0>=300 and (n(x.get('fat_100')) or 0)<10 and x['packaging']!='Tiefkühl (TK)': x['dry']=True
    if x['dry']: flags.append('Trockenprodukt: Nährwerte pro 100 g trocken, nicht in Rankings')
    pp0=n(x.get('protein_pack'))
    if pp0 and pp0>100: flags.append('Großpackung (>100 g Protein/Pkg), Protein/€ nicht mit Einzelportionen vergleichbar')
    x['incomplete']= n(x.get('salt_100')) is None or n(x.get('satfat_100')) is None
    if x['incomplete']: flags.append('Score unvollständig (Salz oder ges. Fett fehlt)')
    x['flags']=flags
    x['rankable']= not x['dry'] and not x['incomplete'] and not (pp0 and pp0>100)
    p,pr,sz=n(x.get('protein_100')),n(x.get('price_eur')),n(x.get('size_g'))
    if not x.get('price_per_kg') and pr and sz: x['price_per_kg']=round(pr/sz*1000,2)
    pp=n(x.get('protein_pack')) or (p*sz/100 if p is not None and sz else None)
    x['protein_per_euro']=round(pp/pr,2) if pp and pr else None
    x['price_per_10g_protein']=round(pr/pp*10,2) if pp and pr else None
    x['protein_per_100kcal']=round(p/n(x['kcal_100'])*100,2) if p is not None and n(x.get('kcal_100')) else None
    x['health_score']=score(x)
    ov=x.get('_ov') or {}
    for k,v in ov.items(): x[k]=v
    if 'dry' in ov:
        x['flags']=[f for f in x['flags'] if not f.startswith('Trockenprodukt')]+(['Trockenprodukt: Nährwerte pro 100 g trocken, nicht in Rankings'] if x['dry'] else [])
    pp0=n(x.get('protein_pack'))
    x['offOnly']= (not x.get('store') or 'openfoodfacts' in str(x.get('url'))) and not x.get('price_eur')
    if x['offOnly']: x['flags'].append('nur Open Food Facts, kein Laden/Preis – nicht in Rankings')
    x['rankable']= not x['dry'] and not x['incomplete'] and not (pp0 and pp0>100) and not x['offOnly'] and x.get('is_meal',True)
    out.append(x)
# dish_key (classics view)
try:
    import sys as _s; _s.path.insert(0,'classics'); from dishes import dish as _dish, LABEL as _DL
    for _x in out:
        _k=_x.get('dish_key') or _dish(_x.get('name'))
        _x['dish_key']=_k; _x['dish']=_DL.get(_k) if _k else None
except Exception as _e: print('dish_key failed',_e)
# nutri_enrich.json (food-connectors nutri): Nutri-Score offiziell/berechnet, NOVA, Zusatzstoffe, Eco-Score
try:
    _NE=json.load(open('nutri_enrich.json'))['by_key']
    for _x in out:
        _e=_NE.get(_x.get('url') or _x.get('name'))
        if not _e: continue
        for _f in ('nutriscore','nutriscore_status','nutriscore_source','nutriscore_computed','nova','nova_source','additives','ecoscore','ingredients_analysis'):
            if _f in _e: _x[_f]=_e[_f]
except Exception as _e: print('nutri_enrich skipped',_e)
# Markenfamilien (brand_families.json): brand_family / sub_brand taggen
try:
    _BF=json.load(open('brand_families.json'))['families']
    _CH={'BILLA':'BILLA','HOFER':'HOFER','SPAR':'SPAR','INTERSPAR':'SPAR','LIDL':'LIDL','PENNY':'PENNY'}
    for _x in out:
        _st=_CH.get(re.sub(r'\s*\(.*','',str(_x.get('store') or '')).upper())
        _t=' '.join(str(_x.get(k) or '') for k in ('brand','name'))
        for _f in _BF:
            if _x.get('sub_brand') and _x.get('brand_family'): break
            if _st and _f['chain']!=_st: continue
            for _s in _f['sub_brands']:
                if re.search(_s['pattern'],str(_x.get('brand') or ''),re.I) or re.search(_s['pattern'],str(_x.get('name') or ''),re.I):
                    _x['brand_family']=_f['chain']; _x['sub_brand']=_s['name']; break
except Exception as _e: print('brand_families failed',_e)

# Spar CDN overlay (heisse→cdn1.interspar.at, verified; see fertiggerichte-daten/raw/spar_cdn_images_*.json)
if os.path.exists("spar_cdn_overlay.json"):
    _ov = {re.sub(r"[^a-z0-9]+", "", (x.get("name") or "").lower()): x["image_url"]
           for x in json.load(open("spar_cdn_overlay.json")).get("images", []) if x.get("image_url")}
    for x in out:
        if re.search(r"spar", str(x.get("store") or ""), re.I) and not x.get("image_url"):
            u = _ov.get(re.sub(r"[^a-z0-9]+", "", (x.get("name") or "").lower()))
            if u: x["image_url"] = u

# Hofer OFF/Aldi overlay (strict match; see fertiggerichte-daten/raw/hofer_images_*.json)
if os.path.exists("hofer_images_overlay.json"):
    _hov = {re.sub(r"[^a-z0-9]+", "", (x.get("name") or "").lower()): x["image_url"]
            for x in json.load(open("hofer_images_overlay.json")).get("images", []) if x.get("image_url")}
    for x in out:
        if re.search(r"hofer", str(x.get("store") or ""), re.I) and not x.get("image_url"):
            u = _hov.get(re.sub(r"[^a-z0-9]+", "", (x.get("name") or "").lower()))
            if u: x["image_url"] = u

# dm overlay (dm.at product JSON / Lotao Shopify / OFF strict; see fertiggerichte-daten/raw/dm_images_*.json)
if os.path.exists("dm_images_overlay.json"):
    _dov = {re.sub(r"[^a-z0-9]+", "", (x.get("name") or "").lower()): x["image_url"]
            for x in json.load(open("dm_images_overlay.json")).get("images", []) if x.get("image_url")}
    for x in out:
        if str(x.get("store") or "").strip().lower() == "dm" and not x.get("image_url"):
            u = _dov.get(re.sub(r"[^a-z0-9]+", "", (x.get("name") or "").lower()))
            if u: x["image_url"] = u

# --- score v2 (analysis/score_v2.md) ---
import score_v2 as _V2
_OFF=_V2.load_off()
for x in out:
    _e=str(ean(x) or '')
    r2=_V2.score_v2(x,_OFF.get(_e))
    x['health_score_v1']=x.get('health_score')
    x.update(r2)
    if x['nutrition_basis']=='dry':
        if x.get('_ov',{}).get('dry') is False: x['flags'].append('QA-Override dry=False ignoriert (Nährwerte trocken)')
        x['dry']=True
        if not any(f.startswith('Trockenprodukt') for f in x['flags']): x['flags'].append('Trockenprodukt: Nährwerte pro 100 g trocken, nicht in Rankings')
    elif x['nutrition_basis']=='prepared': x['dry']=False; x['flags'].append('Nährwerte auf zubereitet umgerechnet ('+(x.get('nutrition_note') or '')+')')
    if False: x['flags'].append(f"Mahlzeit-Check: {x['kcal_meal']} kcal/Portion – Snack/Beilage, keine Mahlzeit" if x['meal_class']=='snack_side' else f"Mahlzeit-Check: nur {x['kcal_meal']} kcal – leichte Mahlzeit")
    _des,_gro=_V2.labels(x)
    if _des: x['gang']='dessert'; x['flags'].append('Dessert – nicht in Rankings')
    if _gro and x.get('segment')!='meal_kit': x['segment']='grocery'; x['flags'].append('Lebensmittel (kein Fertiggericht) – nicht in Rankings')
    _mc=_V2.meal_check(x,r2); x['meal_check']=_mc; x['meal_class']=_mc['cls'] if not _des else 'dessert'
    if re.search(r'hipp|beba|aptamil|alete|babylove|ab dem \d|kleinkind|säugling|\bbaby\b|kinder ?menü|bio-?gläschen',_nm,re.I): x['meal_class']='baby'; x['segment']='baby_food'; _mc['ok']=False; _mc['reason']='Kindernahrung'
    _nm=x.get('name') or ''
    if not _des and _V2.SNACK.search(_nm): x['meal_class']='snack_side'; _mc['ok']=False; _mc['reason']='Brot/Snack/Instant – keine Mahlzeit'
    x['component']=bool(_V2.COMPONENT.search(_nm)) and not _des
    if x['component']: _mc['ok']=False; _mc['reason']=(_mc.get('reason') or '')+' Proteinkomponente (keine vollständige Mahlzeit)'
    if not _mc['ok'] and _mc.get('reason'): x['flags'].append('Mahlzeit-Check: '+_mc['reason'])
    x['rankable']=bool(x['rankable']) and not x['dry'] and x['health_score'] is not None and _mc['ok'] and not _des and not _gro and x.get('is_meal',True)
for x in out:  # meal kits (cook-yourself boxes) are ranked separately from ready meals
    if x.get('segment')=='meal_kit': x['rankable_mealkit']=bool(x.get('rankable')); x['rankable']=False
json.dump(out,open('scored.json','w'),ensure_ascii=False,indent=1)
meals=[x for x in out if x['is_meal']]
types=sorted(set(x['packaging'] for x in meals))
def med(L,f):
    v=[n(x.get(f)) for x in L if n(x.get(f)) is not None]; return (round(st.median(v),2),len(v)) if v else (None,0)
F=['protein_100','protein_per_100kcal','salt_100','satfat_100','sugar_100','fiber_100','price_per_kg','price_per_10g_protein','health_score']
stats={}
for t in types:
    L=[x for x in meals if x['packaging']==t]; stats[t]={'n':len(L),**{f:med(L,f) for f in F}}
json.dump(stats,open('packaging_stats.json','w'),ensure_ascii=False,indent=1)
print(len(items),len(out),len(meals))
for t,s in stats.items(): print(t,s)
