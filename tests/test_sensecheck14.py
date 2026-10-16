"""Sensecheck 14 (orch 17:45, 16.10.2026): verify-run on review-13 data.
1) gaps_overlay --apply must be part of the export (6c11fb6 had lost 15 heisse-preise prices, 383 price_unknown reasons,
   99 shop_status and the store of 7 OFF-only rows → 'unbekannt (OFF)').
2) Rule E: SPAR Natur*pur baby menus verified via SPAR category 'Babynahrung & Getränke|Baby|Menüs' (spar_baby_menus.json);
   Bio-Gemüse-Risotto 250 g/1,35 € and Mediterrane Bio-Kartoffelpfanne 220 g/1,19 € are baby_food,
   Bio-Steinpilz-/Tomaten-Risotto 2,49 € (SPAR: Reis|Rundkornreis) are not."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v2 as V
P=os.environ.get('GOOD_CHOICE_DATA','/workspace/fertig-app/public/data.json')
_D=None
def _rows():
    global _D
    if _D is None: _D=json.load(open(P))
    return _D['rows']

def test_gaps_overlay_applied():
    R=_rows()
    st=[r.get('price_status') for r in R]
    assert st.count('unknown')>=300 and st.count('filled')>=10
    assert sum(1 for r in R if r.get('shop_status'))>=50
    off={r['name']:r['store'] for r in R if 'openfoodfacts.org/product/9009865009129' in (r.get('url') or '')}
    assert off.get('Thai Red Chicken Curry')=='Billa', off
    assert not [r for r in R if r['name'] in ('Buchstabensuppe','Rigatoni caprese','Thunfischsalat Toskana Art') and str(r.get('store')).startswith('unbekannt')]

def test_E_spar_baby_menus_verified():
    assert len(V.SPAR_BABY)>=15
    assert V.naturpur_baby('SPAR Natur*pur Bio-Gemüse-Risotto',250,1.35)==(True,True)
    assert V.naturpur_baby('SPAR Natur*pur Mediterrane Bio-Kartoffelpfanne',220,1.19)==(True,True)
    assert V.naturpur_baby('SPAR Natur*pur Bio-Steinpilz-Risotto',250,2.49)==(False,False)
    assert V.naturpur_baby('SPAR Natur*pur Bio-Tomaten-Risotto',200,2.49)==(False,False)
    assert V.naturpur_baby('SPAR Natur*pur Bio-Penne Kichererbsen',250,2.08)==(False,False)

def test_E_rows():
    R=[r for r in _rows() if r['store']=='Spar' and 'Natur*pur' in r['name']]
    by=lambda pat:[r for r in R if re.search(pat,r['name'],re.I)]
    for pat in [r'Bio-Gemüse-Risotto',r'Mediterrane Bio-Kartoffelpfanne',r'Bio-Gemüse-Lasagne',r'Bio-Spaghetti Bolognese']:
        L=by(pat); assert L, pat
        for r in L: assert r.get('segment')=='baby_food' and not r.get('rankable'), r['name']
    for pat in [r'Steinpilz-Risotto',r'Tomaten-Risotto']:
        for r in by(pat): assert r.get('segment')!='baby_food', r['name']
    for k in ('topPLI','topPE','topHealth','topLight'):
        ids=set(_D[k]); assert not [r for r in _rows() if r['id'] in ids and r.get('segment')=='baby_food'], k
