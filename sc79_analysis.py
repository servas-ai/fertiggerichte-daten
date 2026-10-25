import collections
import glob
import json
import os
import re
import statistics as S


def _med(a):
    a = [x for x in a if x is not None]
    return round(S.median(a), 2) if a else None


def _mean(a):
    a = [x for x in a if x is not None]
    return round(S.mean(a), 2) if a else None


def _box(a):
    a = sorted(x for x in a if x is not None)
    if not a:
        return None
    if len(a) < 4:
        return dict(min=round(a[0], 2), q1=round(a[0], 2), median=round(S.median(a), 2), q3=round(a[-1], 2), max=round(a[-1], 2), mean=round(S.mean(a), 2), n=len(a))
    qs = S.quantiles(a, n=4)
    return dict(min=round(a[0], 2), q1=round(qs[0], 2), median=round(qs[1], 2), q3=round(qs[2], 2), max=round(a[-1], 2), mean=round(S.mean(a), 2), n=len(a))


def _q5(a):
    a = sorted(x for x in a if x is not None)
    if len(a) < 4:
        return None
    qs = S.quantiles(a, n=4)
    return [round(a[0], 2), round(qs[0], 2), round(qs[1], 2), round(qs[2], 2), round(a[-1], 2)]


def _slug(s):
    return re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-') or 'unbekannt'


