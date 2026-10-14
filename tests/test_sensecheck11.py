"""Sensecheck 11 + Tonno dedupe (2026-10-14)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v2 as V
P='/workspace/fertig-app/public/data.json'
def _d(): return json.load(open(P))

def test_breaded_rule():
    for n in ['BILLA Pazifischer Polardorsch paniert','Iglo Crispy Chicken Rosmarin-Meersalz','Iglo Knusper Abenteuer','Hühner Nuggets']:
        assert V.breaded_component(n), n
    for n in ['Backhendl mit Kartoffelsalat','Schnitzel mit Pommes','Dr. Oetker Ristorante Pizza Tonno','Fischstäbchen mit Püree']:
        assert not V.breaded_component(n), n

def test_breaded_rows_are_components_not_ranked():
    for r in _d()['rows']:
        if any(k in r['name'] for k in ('Polardorsch paniert','Crispy Chicken Rosmarin','Knusper Abenteuer')):
            assert r['component'] and r['stage']=='prot' and not r['rankable'], r['name']

def test_kernbeisser_breakfast_and_thai_rice():
    assert not V.labels({'name':'Thai-Naturreis mit Kichererbsen'})[0]
    assert V.BREAKFAST.search('Frühstück-Buchweizen mit Äpfeln')
    for r in _d()['rows']:
        if r['store']=='Kernbeißer' and 'Frühstück' in r['name']: assert not r['rankable'] and r['gang']=='frühstück'
        if r['store']=='Kernbeißer' and 'Thai-Naturreis' in r['name']: assert r.get('gang')!='dessert'

def test_toplight_no_starters():
    d=_d(); R={r['id']:r for r in d['rows']}
    assert not [R[i]['name'] for i in d['topLight'] if R[i].get('gang') in ('vorspeise','frühstück','dessert')]

def test_family_pack_before_off_serving():
    assert V.portion({'name':'IGLO Lasagne 700g','size_g':700},{'serving_quantity':400})==(350,'family_pack')
    assert V.portion({'name':'Lasagneblätter 700g','size_g':700},{'serving_quantity':100,'serving_size':'100 g'})[1]!='family_pack'

def test_tonno_one_name_per_product():
    T=[r for r in _d()['rows'] if 'Ristorante' in r['name'] and 'Tonno' in r['name'] and r.get('size')==355]
    assert {r['name'] for r in T}=={'Dr. Oetker Ristorante Pizza Tonno'}, {r['name'] for r in T}
    assert all(r.get('ean')=='4001724038993' for r in T)
    from collections import Counter
    assert max(Counter(r['store'] for r in T).values())==1
