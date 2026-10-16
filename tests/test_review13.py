"""Review 13 (Good Choice Reviewer, 16.10.2026): D component lock incl. topLight, F variants/shipping/provider cap,
E baby_food, A/B fillet components + piece portions, C breaded list, G Steinofenpizza size + price_condition."""
import json, sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v2 as V
P=os.environ.get('GOOD_CHOICE_DATA','/workspace/fertig-app/public/data.json')
_D=None
def _d():
    global _D
    if _D is None: _D=json.load(open(P))
    return _D
def _rows(): return _d()['rows']
def _byid(): return {r['id']:r for r in _rows()}
TOPS=('topPLI','topPE','topHealth','topLight')

def test_D_meat_piece_rule():
    for n in ['BILLA Genusswelt Rindsbackerl Sous Vide','Schweinsbraten','Wiesbauer Wiener Prater Stelze','bofrost Pfeffersteak','Rindswangerln in Rotweinsauce','Hühnerfilet natur']:
        assert V.meat_piece(n), n
    for n in ['Schweinsbraten mit Knödel','Inzersdorfer Zwiebelrindsbraten mit Spiralen','Rindsrouladen in Bratensauce','Gebratene Nudeln mit Huhn','Hühnerfilet mit Reis','Rindsgulasch']:
        assert not V.meat_piece(n), n

def test_D_toplight_has_no_components():
    b=_byid()
    for k in TOPS:
        for i in _d()[k]:
            r=b[i]; assert not r.get('component'), (k,r['name'])
            assert not re.search(r'rindsbackerl',r['name'],re.I), (k,r['name'])

def test_F_one_variant_per_dish_and_cap():
    b=_byid()
    for k in TOPS:
        L=[b[i] for i in _d()[k]]
        keys=[(r['store'],re.sub(r'[^a-z0-9äöüß]+','',re.sub(r'\(\s*xl[^)]*\)|\bxl\b|\(\s*\d+[.,]?\d*\s*(g|kg)\s*\)','',r['name'].lower()))) for r in L]
        assert len(keys)==len(set(keys)), k
        assert max(collections.Counter(r['store'] for r in L).values())<=10, k
        assert k+'Uncapped' in _d()
    assert _d()['topCap']['perProvider']==10

def test_F_shipping_on_delivery_portion():
    pm=[r for r in _rows() if r['store']=='PrepMyMeal' and r.get('pPor')]
    assert pm and all(abs(r['shipPor']-round(5.99/6,2))<0.011 and abs(r['pPorEff']-r['pPor']-r['shipPor'])<0.011 for r in pm)
    assert not any(r.get('shipPor') for r in _rows() if r['store'] in ('Billa','Spar','MPreis'))

def test_E_baby_food():
    assert V.baby_age('Bio-Gemüse ab 5 Monaten') and V.baby_age('ab dem 8. Monat') and V.baby_age('x','en:baby-foods')
    assert not V.baby_age('Rindsgulasch 400 g')
    assert V.naturpur_baby('SPAR Natur*pur Bio-Spaghetti Bolognese',190,0.95)==(True,True)
    assert V.naturpur_baby('SPAR Natur*pur Bio-Gemüse-Risotto',250,1.35)==(False,False)
    for r in _rows():
        if r['store']=='Spar' and re.search(r'natur\*pur bio-spaghetti bolognese',r['name'],re.I) and (r.get('size') or 999)<=250: assert r['segment']=='baby_food'
        if r['store']=='Spar' and 'Risotto' in r['name'] and 'Natur*pur' in r['name']: assert r.get('segment')!='baby_food', r['name']

def test_AB_goldschatz_component_and_piece_portion():
    g=[r for r in _rows() if 'goldschatz' in r['name'].lower()]
    assert len(g)>=8
    for r in g: assert r['component'] and not r['rankable'] and r['portion']==200, r['name']
    assert V.piece_portion('Iglo Polar-Dorsch Müllerin 4 Stück',400)==200

def test_C_breaded_extended():
    for n in ['Hubers Karaage Asia Style','Garnelen Tempura','Chicken Katsu','Popcorn Chicken','Backhendl','Cordon Bleu']:
        assert V.breaded_component(n), n
    assert not V.breaded_component('Karaage mit Reis')

def test_G_steinofenpizza():
    r=[r for r in _rows() if r['store']=='MPreis' and r['name']=='Jeden Tag Steinofenpizza Thunfisch 2er-Packung']
    assert r and r[0]['size']==710 and r[0]['portion']==355 and r[0].get('price_condition')=='NUR MIT APP'
    for x in _rows():
        if x.get('badge'): assert x['score']<50 and x['rankable']

def test_D_roast_with_side_is_dish():
    for n in ['bofrost Surbraten mit Sauerkraut','Schweinsbraten mit Rotkraut','Rinderbraten mit Gemüse','Braten mit Bohnen','Zwiebelrostbraten mit Spätzle','Schweinsbraten mit Püree']:
        assert not V.meat_piece(n), n
    for n in ['bofrost Faschierter Braten mit Pfefferrahmsauce','Rindswangerln in Rotweinsauce','bofrost Jägerrostbraten']:
        assert V.meat_piece(n), n

def test_D_dish_still_needs_meal_check():
    for r in _rows():
        if r.get('rankable'):
            mc=r.get('meal_check') or {}
            assert 400<=(mc.get('kcal') or 0)<=900 and (mc.get('protein') or 0)>=20, r['name']

def test_G_price_condition_info():
    r=[r for r in _rows() if r['store']=='MPreis' and r['name']=='Jeden Tag Steinofenpizza Thunfisch 2er-Packung'][0]
    i=r['price_condition_info']
    assert i['text']=='NUR MIT APP' and i['source_url']==r['url'] and i['checked']>='2026-10-16'

def test_store_known_for_heisse_preise_matched_off_rows():
    st={r['name']:r['store'] for r in _rows()}
    assert st.get('Thai Red Chicken Curry')=='Billa' and st.get('Kräftige Hühnersuppe')=='Spar'
