"""Sensecheck 7: sides are ready-to-combine Beilagen only — no desserts, mains/soup inserts, dry staples, duplicates."""
import json,os,re,pytest
P='/workspace/fertig-app/public/data.json'
DESSERT=re.compile(r'milchreis|germknödel|kaiserschmarrn|marillen|zwetschk|topfenknödel|nougat|schoko|palatschink|strudel',re.I)
MAIN=re.compile(r'(wurst|fleisch|selchfleisch|grammel|kaspress|leber|käse)[- ]?knödel|kasnudl|pizza|suprema|ristorante|feine küche|simply good\b.*\bbowl\b',re.I)
DRY=re.compile(r'knödelbrot|backerbsen|gnocchi n\.? ?\d|gnocchi sardi|my risotto|erdäpfelteig',re.I)
pytestmark=pytest.mark.skipif(not os.path.exists(P),reason='no app data.json')
def _S(): return json.load(open(P))
def test_no_dessert_main_dry_sides():
    S=_S()['sides']
    for rx in (DESSERT,MAIN,DRY):
        bad=[s['name'] for s in S if rx.search((s.get('name') or '')+' '+(s.get('brand') or ''))]
        assert not bad,(rx.pattern[:30],bad)
def test_side_portions_plausible():
    S=_S()['sides']
    bad=[(s['name'],s['kcal']) for s in S if s['kcal']>450]
    assert not bad,bad
    dry=[(s['name'],s['k100']) for s in S if (s.get('k100') or 0)>=300 and not re.search(r'reis|basmati|jasmin',s['name'],re.I)]
    assert not dry,dry
def test_no_duplicate_sides_and_combos_resolve():
    D=_S(); S=D['sides']
    names=[re.sub(r'\s+',' ',s['name'].lower().replace('’',"'")).strip() for s in S]
    assert len(names)==len(set(names)),[n for n in set(names) if names.count(n)>1]
    ids={s['id'] for s in S}; assert len(ids)==len(S)
    assert D['combos'] and all(c['veg'] in ids and (c['side'] is None or c['side'] in ids) for c in D['combos'])
    assert len(S)>=120
def test_combo_veg_variety():
    D=_S(); S={s['id']:s['name'] for s in D['sides']}
    from collections import Counter
    top=Counter(S[c['veg']] for c in D['combos']).most_common(1)[0][1]
    assert top<=6,top
