"""Sensecheck 6: Thunfisch wraps are stage meal (not prot/component); plain thunfisch cans may stay prot."""
import json,re
import os as _os; P=_os.environ.get('GOOD_CHOICE_DATA','/workspace/fertig-app/public/data.json')

def test_thunfisch_wraps_are_meal_not_prot():
    R=json.load(open(P))['rows']
    wraps=[r for r in R if re.search(r'wrap',(r.get('name') or ''),re.I) and re.search(r'thunfisch',(r.get('name') or ''),re.I)]
    assert wraps, 'expected at least one Thunfisch wrap'
    bad=[(r['id'],r['name'],r.get('stage'),r.get('component')) for r in wraps if r.get('stage')=='prot' or r.get('component')]
    assert not bad, f'Thunfisch wraps still prot/component: {bad}'
    for r in wraps:
        assert r.get('stage')=='meal', (r['id'],r['name'],r.get('stage'))