def regenerate_all(can, base_dir):
    rows = can['rows']
    linz_rows = [
        dict(r) for r in rows
        if r.get('dupOf') is None
        and not r.get('nonfood')
        and r.get('delivers_4020') is not False
        and not str(r.get('store') or '').startswith('unbekannt')
    ]
    meal_rows = [
        r for r in linz_rows
        if r.get('stage') in ('meal', 'stew')
        and r.get('gang') != 'dessert'
    ]

    # Target directories to write analysis JSONs
    out_dirs = [os.path.join(base_dir, 'analysis')]
    app_analysis = '/workspace/fertig-app/public/analysis'
    if os.path.isdir(app_analysis):
        out_dirs.append(app_analysis)
    if os.environ.get('GOOD_CHOICE_ANALYSIS_DIR'):
        out_dirs = [os.environ['GOOD_CHOICE_ANALYSIS_DIR']]

    # =========================================================================
    # 1. packaging_v2.json
    # =========================================================================
    pkg_path = os.path.join(base_dir, 'analysis/packaging_v2.json')
    old_pkg = json.load(open(pkg_path)) if os.path.exists(pkg_path) else {}
    det = {}
    for fn in ('det.json', 'det2.json'):
        p = os.path.join(base_dir, fn)
        if os.path.exists(p):
            try:
                det.update({k: v for k, v in json.load(open(p)).items() if v})
            except Exception:
                pass

    T_PKG = ['Dose', 'Kühlschale/MAP', 'Tiefkühl', 'Pouch/Retort', 'Glas', 'Sous-vide/Vakuum', 'Trocken/Instant-Beutel']
    OLD_PKG = {
        'Dose/Konserve': 'Dose',
        'Kühlregal (Menüschale/frisch)': 'Kühlschale/MAP',
        'Tiefkühl (TK)': 'Tiefkühl',
        'Trocken/Instant': 'Trocken/Instant-Beutel',
        'Glas': 'Glas',
        'Sous-vide (vakuum)': 'Sous-vide/Vakuum',
        'Beutel ungekühlt (Retort-Pouch)': 'Pouch/Retort',
    }
    NAME_PKG = [
        (r'sous.?vide|vakuumgegart|niedertemperatur', 'Sous-vide/Vakuum', 'Name: Sous-vide'),
        (r'\btk\b|tiefgek|tiefkühl|eisknödel|\bfrosta\b|\biglo\b|\bfrost\b|pizza.*steinofen|ofenfrisch', 'Tiefkühl', 'Name/Marke: TK'),
        (r'\bdose\b|konserve|\binzersdorfer\b|\berasco\b|\bsonnen bassermann\b|\bhengstenberg\b|meisterkessel', 'Dose', 'Name/Marke: Dose'),
        (r'\bim glas\b|\bglas\b|\bgläschen\b', 'Glas', 'Name: Glas'),
        (r'express|microwave|mikrowellen.?beutel|pouch|\bready to eat\b|\bsnack pot\b|\blotao\b', 'Pouch/Retort', 'Name: Express/Pouch'),
        (r'5 minuten|terrine|fix für|\bfix\b|instant|cup|becher.*nudel|nudel.*becher|fertigmischung|pulver|für \d+ teller|teller\)|suppenwürfel|\bbrühe\b|magic asia|spaghetteria|\bpüree\b.*portionen|instant', 'Trocken/Instant-Beutel', 'Name: Instant/Trocken'),
        (r'good choice|menüschale|menü\b|frisch|tortell|ravioli|cappelletti|gnocchi frisch|salat\b|bowl|wrap|sandwich|youcook|feine küche|\bchef select\b|simply good|hilcona|cecchin|rana\b|capricci|la nova|\bager\b|radatz|tann\b|hütthaler|toni kaiser|spätzle fertig', 'Kühlschale/MAP', 'Name/Marke: Kühlregal'),
        (r'knödel|strudel|laibchen|samosas|gyoza|frühlingsrolle', 'Tiefkühl', 'Name: typ. TK-Ware (schwach)'),
    ]
    CAT_PKG = {
        'Menüschalen': 'Kühlschale/MAP',
        'Fertiggerichte Gekühlt': 'Kühlschale/MAP',
        'Fertiggerichte gekühlt': 'Kühlschale/MAP',
        'Frische Pasta & Beilagen': 'Kühlschale/MAP',
        'Frischer Teig & Pasta': 'Kühlschale/MAP',
        'Salate': 'Kühlschale/MAP',
        'Sandwiches & Co': 'Kühlschale/MAP',
        'Dose': 'Dose',
        'Beutel': 'Pouch/Retort',
        'Suppengewürze': 'Trocken/Instant-Beutel',
        'Basis- & Fixprodukte': 'Trocken/Instant-Beutel',
    }
    ADD_RX = re.compile(r'konservierungsstoff|verdickungsmittel|säuerungsmittel|säureregulator|emulgator|stabilisator|geschmacksverstärker|farbstoff|antioxidationsmittel|modifizierte stärke|backtriebmittel|feuchthaltemittel|\be ?\d{3}[a-z]?\b', re.I)

    def _sku(r):
        m = re.search(r'(\d{2})(\d{6})$', r.get('url') or '')
        return f'{m.group(1)}-{m.group(2)}' if m and 'billa' in (r.get('url') or '') else None

    def _classify_pkg(r):
        d = det.get(_sku(r) or '', {})
        st = (d.get('storageAndUsageStatements') or '')
        s = st.lower().split('nach dem öffnen')[0]
        pl = (d.get('packageLabel') or '')
        if re.search(r'-\s?18\s?°?c|tiefgekühlt|tiefkühl', s):
            return 'Tiefkühl', 'Etikett: −18 °C', st
        if pl == 'Dose':
            return 'Dose', 'Etikett: Verpackung Dose', st
        if pl == 'Glas':
            return 'Glas', 'Etikett: Verpackung Glas', st
        if re.search(r'\+?\s?[0-4]\s?°?c?\s?bis\s?\+?\s?[4-8]\s?°?c|gekühlt lagern|kühl lagern bei \+', s):
            if re.search(r'sous|vakuum', (r.get('name') or '').lower()):
                return 'Sous-vide/Vakuum', 'Etikett gekühlt + Name Sous-vide', st
            return 'Kühlschale/MAP', 'Etikett: gekühlt +2…+6 °C', st
        c = d.get('category')
        t = f"{r.get('name') or ''} {r.get('brandN') or r.get('brand') or ''}".lower()
        if c == 'Beutel' and (r.get('dry') or re.search(NAME_PKG[5][0], t) or re.search(r'suppe ?(abc|gerstl|sternderl|hörnchen|hoernchen)|einlage|nudeln', t)):
            return 'Trocken/Instant-Beutel', 'BILLA-Kategorie Beutel + Trockenware', st
        if c in CAT_PKG:
            return CAT_PKG[c], f'BILLA-Kategorie: {c}', st
        o = OLD_PKG.get(r.get('pack'))
        if 'meisterkessel' in t:
            return 'Dose', 'Marke: Knorr Meisterkessel (Dose)', st
        for rx, ty, why in NAME_PKG:
            if re.search(rx, t):
                if why.endswith('(schwach)') and o:
                    break
                return ty, why, st
        if o:
            return o, 'bisherige Einstufung (Shop-Rubrik)', st
        if d.get('category') == 'Fertiggerichte Ungekühlt':
            return 'Pouch/Retort', 'BILLA-Kategorie: ungekühlt (Schale/Pouch)', st
        return None, 'keine belastbaren Hinweise', st

    why_counts = {}
    for r in linz_rows:
        ty, w, st = _classify_pkg(r)
        d = det.get(_sku(r) or '', {})
        m = re.search(r'"ingredientsText": "((?:[^"\\]|\\.)*)"', json.dumps(d, ensure_ascii=False)) if d else None
        ing = m.group(1) if m else (r.get('ing') or '')
        r['_t'] = ty
        r['_w'] = w
        r['_st'] = st
        r['_add'] = len(set(x.lower() for x in ADD_RX.findall(ing))) if ing else (len(r['additives']) if r.get('additives') is not None else None)
        why_counts[w] = why_counts.get(w, 0) + 1

    moved = sum(1 for r in linz_rows if r.get('_t') and OLD_PKG.get(r.get('pack')) != r['_t'])
    ICON_PKG = {'Dose': '🥫', 'Kühlschale/MAP': '🍱', 'Tiefkühl': '❄️', 'Pouch/Retort': '🛍️', 'Glas': '🫙', 'Sous-vide/Vakuum': '🥩', 'Trocken/Instant-Beutel': '🍜'}
    MHD_PKG = {
        'Kühlschale/MAP': [5, 21, '5–21 Tage', 'vz'],
        'Sous-vide/Vakuum': [14, 42, '2–6 Wochen', 'vz'],
        'Tiefkühl': [180, 730, '6–24 Monate', 'vzk'],
        'Trocken/Instant-Beutel': [270, 730, '9–24 Monate', 'vz'],
        'Pouch/Retort': [270, 540, '9–18 Monate', 'vz'],
        'Glas': [365, 730, '1–2 Jahre', 'vz'],
        'Dose': [730, 1460, '2–4 Jahre', 'vzk'],
    }
    OT_PKG = {x['type']: x for x in (old_pkg.get('types') or [])}
    pkg_types = []
    for ty in T_PKG:
        L = [r for r in linz_rows if r.get('_t') == ty]
        R_el = [
            r for r in L
            if (r.get('rankable') or r.get('rankableLight'))
            and not r.get('sold_out')
            and not r.get('price_stale')
            and r.get('pstat') != 'Preis veraltet'
        ]
        after = {}
        for r in L:
            m = re.search(r'nach dem öffnen[^.\n]*', (r.get('_st') or '').lower())
            if m:
                after[m.group(0).strip()] = after.get(m.group(0).strip(), 0) + 1
        top_cands = sorted(
            [
                r for r in R_el
                if r.get('score') is not None
                and r.get('img')
                and r.get('stage') in ('meal', 'stew')
                and not r.get('dry')
                and (r.get('protpack') or 0) >= 12
                and (r.get('pli') is not None or r.get('pliLight') is not None)
            ],
            key=lambda r: (-(r.get('pli') if r.get('pli') is not None else r.get('pliLight') or 0), -r['score']),
        )[:5]
        o = OT_PKG.get(ty, {})
        pkg_types.append({
            **{k: v for k, v in o.items() if k not in ('stats',)},
            'type': ty,
            'icon': ICON_PKG[ty],
            'stats': dict(
                n_products=len(L),
                n_rankable=len(R_el),
                median_price=_med([r.get('price') for r in L]),
                median_price_per_kg=_med([r.get('ppk') for r in L]),
                median_price_per_10g_protein=_med([r.get('eur10p') for r in R_el]),
                median_health_score=_med([r.get('score') for r in R_el]),
                median_pli=_med([r.get('pli') if r.get('pli') is not None else r.get('pliLight') for r in R_el]),
                median_protein_100=_med([r.get('p100') for r in L]),
                median_salt_100=_med([r.get('salt') for r in L]),
                median_kcal_100=_med([r.get('kcal') for r in L]),
                median_additives=_med([r.get('_add') for r in L]),
                n_additives=sum(1 for r in L if r.get('_add') is not None),
                share_bio=round(sum(1 for r in L if r.get('bio')) / len(L) * 100) if L else 0,
            ),
            'box': dict(
                eur10p=_q5([r['eur10p'] for r in R_el if r.get('eur10p') and r['eur10p'] < 15]),
                score=_q5([r['score'] for r in R_el if r.get('score') is not None]),
                salt=_q5([r['salt'] for r in L if r.get('salt') is not None]),
            ),
            'stores': sorted({r['store'] for r in L if r.get('store')}),
            'mhd_typical': MHD_PKG[ty],
            'after_opening_labels': sorted(after.items(), key=lambda x: -x[1])[:5],
            'top': [
                dict(
                    id=r['id'],
                    uid=r.get('uid'),
                    name=r['name'],
                    brand=r.get('brandN') or r.get('brand'),
                    store=r['store'],
                    img=r['img'],
                    logo=r.get('logo'),
                    price=r.get('price'),
                    eur10p=r.get('eur10p'),
                    score=r.get('score'),
                    pli=r.get('pli') if r.get('pli') is not None else r.get('pliLight'),
                    url=r.get('url'),
                )
                for r in top_cands
            ],
        })

    unk_pkg = [r for r in linz_rows if not r.get('_t')]
    assign_map = {}
    for r in rows:
        if not r.get('nonfood'):
            ty, w, _ = _classify_pkg(r)
            if ty:
                assign_map[str(r['id'])] = [ty, w]

    new_pkg = dict(old_pkg)
    new_pkg.update(
        generated='2026-10-25',
        version=4,
        types=pkg_types,
        classification=dict(
            rules=[
                '1 Etikett-Lagerhinweis/Verpackungsangabe (BILLA-Produktdaten)',
                '2 BILLA-Shopkategorie',
                '3 Name/Marke (z. B. FRoSTA/Iglo → TK, Inzersdorfer → Dose, Express/Lotao → Pouch)',
                '4 bisherige Shop-Rubrik',
            ],
            by_reason=sorted(why_counts.items(), key=lambda x: -x[1]),
            moved=moved,
            unclassified=len(unk_pkg),
            total=len(linz_rows),
        ),
        assign=assign_map,
        chart=dict(
            labels=T_PKG,
            n_products=[t['stats']['n_products'] for t in pkg_types],
            median_protein_100=[t['stats']['median_protein_100'] for t in pkg_types],
            median_salt_100=[t['stats']['median_salt_100'] for t in pkg_types],
            median_price_per_10g_protein=[t['stats']['median_price_per_10g_protein'] for t in pkg_types],
            median_health_score=[t['stats']['median_health_score'] for t in pkg_types],
        ),
    )

    # =========================================================================
    # 2. brands.json
    # =========================================================================
    br_path = os.path.join(base_dir, 'analysis/brands.json')
    old_br = json.load(open(br_path)) if os.path.exists(br_path) else {}
    old_br_by_name = {x['brand'].lower(): x for x in (old_br.get('brands') or [])}

    PRIV_META = {
        'billa': ('REWE Group (Billa Eigenmarke)', 'private', 'standard'),
        'billa immer gut': ('REWE Group (Billa Eigenmarke)', 'private', 'standard'),
        'billa bio': ('REWE Group (Billa Bio-Eigenmarke)', 'private', 'bio'),
        'billa genusswelt': ('REWE Group (Billa Premium-Eigenmarke)', 'private', 'premium'),
        'clever': ('REWE Group (Discount-Eigenmarke)', 'private', 'budget'),
        'ja! natürlich': ('REWE Group (Bio-Eigenmarke)', 'private', 'bio'),
        'vegavita': ('REWE Group (Vegan-Eigenmarke)', 'private', 'veggie'),
        'omis schmankerl': ('REWE Group (Billa Frische-Eigenmarke)', 'private', 'standard'),
        'simply good': ('REWE Group (Billa Convenience-Eigenmarke)', 'private', 'standard'),
        'die grillerei': ('REWE Group (Billa Grill-Eigenmarke)', 'private', 'standard'),
        'hofstädter': ('REWE Group (Fleisch-Eigenmarke)', 'private', 'standard'),
        'spar': ('SPAR Österreich (Eigenmarke)', 'private', 'standard'),
        's-budget': ('SPAR Österreich (Discount-Eigenmarke)', 'private', 'budget'),
        'spar natur*pur': ('SPAR Österreich (Bio-Eigenmarke)', 'private', 'bio'),
        'spar natur pur': ('SPAR Österreich (Bio-Eigenmarke)', 'private', 'bio'),
        'spar veggie': ('SPAR Österreich (Veggie-Eigenmarke)', 'private', 'veggie'),
        'spar vital': ('SPAR Österreich (Gesundheits-Eigenmarke)', 'private', 'health'),
        'spar enjoy': ('SPAR Österreich (Convenience-Eigenmarke)', 'private', 'standard'),
        'spar feine küche': ('SPAR Österreich (Frische-Eigenmarke)', 'private', 'standard'),
        'spar premium': ('SPAR Österreich (Premium-Eigenmarke)', 'private', 'premium'),
        'spar bbq': ('SPAR Österreich (Grill-Eigenmarke)', 'private', 'standard'),
        'spar asia': ('SPAR Österreich (Asia-Eigenmarke)', 'private', 'standard'),
        'spar free from': ('SPAR Österreich (Free-From-Eigenmarke)', 'private', 'health'),
        'despar': ('SPAR Italien / Österreich (Eigenmarke)', 'private', 'standard'),
        'tann': ('SPAR Österreich (Fleischwerk-Eigenmarke)', 'private', 'standard'),
        'simpex': ('SPAR Österreich (Non-Food-Eigenmarke)', 'private', 'standard'),
        'interspar': ('SPAR Österreich (Eigenmarke)', 'private', 'standard'),
        'good choice': ('Hofer KG / Aldi Süd (Convenience-Eigenmarke)', 'private', 'standard'),
        'cucina nobile': ('Hofer KG / Aldi Süd (Italien-Eigenmarke)', 'private', 'standard'),
        'cucina': ('Hofer KG / Aldi Süd (Italien-Eigenmarke)', 'private', 'standard'),
        'primana': ('Hofer KG / Aldi Süd (Fertiggerichte-Eigenmarke)', 'private', 'budget'),
        'zurück zum ursprung': ('Hofer KG / Aldi Süd (Bio-Eigenmarke)', 'private', 'bio'),
        'natur aktiv': ('Hofer KG / Aldi Süd (Bio-Eigenmarke)', 'private', 'bio'),
        'le gusto': ('Hofer KG / Aldi Süd (Würz-/Suppen-Eigenmarke)', 'private', 'budget'),
        'asia green garden': ('Hofer KG / Aldi Süd (Asia-Eigenmarke)', 'private', 'standard'),
        "nature's gold": ('Hofer KG / Aldi Süd (TK-Eigenmarke)', 'private', 'standard'),
        'gourmet finest cuisine': ('Hofer KG / Aldi Süd (Premium-Eigenmarke)', 'private', 'premium'),
        'almare': ('Hofer KG / Aldi Süd (Fisch-Eigenmarke)', 'private', 'standard'),
        'landgut': ('Hofer KG / Aldi Süd (Eigenmarke)', 'private', 'standard'),
        'wonnemeyer': ('Hofer KG / Aldi Süd (Feinkost-Eigenmarke)', 'private', 'standard'),
        'genuss aus österreich': ('Hofer KG / Aldi Süd (Regional-Eigenmarke)', 'private', 'standard'),
        'chef select': ('Lidl Stiftung (Convenience-Eigenmarke)', 'private', 'standard'),
        'vemondo': ('Lidl Stiftung (Vegan-Eigenmarke)', 'private', 'veggie'),
        'kania': ('Lidl Stiftung (Suppen-/Würz-Eigenmarke)', 'private', 'budget'),
        'kania (lidl)': ('Lidl Stiftung (Suppen-/Würz-Eigenmarke)', 'private', 'budget'),
        'culinea': ('Lidl Stiftung (TK-Eigenmarke)', 'private', 'standard'),
        'trattoria alfredo': ('Lidl Stiftung (Pizza-Eigenmarke)', 'private', 'standard'),
        'select&go': ('Lidl Stiftung (To-Go-Eigenmarke)', 'private', 'standard'),
        'chef menü': ('REWE / Penny (Fertiggerichte-Eigenmarke)', 'private', 'budget'),
        'penny ready': ('REWE / Penny (Convenience-Eigenmarke)', 'private', 'standard'),
        'food for future': ('REWE / Penny (Vegan-Eigenmarke)', 'private', 'veggie'),
        'dmbio': ('dm-drogerie markt (Bio-Eigenmarke)', 'private', 'bio'),
    }

    CANON_BRAND = {
        'spar feine küche': 'SPAR Feine Küche',
        'spar enjoy': 'SPAR enjoy',
        'spar premium': 'SPAR PREMIUM',
        'spar veggie': 'SPAR Veggie',
        'spar vital': 'SPAR Vital',
        'spar natur pur': 'SPAR Natur*pur',
        'spar natur*pur': 'SPAR Natur*pur',
        'billa': 'BILLA',
        'billa bio': 'BILLA Bio',
        'simply good': 'Simply Good',
        'primana': 'Primana',
        'cucina': 'Cucina',
        'chef select': 'Chef Select',
        'chef menü': 'Chef Menü',
        'kania (lidl)': 'Kania',
        "pizz'ah": "Pizz'Ah",
        "ben's original": "Ben's Original",
        'ben’s original': "Ben's Original",
        'fittaste': 'FitTaste',
        'fit taste': 'FitTaste',
    }

    # Exclude non-meal brands (baby food, sweet pudding/fruit cups) from meal brand rankings
    EXCL_BRAND_M = {'hipp', 'holle', 'mamia', 'freche freunde', 'darbo', 'bonne maman', 'zott', 'alpro', 'danone', 'andros', 'franuí'}

    by_brand = collections.defaultdict(list)
    for r in meal_rows:
        raw_b = (r.get('brandN') or r.get('brand') or '').strip()
        if not raw_b or raw_b in ('(ohne Marke)', 'Ohne Marke'):
            continue
        if raw_b.lower() in EXCL_BRAND_M:
            continue
        b = CANON_BRAND.get(raw_b.lower(), raw_b)
        by_brand[b].append(r)

    all_ppk = [r['ppk'] for r in meal_rows if r.get('ppk') and not r.get('dry') and r['ppk'] < 60]
    all_p10 = [r['eur10p'] for r in meal_rows if r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20]
    med_ppk_all = S.median(all_ppk) if all_ppk else 10.0
    med_p10_all = S.median(all_p10) if all_p10 else 1.5

    brands_out = []
    for b, L in sorted(by_brand.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        bl = b.lower()
        old_m = old_br_by_name.get(bl, {})
        if bl in PRIV_META:
            owner, btype, tier = PRIV_META[bl]
        elif old_m:
            owner = old_m.get('owner') or f'{b} (Markenartikel)'
            btype = old_m.get('type') or ('private' if any(r.get('ownbrand') for r in L) else 'brand')
            tier = old_m.get('tier') or ('bio' if sum(1 for r in L if r.get('bio')) > len(L) / 2 else 'standard')
        else:
            btype = 'private' if any(r.get('ownbrand') for r in L) else 'brand'
            owner = (L[0].get('herst') or L[0].get('manuf') or f'{b} (Markenartikel)')
            tier = 'bio' if sum(1 for r in L if r.get('bio')) > len(L) / 2 else ('veggie' if sum(1 for r in L if r.get('vegan')) > len(L) / 2 else 'standard')

        prices = [r['price'] for r in L if r.get('price')]
        ppks = [r['ppk'] for r in L if r.get('ppk') and not r.get('dry') and r['ppk'] < 60]
        p10s = [r['eur10p'] for r in L if r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20]
        p100ks = [r['p100k'] for r in L if r.get('p100k') is not None]
        p100s = [r['p100'] for r in L if r.get('p100') is not None]
        k100s = [r['kcal'] for r in L if r.get('kcal') is not None]
        salts = [r['salt'] for r in L if r.get('salt') is not None]
        sats = [r['sat'] for r in L if r.get('sat') is not None]
        sugars = [r['sugar'] for r in L if r.get('sugar') is not None]
        fibs = [r['fib'] for r in L if r.get('fib') is not None]
        scores = [r['score'] for r in L if r.get('score') is not None]
        ppes = [r['ppe'] for r in L if r.get('ppe') and not r.get('dry')]
        plis = [r.get('pli') if r.get('pli') is not None else r.get('pliLight') for r in L if (r.get('pli') is not None or r.get('pliLight') is not None)]

        st_box = dict(
            price=_box(prices),
            price_per_kg=_box(ppks),
            eur_per_10g_protein=_box(p10s),
            protein_per_100kcal=_box(p100ks),
            protein_100=_box(p100s),
            kcal_100=_box(k100s),
            salt_100=_box(salts),
            satfat_100=_box(sats),
            sugar_100=_box(sugars),
            fiber_100=_box(fibs),
            health_score=_box(scores),
            protein_per_eur=_box(ppes),
            pli=_box(plis),
            n_with_price=len(prices),
            n_with_nutrition=len(k100s),
            n_rankable=sum(1 for r in L if r.get('rankable') or r.get('rankableLight')),
            bio_share=round(sum(1 for r in L if r.get('bio')) / len(L), 2),
            vegan_share=round(sum(1 for r in L if r.get('vegan')) / len(L), 2),
        )
        mpk = st_box['price_per_kg']['median'] if st_box['price_per_kg'] else None
        mp10 = st_box['eur_per_10g_protein']['median'] if st_box['eur_per_10g_protein'] else None
        ch = min([r for r in L if r.get('price')], key=lambda r: r['price'], default=None)
        bp = min([r for r in L if r.get('eur10p') and not r.get('dry')], key=lambda r: r['eur10p'], default=None)
        lg = next((r.get('logo') for r in L if r.get('logo')), old_m.get('logo'))
        brands_out.append(dict(
            brand=b,
            slug=_slug(b),
            owner=owner,
            type=btype,
            tier=tier,
            count=len(L),
            stores=dict(collections.Counter(r['store'] for r in L if r.get('store')).most_common()),
            stats=st_box,
            price_premium_kg_pct=round((mpk / med_ppk_all - 1) * 100, 1) if mpk else None,
            protein_price_premium_pct=round((mp10 / med_p10_all - 1) * 100, 1) if mp10 else None,
            top_producers=[[p, c] for p, c in collections.Counter(r['herst'] for r in L if r.get('herst')).most_common(3)],
            packaging=dict(collections.Counter(r.get('pack') for r in L if r.get('pack')).most_common()),
            cheapest=dict(id=ch['id'], uid=ch.get('uid'), name=ch['name'], price=ch['price'], size=ch.get('size'), store=ch['store']) if ch else None,
            best_protein_value=dict(id=bp['id'], uid=bp.get('uid'), name=bp['name'], eur10p=bp['eur10p'], protpack=bp.get('protpack'), price=bp.get('price'), score=bp.get('score'), store=bp['store']) if bp else None,
            logo=lg,
            logo_is_chain_logo=bool(old_m.get('logo_is_chain_logo', False)),
        ))

    def _bar_rank(metric, min_n=3, rev=False, limit=25):
        out_r = []
        for x in brands_out:
            s = x['stats'].get(metric)
            if s and s['n'] >= min_n:
                out_r.append(dict(brand=x['brand'], type=x['type'], tier=x['tier'], count=x['count'], n=s['n'], median=s['median'], mean=s['mean'], q1=s['q1'], q3=s['q3']))
        out_r.sort(key=lambda d: d['median'], reverse=rev)
        return out_r[:limit]

    bar_rankings = dict(
        cheapest_price_per_kg=_bar_rank('price_per_kg', 3, False),
        most_expensive_price_per_kg=_bar_rank('price_per_kg', 3, True),
        cheapest_protein=_bar_rank('eur_per_10g_protein', 3, False),
        healthiest=_bar_rank('health_score', 3, True),
        protein_density=_bar_rank('protein_per_100kcal', 3, True),
        lowest_salt=_bar_rank('salt_100', 3, False),
        cheapest_pack_price=_bar_rank('price', 3, False),
        protein_price_premium=sorted(
            [dict(brand=x['brand'], type=x['type'], tier=x['tier'], count=x['count'], n=x['stats']['eur_per_10g_protein']['n'], eur10p_median=x['stats']['eur_per_10g_protein']['median'], premium_pct=x['protein_price_premium_pct']) for x in brands_out if x['stats']['eur_per_10g_protein'] and x['stats']['eur_per_10g_protein']['n'] >= 3 and x['protein_price_premium_pct'] is not None],
            key=lambda d: d['premium_pct'],
        ),
    )

    top_box_brands = [x for x in brands_out if x['count'] >= 5][:30]
    boxplots = {
        m: [dict(brand=x['brand'], type=x['type'], tier=x['tier'], **x['stats'][m]) for x in top_box_brands if x['stats'].get(m)]
        for m in ('price', 'price_per_kg', 'eur_per_10g_protein', 'health_score', 'protein_per_100kcal', 'salt_100')
    }

    scatter = dict(
        price_vs_protein=[
            dict(id=r['id'], uid=r.get('uid'), name=r['name'], brand=CANON_BRAND.get((r.get('brandN') or r.get('brand') or '').lower(), r.get('brandN') or r.get('brand')), type='private' if r.get('ownbrand') else 'brand', tier='bio' if r.get('bio') else 'standard', store=r['store'], price=r['price'], ppk=r.get('ppk'), protpack=r.get('protpack'), eur10p=r.get('eur10p'), p100k=r.get('p100k'), score=r.get('score'), salt=r.get('salt'))
            for r in meal_rows
            if r.get('price') and r.get('protpack') and not r.get('dry') and (r.get('ppk') or 0) < 60
        ],
        brand_bubbles=[
            dict(brand=x['brand'], type=x['type'], tier=x['tier'], count=x['count'], ppk_median=x['stats']['price_per_kg']['median'], eur10p_median=x['stats']['eur_per_10g_protein']['median'], score_median=x['stats']['health_score']['median'] if x['stats']['health_score'] else None, p100k_median=x['stats']['protein_per_100kcal']['median'] if x['stats']['protein_per_100kcal'] else None)
            for x in brands_out
            if x['count'] >= 3 and x['stats']['price_per_kg'] and x['stats']['eur_per_10g_protein']
        ],
    )

    def _grp_summary(pred):
        G = [r for r in meal_rows if pred(r)]
        return dict(
            count=len(G),
            price=_box([r['price'] for r in G if r.get('price')]),
            price_per_kg=_box([r['ppk'] for r in G if r.get('ppk') and not r.get('dry') and r['ppk'] < 60]),
            eur_per_10g_protein=_box([r['eur10p'] for r in G if r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20]),
            protein_per_100kcal=_box([r['p100k'] for r in G if r.get('p100k') is not None]),
            protein_100=_box([r['p100'] for r in G if r.get('p100') is not None]),
            kcal_100=_box([r['kcal'] for r in G if r.get('kcal') is not None]),
            salt_100=_box([r['salt'] for r in G if r.get('salt') is not None]),
            satfat_100=_box([r['sat'] for r in G if r.get('sat') is not None]),
            sugar_100=_box([r['sugar'] for r in G if r.get('sugar') is not None]),
            fiber_100=_box([r['fib'] for r in G if r.get('fib') is not None]),
            health_score=_box([r['score'] for r in G if r.get('score') is not None]),
            protein_per_eur=_box([r['ppe'] for r in G if r.get('ppe') and not r.get('dry')]),
            pli=_box([r.get('pli') if r.get('pli') is not None else r.get('pliLight') for r in G if (r.get('pli') is not None or r.get('pliLight') is not None)]),
            n_with_price=sum(1 for r in G if r.get('price')),
            n_with_nutrition=sum(1 for r in G if r.get('kcal') is not None),
            n_rankable=sum(1 for r in G if r.get('rankable') or r.get('rankableLight')),
            bio_share=round(sum(1 for r in G if r.get('bio')) / len(G), 2) if G else 0,
            vegan_share=round(sum(1 for r in G if r.get('vegan')) / len(G), 2) if G else 0,
        )

    btype_map = {x['brand']: x['type'] for x in brands_out}
    btier_map = {x['brand']: x['tier'] for x in brands_out}
    private_vs_name = dict(
        Eigenmarke=_grp_summary(lambda r: btype_map.get(CANON_BRAND.get((r.get('brandN') or r.get('brand') or '').lower(), r.get('brandN') or r.get('brand'))) == 'private'),
        Markenartikel=_grp_summary(lambda r: btype_map.get(CANON_BRAND.get((r.get('brandN') or r.get('brand') or '').lower(), r.get('brandN') or r.get('brand'))) == 'brand'),
    )
    tiers_out = {
        t_k: _grp_summary(lambda r, tk=t_k: btier_map.get(CANON_BRAND.get((r.get('brandN') or r.get('brand') or '').lower(), r.get('brandN') or r.get('brand'))) == tk)
        for t_k in ('bio', 'budget', 'health', 'premium', 'standard', 'veggie')
    }

    new_br = dict(old_br)
    new_br.update(
        meta=dict(
            generated='2026-10-25',
            total_products=len(meal_rows),
            distinct_brands=len(brands_out),
            brands_ge_3=sum(1 for x in brands_out if x['count'] >= 3),
            brands_ge_5=sum(1 for x in brands_out if x['count'] >= 5),
            private_label_products=private_vs_name['Eigenmarke']['count'],
            name_brand_products=private_vs_name['Markenartikel']['count'],
            unbranded_products=sum(1 for r in meal_rows if r.get('noBrand')),
            overall_median_ppk=round(med_ppk_all, 2),
            overall_median_eur10p=round(med_p10_all, 2),
            overall_median_score=_med([r['score'] for r in meal_rows if r.get('score') is not None]),
        ),
        brands=brands_out,
        bar_rankings=bar_rankings,
        boxplots=boxplots,
        scatter=scatter,
        private_vs_name=private_vs_name,
        tiers=tiers_out,
    )

    # =========================================================================
    # 3. producers_nutrients.json
    # =========================================================================
    pn_path = os.path.join(base_dir, 'analysis/producers_nutrients.json')
    old_pn = json.load(open(pn_path)) if os.path.exists(pn_path) else {}
    res_path = os.path.join(base_dir, 'producers_resolved.json')
    res_prods = json.load(open(res_path)).get('producers', []) if os.path.exists(res_path) else []

    by_nm_linz = {}
    for r in linz_rows:
        by_nm_linz.setdefault((r['store'].lower(), (r.get('name') or '').strip().lower()), r)
        by_nm_linz.setdefault(('*', (r.get('name') or '').strip().lower()), r)

    same_factory = []
    for p in res_prods:
        comp = p.get('company')
        if not comp:
            continue
        code = p.get('code')
        matched_map = {}
        for r in linz_rows:
            if (code and r.get('pid') == code) or (r.get('herst') and comp[:15].lower() in r['herst'].lower()):
                matched_map[r['id']] = r
        for nm in p.get('products') or []:
            r = by_nm_linz.get(('billa', nm.strip().lower())) or by_nm_linz.get(('*', nm.strip().lower()))
            if r:
                matched_map[r['id']] = r
        prods_list = []
        for r in matched_map.values():
            prods_list.append(dict(
                id=r['id'],
                uid=r.get('uid'),
                name=r['name'],
                brand=r.get('brandN') or r.get('brand') or '?',
                chain=r['store'],
                price_eur=r.get('price'),
                size_g=r.get('size'),
                price_per_kg=r.get('ppk'),
                kcal_100=r.get('kcal'),
                protein_100=r.get('p100'),
                salt_100=r.get('salt'),
                health_score=r.get('score'),
                packaging=r.get('pack'),
                image_url=r.get('img'),
            ))
        if not prods_list:
            continue
        prods_list.sort(key=lambda x: (x['price_per_kg'] is None, x['price_per_kg'] or 0))
        ppks = [x['price_per_kg'] for x in prods_list if x['price_per_kg']]
        same_factory.append(dict(
            company=comp,
            state=p.get('state'),
            code=code,
            ooe=p.get('state') == 'Oberösterreich',
            n=len(prods_list),
            brands=sorted({x['brand'] for x in prods_list if x['brand']}),
            chains=sorted({x['chain'] for x in prods_list if x['chain']}),
            price_per_kg_min=min(ppks) if ppks else None,
            price_per_kg_max=max(ppks) if ppks else None,
            spread_factor=round(max(ppks) / min(ppks), 2) if len(ppks) >= 2 and min(ppks) > 0 else None,
            products=prods_list,
        ))
    same_factory.sort(key=lambda x: -x['n'])

    def _dish_bucket(n):
        s = (n or '').lower()
        for k, pat in [
            ('Chili con Carne', 'chili con carne'),
            ('Chili sin Carne', 'chili sin carne'),
            ('Rindsgulasch / Gulasch', 'gulasch'),
            ('Gefüllte Paprika', 'paprika'),
            ('Lasagne Bolognese', 'lasagne'),
            ('Tortelloni / Ravioli', 'tortelloni|ravioli'),
            ('Leberkäse', 'leberkäse|leberkaese'),
            ('Spareribs', 'spareribs|spare ribs'),
            ('Suppentopf', 'suppentopf'),
            ('Linseneintopf', 'linsen'),
            ('Kichererbsen', 'kichererbsen'),
            ('Beuschel', 'beuschel'),
            ('Reisfleisch', 'reisfleisch'),
            ('Cevapcici', 'cevapcici'),
        ]:
            if re.search(pat, s):
                return k
        return None

    similar = []
    for f_entry in same_factory:
        by_d = collections.defaultdict(list)
        for p_item in f_entry['products']:
            b_k = _dish_bucket(p_item['name'])
            if b_k and p_item['price_per_kg']:
                by_d[b_k].append(p_item)
        for d_name, items in by_d.items():
            if len(items) >= 2 and len({(i['brand'], i['chain']) for i in items}) >= 2:
                items.sort(key=lambda x: x['price_per_kg'])
                similar.append(dict(
                    company=f_entry['company'],
                    dish=d_name,
                    cheapest=items[0],
                    priciest=items[-1],
                    factor=round(items[-1]['price_per_kg'] / items[0]['price_per_kg'], 2),
                ))
    similar.sort(key=lambda x: -x['factor'])

    # Nutrient correlations & scatter from meal_rows (excluding base/nonfood!)
    NKEYS = [
        ('kcal', 'kcal_100'),
        ('p100', 'protein_100'),
        ('fat', 'fat_100'),
        ('sat', 'satfat_100'),
        ('carbs', 'carbs_100'),
        ('sugar', 'sugar_100'),
        ('fib', 'fiber_100'),
        ('salt', 'salt_100'),
        ('ppk', 'price_per_kg'),
        ('score', 'health_score'),
    ]

    def _pearson(xs, ys):
        n = len(xs)
        if n < 5:
            return None, n
        mx, my = sum(xs) / n, sum(ys) / n
        vx = sum((x - mx) ** 2 for x in xs)
        vy = sum((y - my) ** 2 for y in ys)
        if vx <= 0 or vy <= 0:
            return 0.0, n
        return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / ((vx * vy) ** 0.5), 3), n

    corr_mat = {}
    for k1, l1 in NKEYS:
        corr_mat[l1] = {}
        for k2, l2 in NKEYS:
            pts = [(r.get(k1), r.get(k2)) for r in meal_rows if r.get(k1) is not None and r.get(k2) is not None and not r.get('dry')]
            r_val, n_val = _pearson([p[0] for p in pts], [p[1] for p in pts])
            corr_mat[l1][l2] = dict(r=r_val, n=n_val)

    def _to_pn_item(r):
        return dict(
            id=r['id'],
            uid=r.get('uid'),
            name=r['name'],
            brand=r.get('brandN') or r.get('brand') or '?',
            chain=r['store'],
            packaging=r.get('pack'),
            price_eur=r.get('price'),
            price_per_kg=r.get('ppk'),
            protein_100=r.get('p100'),
            kcal_100=r.get('kcal'),
            salt_100=r.get('salt'),
            protein_per_euro=r.get('ppe'),
            health_score=r.get('score'),
            ooe=bool(r.get('ooe')),
            image_url=r.get('img'),
            rankable=bool(r.get('rankable') or r.get('rankableLight')),
        )

    pn_items = [_to_pn_item(r) for r in meal_rows if not r.get('dry')]
    scatter_pn = dict(
        protein_vs_price_per_kg=[
            dict(id=x['id'], uid=x['uid'], name=x['name'], brand=x['brand'], chain=x['chain'], x=x['protein_100'], y=x['price_per_kg'], health=x['health_score'], kcal=x['kcal_100'])
            for x in pn_items
            if x['protein_100'] is not None and x['price_per_kg'] is not None and x['price_per_kg'] < 60
        ],
        kcal_vs_protein=[
            dict(id=x['id'], uid=x['uid'], name=x['name'], brand=x['brand'], chain=x['chain'], x=x['kcal_100'], y=x['protein_100'], salt=x['salt_100'], health=x['health_score'])
            for x in pn_items
            if x['kcal_100'] is not None and x['protein_100'] is not None
        ],
    )

    by_pack_salt = collections.defaultdict(list)
    for x in pn_items:
        if x['salt_100'] is not None and 0 <= x['salt_100'] <= 10 and x['packaging']:
            by_pack_salt[x['packaging']].append(x['salt_100'])
    salt_by_pack = [
        dict(packaging=k, n=len(v), median=round(S.median(v), 2), mean=round(S.mean(v), 2), share_over_1_5g=round(sum(1 for s in v if s > 1.5) / len(v), 3))
        for k, v in sorted(by_pack_salt.items(), key=lambda kv: -S.median(kv[1]))
        if len(v) >= 5
    ]

    cand_pareto = [x for x in pn_items if x['rankable'] and x['protein_per_euro'] and x['health_score'] is not None]
    pareto = []
    for a_it in cand_pareto:
        if not any(
            b_it['health_score'] >= a_it['health_score']
            and b_it['protein_per_euro'] >= a_it['protein_per_euro']
            and (b_it['health_score'] > a_it['health_score'] or b_it['protein_per_euro'] > a_it['protein_per_euro'])
            for b_it in cand_pareto
        ):
            pareto.append(a_it)
    pareto.sort(key=lambda x: -x['health_score'])

    bands = []
    for lo, hi in [(30, 40), (40, 50), (50, 60), (60, 70), (70, 101)]:
        sub = [x for x in cand_pareto if lo <= x['health_score'] < hi]
        sub.sort(key=lambda x: -x['protein_per_euro'])
        if sub:
            bands.append(dict(health_band=f'{lo}-{hi - 1}', n=len(sub), best=sub[0], median_ppe=round(S.median([s['protein_per_euro'] for s in sub]), 2)))

    ppks_valid = sorted(x['price_per_kg'] for x in pn_items if x['price_per_kg'] and x['price_per_kg'] < 60)
    p75 = ppks_valid[int(0.75 * len(ppks_valid))] if ppks_valid else 15.0
    expensive_low_prot = sorted(
        [x for x in pn_items if x['price_per_kg'] and x['price_per_kg'] >= p75 and x['protein_100'] is not None and x['protein_100'] < 6],
        key=lambda x: -x['price_per_kg'],
    )[:15]
    salt_bombs = sorted(
        [x for x in pn_items if x['salt_100'] is not None and 2.0 <= x['salt_100'] <= 8.0],
        key=lambda x: -x['salt_100'],
    )[:15]
    best_ppe = sorted(cand_pareto, key=lambda x: -x['protein_per_euro'])[:15]

    ooe_items = [_to_pn_item(r) for r in linz_rows if r.get('ooe')]
    other_at_items = [_to_pn_item(r) for r in linz_rows if r.get('herst') and not r.get('ooe')]
    non_ooe_items = [_to_pn_item(r) for r in linz_rows if not r.get('ooe')]

    def _agg_ooe(lst):
        return dict(
            n=len(lst),
            median_price_per_kg=_med([x['price_per_kg'] for x in lst if x['price_per_kg'] and x['price_per_kg'] < 60]),
            median_protein_100=_med([x['protein_100'] for x in lst]),
            median_salt_100=_med([x['salt_100'] for x in lst if x['salt_100'] is not None and x['salt_100'] <= 10]),
            median_health_score=_med([x['health_score'] for x in lst]),
            median_protein_per_euro=_med([x['protein_per_euro'] for x in lst]),
        )

    new_pn = dict(old_pn)
    new_pn.update(
        meta=dict(
            generated='2026-10-25',
            n_total=len(linz_rows),
            n_meal_rows=len(meal_rows),
            n_resolved_producer_products=sum(f['n'] for f in same_factory),
        ),
        same_factory=same_factory,
        same_factory_similar_dishes=similar,
        correlation_matrix=corr_mat,
        scatter=scatter_pn,
        salt_by_packaging=salt_by_pack,
        pareto_health_vs_protein_per_euro=pareto,
        best_per_health_band=bands,
        traps=dict(
            expensive_low_protein=expensive_low_prot,
            salt_bombs=salt_bombs,
            best_protein_per_euro=best_ppe,
            median_protein_per_euro=_med([x['protein_per_euro'] for x in cand_pareto]),
        ),
        ooe_vs_others=dict(
            ooe=_agg_ooe(ooe_items),
            other_resolved_producers=_agg_ooe(other_at_items),
            all_non_ooe=_agg_ooe(non_ooe_items),
            ooe_products=ooe_items,
        ),
    )

    # =========================================================================
    # 4. chains_categories.json
    # =========================================================================
    cc_path = os.path.join(base_dir, 'analysis/chains_categories.json')
    old_cc = json.load(open(cc_path)) if os.path.exists(cc_path) else {}

    CHAINS_CC = ['Billa', 'Spar', 'Hofer', 'Lidl', 'dm', 'Fit to Go', 'Penny']
    CATS_CC = ['Ripperl', 'Pute', 'Huhn', 'Fisch', 'Gulasch', 'Curry', 'Suppe', 'Knödel', 'Pasta', 'Bowl', 'Asia', 'Hülsenfrüchte', 'Rind', 'Schwein', 'vegetarisch', 'vegan', 'Sonstige']

    # Rows for chain/category analysis: Linz non-base food rows
    cc_rows = [r for r in linz_rows if r.get('stage') != 'base' and r.get('gang') != 'dessert']

    def _get_cc_cat(r):
        cp = set(r.get('cprot') or [])
        cd = set(r.get('cdish') or [])
        nm = (r.get('name') or '').lower()
        if 'Ripperl/Spareribs' in cp:
            return 'Ripperl'
        if 'Gulasch' in cd or re.search(r'gulasch|saftfleisch', nm):
            return 'Gulasch'
        if 'Curry' in cd or re.search(r'curry|tikka|masala|korma|vindaloo|\bdal\b|\bdhal\b', nm):
            return 'Curry'
        if 'Suppe' in cd or re.search(r'suppe|eintopf|minestrone|borschtsch|soljanka|chili', nm):
            return 'Suppe'
        if 'Knödel' in cd or re.search(r'knödel|knoedel', nm):
            return 'Knödel'
        if 'Bowl' in cd or re.search(r'bowl|poke|buddha', nm):
            return 'Bowl'
        if 'Pasta' in cd or re.search(r'pasta|spaghetti|penne|lasagne|ravioli|tortellini|tortelloni|cannelloni|mac.*cheese|bolognese|carbonara|nudel|gnocchi|tagliatelle|fusilli|farfalle|spätzle|spaetzle|schupfnudel|krautfleckerl|hörnchen|makkaroni', nm):
            return 'Pasta'
        if 'Asia' in cd or re.search(r'asia|wok|teriyaki|sweet.*sour|süß.*sauer|pad thai|ramen|udon|bami|nasi|chop suey|fried rice|gebratene nudel|frühlingsrolle|gyoza|dim sum|sushi|thai|vietnam|korean|bibimbap|kimchi', nm):
            return 'Asia'
        if 'Fisch' in cp or 'Meeresfrüchte' in cp:
            return 'Fisch'
        if 'Pute' in cp:
            return 'Pute'
        if 'Huhn' in cp:
            return 'Huhn'
        if 'Rind' in cp:
            return 'Rind'
        if 'Schwein' in cp:
            return 'Schwein'
        if 'Hülsenfrüchte' in cp:
            return 'Hülsenfrüchte'
        if r.get('vegan') or 'vegan' in cp:
            return 'vegan'
        if 'vegetarisch' in cp or 'Käse/Milch' in cp or 'Ei' in cp or 'Tofu/Soja' in cp or 'Seitan/Fleischersatz' in cp:
            return 'vegetarisch'
        return 'Sonstige'

    for r in cc_rows:
        r['_cc_cat'] = _get_cc_cat(r)

    chains_out = {}
    for ch in CHAINS_CC:
        L = [r for r in cc_rows if r['store'] == ch]
        R_el = [r for r in L if r.get('rankable') or r.get('rankableLight')]
        chains_out[ch] = dict(
            count=len(L),
            n_with_nutrition=sum(1 for r in L if r.get('kcal') is not None),
            n_rankable=len(R_el),
            median_price=_med([r.get('price') for r in L]),
            median_price_per_kg=_med([r.get('ppk') for r in L if r.get('ppk') and not r.get('dry') and r['ppk'] < 60]),
            median_eur_per_10g_protein=_med([r.get('eur10p') for r in R_el if r.get('eur10p')]) or _med([r.get('eur10p') for r in L if r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20]),
            median_eur_per_10g_protein_all=_med([r.get('eur10p') for r in L if r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20]),
            median_health_score=_med([r.get('score') for r in R_el if r.get('score') is not None]) or _med([r.get('score') for r in L if r.get('score') is not None]),
            median_salt_100=_med([r.get('salt') for r in L]),
            median_kcal_100=_med([r.get('kcal') for r in L]),
            median_protein_100=_med([r.get('p100') for r in L]),
        )

    cats_out = {}
    best_per_cat = {}
    for cat in CATS_CC:
        L = [r for r in cc_rows if r['_cc_cat'] == cat]
        R_el = [
            r for r in L
            if (r.get('rankable') or r.get('rankableLight'))
            and not r.get('sold_out')
            and not r.get('price_stale')
            and r.get('pstat') != 'Preis veraltet'
        ]
        cats_out[cat] = dict(
            count=len(L),
            n_rankable=len(R_el),
            median_price=_med([r.get('price') for r in L]),
            median_price_per_kg=_med([r.get('ppk') for r in L if r.get('ppk') and not r.get('dry') and r['ppk'] < 60]),
            median_eur_per_10g_protein=_med([r.get('eur10p') for r in R_el if r.get('eur10p')]) or _med([r.get('eur10p') for r in L if r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20]),
            median_health_score=_med([r.get('score') for r in R_el if r.get('score') is not None]) or _med([r.get('score') for r in L if r.get('score') is not None]),
            median_salt_100=_med([r.get('salt') for r in L]),
            median_kcal_100=_med([r.get('kcal') for r in L]),
            median_protein_100=_med([r.get('p100') for r in L]),
        )
        cands = R_el if R_el else [r for r in L if r.get('score') is not None and r.get('price')]
        if cands:
            cands_pli = sorted(cands, key=lambda r: (-(r.get('pli') if r.get('pli') is not None else r.get('pliLight') or 0), -(r.get('score') or 0)))
            cands_hlth = sorted(cands, key=lambda r: -(r.get('score') or 0))
            cands_prot = sorted([r for r in cands if r.get('eur10p')], key=lambda r: r['eur10p']) or cands_pli

            def _fmt_b(r):
                return dict(
                    id=r['id'],
                    uid=r.get('uid'),
                    name=r['name'],
                    brand=r.get('brandN') or r.get('brand'),
                    store=r['store'],
                    price=r.get('price'),
                    eur_per_10g_protein=r.get('eur10p'),
                    health_score=r.get('score'),
                    pli=r.get('pli') if r.get('pli') is not None else r.get('pliLight'),
                    img=r.get('img'),
                    url=r.get('url'),
                )

            best_per_cat[cat] = dict(
                best_overall=_fmt_b(cands_pli[0]),
                healthiest=_fmt_b(cands_hlth[0]),
                cheapest_protein=_fmt_b(cands_prot[0]),
            )

    heatmap_counts = {
        ch: {cat: sum(1 for r in cc_rows if r['store'] == ch and r['_cc_cat'] == cat) for cat in CATS_CC}
        for ch in CHAINS_CC
    }
    heatmap_eur10p = {
        ch: {
            cat: _med([r['eur10p'] for r in cc_rows if r['store'] == ch and r['_cc_cat'] == cat and r.get('eur10p') and not r.get('dry') and r['eur10p'] <= 20])
            for cat in CATS_CC
        }
        for ch in CHAINS_CC
    }

    new_cc = dict(old_cc)
    new_cc.update(
        meta=dict(
            generated='2026-10-25',
            total_products=len(cc_rows),
            chains=CHAINS_CC,
            categories=CATS_CC,
        ),
        chains=chains_out,
        categories=cats_out,
        best_per_category=best_per_cat,
        heatmap_chain_category=dict(
            counts=heatmap_counts,
            median_eur_per_10g_protein=heatmap_eur10p,
        ),
        charts=dict(
            bar_chain_eur10gP=[
                dict(chain=ch, median_eur_per_10g_protein=chains_out[ch]['median_eur_per_10g_protein'], n=chains_out[ch]['count'])
                for ch in CHAINS_CC
                if chains_out[ch]['median_eur_per_10g_protein'] is not None
            ],
            bar_cat_eur10gP=[
                dict(category=cat, median_eur_per_10g_protein=cats_out[cat]['median_eur_per_10g_protein'], n=cats_out[cat]['count'])
                for cat in CATS_CC
                if cats_out[cat]['median_eur_per_10g_protein'] is not None
            ],
            bar_cat_health=[
                dict(category=cat, median_health_score=cats_out[cat]['median_health_score'], n=cats_out[cat]['count'])
                for cat in CATS_CC
                if cats_out[cat]['median_health_score'] is not None
            ],
        ),
    )

    for d_out in out_dirs:
        os.makedirs(d_out, exist_ok=True)
        json.dump(new_pkg, open(os.path.join(d_out, 'packaging_v2.json'), 'w'), ensure_ascii=False, indent=1)
        json.dump(new_br, open(os.path.join(d_out, 'brands.json'), 'w'), ensure_ascii=False, indent=2)
        json.dump(new_pn, open(os.path.join(d_out, 'producers_nutrients.json'), 'w'), ensure_ascii=False, indent=2)
        json.dump(new_cc, open(os.path.join(d_out, 'chains_categories.json'), 'w'), ensure_ascii=False, indent=2)

    return dict(packaging_v2=new_pkg, brands=new_br, producers_nutrients=new_pn, chains_categories=new_cc)
