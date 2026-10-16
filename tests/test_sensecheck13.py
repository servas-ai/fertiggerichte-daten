"""Sensecheck 13 (2026-10-16 orch 17:10): same shop URL with different pack size/price is one product (keep the live size),
oven fish with topping and pure Planted pieces are components, carb + protein names (Penne … Hühnerfilet) are dishes."""
import json, sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v2 as V
P=os.environ.get('GOOD_CHOICE_DATA','/workspace/fertig-app/public/data.json')
_D=None
def _d():
    global _D
    if _D is None: _D=json.load(open(P))
    return _D
TOPS=('topPLI','topPE','topHealth','topLight')

def test_component_rule_carb_word_makes_dish():
    for n in ['Iglo Französische Art Penne, Gemüse & Hühnerfilet','Faschierte Laibchen mit Kartoffelpüree','Cevapcici mit Letscho und Reis',
              'Japanisches Miso-Lachsfilet auf Sushi-Sesam-Reis mit crunchy Salat']:
        assert not V.component_name(n), n
    for n in ['Iglo Schlemmerfilet Bordelaise MSC','Erdäpfellaibchen','Clever Lachsfilet','Falafel','Hühnerfilet natur']:
        assert V.component_name(n), n

def test_topped_fish_is_component():
    for n in ['Iglo Polardorsch Mediterrane Art MSC','Iglo Polar-Dorsch Serbische Art','Iglo MSC Polar-Dorsch Müllerin 4 Stück',
              'S-BUDGET Schlemmerfilet mit Kräutern','Costa Ofenfisch Bordelaise MSC','Iglo MSC Filegro Müllerin XL']:
        assert V.topped_fish(n), n
    for n in ['Seelachs, Reis & Gemüse (XL, 2 Portionen)','Kabeljau mit Tomaten-Sahne-Soße auf Karottenreis','Satay Seelachs',
              'Pochiertes Fischfilet in Tomatenrahm dazu Ofengemüse und Kartoffelspalten','Frosta Tagliatelle Wildlachs']:
        assert not V.topped_fish(n), n

def test_planted_pieces_are_components():
    assert V.meat_sub_piece('Chicken Kräuter & Zitrone','Planted.',160)
    assert V.meat_sub_piece('Planted Chicken Kräuter & Zitrone','Planted',160)
    assert V.meat_sub_piece('planted. steak','planted.',150)
    for n,b,s in [('Planted Chicken BBQ','Juit',500),('Planted Grünes Curry','PrepMyMeal',460),('BILLA Wrap Gyros Planted','BILLA',180),
                  ('SPAR enjoy Kebab-Style Wrap Made with planted.','Spar enjoy',180),('Hähnchen mit Reis','Iglo',400)]:
        assert not V.meat_sub_piece(n,b,s), n

def _core(n):
    n=re.sub(r'\b\d+[.,]?\d*\s*(g|kg|ml|l)\b|\b\d+\s*(portionen|portion|stück|stk)\b','',(n or '').lower())
    return re.sub(r'[^a-z0-9äöüß]+','',n)

def test_same_url_one_visible_size():
    g=collections.defaultdict(list)
    for r in _d()['rows']:
        if r.get('url') and r.get('dupOf') is None and not str(r.get('store') or '').startswith('unbekannt'):
            g[(r['store'],r['url'],_core(r['name']))].append(r)
    bad=[(k[0],k[2],[x.get('size') for x in v]) for k,v in g.items() if len(v)>1 and len({x.get('size') for x in v})>1]
    assert not bad, bad[:10]

def test_billa_lasagne_bolognese_live_size():
    vis=[r for r in _d()['rows'] if r['name']=='BILLA Lasagne Bolognese' and r['store']=='Billa' and r.get('dupOf') is None]
    assert len(vis)==1 and vis[0]['size']==400 and vis[0]['price']==3.19, [(r['size'],r['price']) for r in vis]
    hid=[r for r in _d()['rows'] if r['name']=='BILLA Lasagne Bolognese' and r.get('size')==700]
    assert hid and all(r.get('dupOf') is not None and not r['rankable'] for r in hid)
    ig=[r for r in _d()['rows'] if r['name']=='Iglo Lasagne al Forno' and r['store']=='Billa' and r.get('dupOf') is None]
    assert len(ig)==1 and ig[0]['size']==700, [(r['size'],r['price']) for r in ig]  # shop API 16.10.: 700 g / 7,69 €

def test_listing_urls_not_collapsed():
    # wokostswas.at listing pages carry several different Hofer products on one URL; they must stay separate
    rows=[r for r in _d()['rows'] if (r.get('url') or '').startswith('https://wokostswas.at/k54/')]
    assert len(rows)>=5 and all(r.get('dupOf') is None for r in rows)

def test_top_lists_clean():
    d=_d(); R={r['id']:r for r in d['rows']}
    for L in TOPS:
        ids=d[L]; assert len(ids)==len(set(ids)), L
        for i in ids:
            r=R[i]
            assert r.get('dupOf') is None, (L,r['name'])
            assert not r.get('component'), (L,r['name'])
            assert not re.search(r'polar.?dorsch|schlemmerfilet|filegro|ofenfisch',r['name'],re.I), (L,r['name'])
            assert not (re.search(r'planted',(r['name']+' '+(r.get('brand') or '')),re.I) and (r.get('size') or 0)<=300), (L,r['name'])
        keys=[(R[i]['store'],R[i].get('url'),_core(R[i]['name'])) for i in ids if R[i].get('url')]
        assert len(keys)==len(set(keys)), (L,[k for k,c in collections.Counter(keys).items() if c>1])

def test_component_rows_in_data():
    R=_d()['rows']
    for r in R:
        if re.search(r'Polar.?dorsch (Mediterrane|Serbische) Art|Polardorsch (Mediterrane|Serbische) Art',r['name']):
            assert r['component'] and r['stage']=='prot' and not r['rankable'], r['name']
        if re.fullmatch(r'(Planted )?Chicken Kräuter & Zitrone',r['name']):
            assert r['component'] and not r['rankable'], r['name']
    pen=[r for r in R if 'Französische Art Penne, Gemüse & Hühnerfilet' in r['name']]
    assert pen and all(not r['component'] and r['stage']=='meal' for r in pen)
    assert any(r['rankable'] and 'Laibchen mit Püree' in r['name'] for r in R)
