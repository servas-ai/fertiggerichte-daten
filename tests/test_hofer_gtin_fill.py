"""Sensecheck 6 §3 follow-up: Hofer GOOD CHOICE rows filled only from OFF by EAN (GTIN-confirmed).
Values must equal the OFF evidence snapshot; same-store twins collapse via dupOf; low-protein
light meals stay unranked (no invented ranking)."""
import json,re
import os as _os; P=_os.environ.get('GOOD_CHOICE_DATA','/workspace/fertig-app/public/data.json')
EV=json.load(open('/workspace/fertig/qa/hofer_gtin_off_2026-10-14.json'))['products']
EXP={'4099200075556':(266,11,1.6),'4099200075570':(220,5.4,1.5),'4061463022950':(113,3.3,0.84),'4061463023018':(119,4.0,1.02)}

def _rows():
    return json.load(open(P))['rows']

def test_evidence_matches_expected():
    for e,(k,p,s) in EXP.items():
        n=EV[e]['nutriments_100g']
        assert EV[e]['status']==1, e
        assert n['energy-kcal_100g']==k and n['proteins_100g']==p and abs(n['salt_100g']-s)<0.02, (e,n)

def test_hofer_gtin_rows_filled_and_confirmed():
    R=[r for r in _rows() if (r.get('store') or '').lower()=='hofer' and str(r.get('ean') or '') in EXP]
    by={}
    for r in R: by.setdefault(r['ean'],[]).append(r)
    assert set(by)==set(EXP), sorted(by)
    for e,rs in by.items():
        k,p,s=EXP[e]
        for r in rs:
            assert r['kcal']==k and r['p100']==p and abs((r.get('salt') or 0)-s)<0.02, (r['id'],r['name'],r['kcal'],r['p100'],r.get('salt'))
            assert r.get('nutrition_source')=='GTIN-confirmed', (r['id'],r.get('nutrition_source'))
        main=[r for r in rs if r.get('dupOf') is None]
        assert len(main)==1, (e,[(r['id'],r.get('dupOf')) for r in rs])

def test_wraps_have_nutrition_now():
    R=_rows()
    for pat in (r'wrap caes?er chicken',r'wraps? thai couscous'):
        w=[r for r in R if (r.get('store') or '').lower()=='hofer' and re.search(pat,r['name'],re.I)]
        assert w and all(r.get('kcal') is not None and r.get('p100') is not None for r in w), (pat,[(r['id'],r.get('kcal')) for r in w])

def test_low_protein_light_meals_not_ranked():
    for r in _rows():
        if str(r.get('ean') or '') in EXP:
            mc=r.get('meal_check') or {}
            if not mc.get('ok'): assert not r.get('rankable') and r.get('pli') is None, (r['id'],r['name'])
