"""sensecheck 50: _reconcile_sc48 recompute path (shipPor, rank guard, sold-out reset, real _collapse with ship-box cap)."""
import collections, json, os, subprocess, sys
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOP = ('topPLI', 'topPLIUncapped', 'topHealth', 'topHealthUncapped', 'topPE', 'topPEUncapped', 'topLight', 'topLightUncapped')

def _export(tmp_path, name, **env):
    out = tmp_path / f'{name}.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), **env)
    e.setdefault('GOOD_CHOICE_AVAILABILITY', 'online_availability_2026-10-18.json')  # baseline snapshot (sensecheck 52 P1)
    e.setdefault('SC52_DUPOF', '0')  # baseline rows without sensecheck 52 P3/P4 dupOf links
    e.pop('ENFORCE_SHIPBOX_CAP', None) if 'ENFORCE_SHIPBOX_CAP' not in env else None  # unset -> sensecheck 51 default shipBox = 6
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))

@pytest.fixture(scope='module')
def canon():
    return json.load(open(os.path.join(ROOT, 'sc48_baseline.json')))['canonical_data']

@pytest.mark.skipif(not os.path.exists(os.path.join(ROOT, 'sc48_baseline.json')), reason='baseline missing')
def test_forced_recompute_reproduces_canonical_top_lists(tmp_path, canon):
    d = _export(tmp_path, 'force', SC50_FORCE_RECOMPUTE='1', ENFORCE_SHIPBOX_CAP='0')
    for k in TOP:
        assert d[k] == canon[k], k
    assert sum(bool(r.get('rankable')) for r in d['rows']) == sum(bool(r.get('rankable')) for r in canon['rows'])

@pytest.mark.skipif(not os.path.exists(os.path.join(ROOT, 'sc48_baseline.json')), reason='baseline missing')
def test_shipbox_cap_keeps_30_and_limits_shipbox_providers(tmp_path, canon):
    d = _export(tmp_path, 'cap', ENFORCE_SHIPBOX_CAP='1')
    by = {r['id']: r for r in d['rows']}
    for k in ('topPLI', 'topHealth', 'topPE'):
        assert len(d[k]) == 30, k  # bug B: used to shrink to 20
        cnt = collections.Counter(by[i]['store'] for i in d[k])
        assert cnt['PrepMyMeal'] <= 6
        assert max(cnt.values()) <= 10
    assert d['topPLIUncapped'] == canon['topPLIUncapped']

def test_rank_guard_and_shipbox_set():
    sys.path.insert(0, ROOT)
    src = open(os.path.join(ROOT, 'export_app.py')).read()
    assert "sh = r.get('shipPor') or 0.0" in src
    assert "'minPortions'" not in src.split('def _reconcile_sc48')[1]
    ns = {'MEALPREP_ONLY': {'PrepMyMeal'}}
    start = src.index('SC50_SHIPBOX_STORES'); end = src.index('def _reconcile_sc48')
    exec(src[start:end], ns)
    g = ns['_sc50_rank_guard']
    ok = dict(score=40, kcalPor=600, price=5, stage='meal', segment='ready_meal', dupOf=None, flags=[])
    assert g(ok)
    for bad in (dict(score=25), dict(kcalPor=950), dict(stage='prot'), dict(component=True), dict(price_stale=True),
                dict(dupOf=3), dict(flags=['Duplikat (x)'])):
        assert not g({**ok, **bad}), bad
    assert 'bofrost' not in ns['SC50_SHIPBOX_STORES'] and 'PrepMyMeal' in ns['SC50_SHIPBOX_STORES']

@pytest.mark.skipif(not os.path.exists(os.path.join(ROOT, 'sc48_baseline.json')), reason='baseline missing')
def test_sc51_default_is_shipbox6_and_uidtop_has_8_keys(tmp_path, canon):
    d = _export(tmp_path, 'default')
    c = _export(tmp_path, 'cap1', ENFORCE_SHIPBOX_CAP='1')
    for k in TOP:
        assert d[k] == c[k], k
    by = {r['id']: r for r in d['rows']}
    assert collections.Counter(by[i]['store'] for i in d['topPLI'])['PrepMyMeal'] == 6
    assert set(d['uidTop']) == set(TOP)
    for k in TOP:
        assert d['uidTop'][k] == [by[i]['uid'] for i in d[k]], k
    # no shared variantIds mutation: rows identical to canonical apart from recompute
    assert [r.get('variantIds') for r in d['rows']] == [r.get('variantIds') for r in canon['rows']]

def test_sc51_default_off_switch(tmp_path, canon):
    d = _export(tmp_path, 'off', ENFORCE_SHIPBOX_CAP='0')
    for k in TOP:
        assert d[k] == canon[k], k
