"""Sensecheck 12-verify (2026-10-14 orch 07:46): plain fresh pasta is an ingredient, Butter Chicken is a ready meal, protein+pasta names are dishes."""
import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v2 as V
P=os.environ.get('GOOD_CHOICE_DATA','/workspace/fertig-app/public/data.json')
def _d(): return json.load(open(P))

def test_butter_chicken_not_grocery():
    for n in ['BILLA Butter Chicken mit Reis','Rana Indian Style Butter Chicken mit Reis','HOFMANNs Gelbes Curry "Butter Chicken Style"','Veganes Curry typ Butter-Chicken']:
        assert not V.labels({'name':n})[1], n
    for n in ["Kelly's Mikrowellen Popcorn Butter Geschmack 3 x 90g",'Kerrygold Butter 250 g']:
        assert V.labels({'name':n})[1], n

def test_plain_fresh_pasta_not_ranked():
    rows=[r for r in _d()['rows'] if re.fullmatch(r'(Bertagni|Rana) Tagliatelle( \(frische Pasta\))?',r['name'])]
    assert rows
    for r in rows: assert r['stage']=='base' and not r['rankable'] and r.get('pli') is None, r['name']

def test_pasta_dishes_stay_meals():
    R=_d()['rows']
    for r in R:
        if re.search(r'Tagliatelle Wildlachs|Wildlachs Spaghetti|Pumpkin Rigatoni|Pappardelle mit Ragout',r['name']): assert r['stage']=='meal' or r['stage']=='stew', (r['name'],r['stage'])
    assert any(r['rankable'] and 'Butter Chicken' in r['name'] for r in R)

def test_no_plain_pasta_in_top_lists():
    d=_d(); R={r['id']:r for r in d['rows']}
    for L in ('topPLI','topPE','topHealth','topLight'):
        assert not [R[i]['name'] for i in d[L] if R[i]['stage']=='base' or re.search(r'frische pasta\)',R[i]['name'],re.I)], L
