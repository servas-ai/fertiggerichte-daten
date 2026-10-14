"""Sensecheck 6b: no dry Knorr/Maggi Kochbeutel/instant mixes in sides; Spaghetteria never in tops."""
import json,os,re,pytest
P='/workspace/fertig-app/public/data.json'
DRY_SIDE=re.compile(
    r'\b(knorr|maggi)\b.*(kochbeutel|semmelknödel|knödel halb|spaghetteria|pasta snack|cup[- ]?a[- ]?soup|asia noodles|bitte zu tisch|quick soup|hüttensnack|instant)|'
    r'kochbeutel.*\b(knorr|maggi)\b',
    re.I)
SPAGH=re.compile(r'spaghetteria',re.I)
@pytest.mark.skipif(not os.path.exists(P),reason='no app data.json')
def test_no_dry_knorr_maggi_in_sides():
    D=json.load(open(P)); S=D['sides']
    bad=[s['name'] for s in S if DRY_SIDE.search((s.get('name') or '')+' '+(s.get('brand') or ''))]
    assert not bad, bad
    assert not any(re.search(r'knorr.*(semmelknödel|kochbeutel)|kochbeutel.*knorr',(s.get('name') or '')+' '+(s.get('brand') or ''),re.I) for s in S)
    ids={s['id'] for s in S}
    assert all(c['veg'] in ids and (c['side'] is None or c['side'] in ids) for c in D['combos'])
@pytest.mark.skipif(not os.path.exists(P),reason='no app data.json')
def test_spaghetteria_not_in_tops():
    D=json.load(open(P)); by={r['id']:r for r in D['rows']}
    for key in ('topPLI','topPE','topHealth','topLight'):
        bad=[by[i]['name'] for i in D.get(key,[]) if i in by and SPAGH.search(by[i].get('name') or '')]
        assert not bad, (key, bad)
    # Spaghetteria rows stay dry + not rankable
    sp=[r for r in D['rows'] if SPAGH.search(r.get('name') or '')]
    assert sp, 'expected Spaghetteria rows in catalog'
    assert all(r.get('dry') and not r.get('rankable') for r in sp), [(r['id'],r['name'],r.get('dry'),r.get('rankable')) for r in sp if not (r.get('dry') and not r.get('rankable'))]
