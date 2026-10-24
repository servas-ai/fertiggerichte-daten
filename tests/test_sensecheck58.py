import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC60_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc58_ungate_6_prepmymeal_full_meals(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    expected = [
        (2828, 'ejupucyhhi', 56.4, 71.3, 60.0, 9.6, 580.0, 500),
        (2852, 'sxrcfm5xb5', 48.4, 59.2, 54.5, 8.7, 550.0, 500),
        (2793, 'oi2itoqcpp', 42.8, 56.2, 42.5, 6.8, 585.0, 500),
        (2849, 'sny929kedi', 36.0, 50.3, 31.5, 5.0, 590.0, 500),
        (2867, 'r7kjdcrlme', 29.0, 40.6, 38.4, 3.8, 596.0, 400),
        (2801, 'kah0s1vb9m', 28.1, 39.4, 38.5, 3.7, 555.0, 470),
    ]
    for rid, uid, pli, score, prot_por, ppe, kcal_por, portion in expected:
        r = by[rid]
        assert r['uid'] == uid
        assert r['store'] == 'PrepMyMeal'
        assert r['rankable'] is True
        assert r['pli'] == pli
        assert r['score'] == score
        assert r['protPor'] == prot_por
        assert r['ppe'] == ppe
        assert r['kcalPor'] == kcal_por
        assert r['portion'] == portion
        assert r['meal_class'] == 'meal'
        assert r['meal_check']['ok'] is True
        assert r['meal_check']['cls'] == 'meal'
        assert not r.get('sold_out')
        assert not r.get('kiloErr')
        assert r.get('flags') == []

    # #2828 enters topPLI, topHealth, and topPE
    assert 2828 in d['topPLI'] and 2828 in d['topPLIUncapped']
    assert 2828 in d['topHealth'] and 2828 in d['topHealthUncapped']
    assert 2828 in d['topPE'] and 2828 in d['topPEUncapped']
    # #2852 enters topPLIUncapped and topPE
    assert 2852 in d['topPLIUncapped']
    assert 2852 in d['topPE'] and 2852 in d['topPEUncapped']
    # PrepMyMeal capped at 6 in topPLI, topHealth, topPE
    for k in ('topPLI', 'topHealth', 'topPE'):
        assert sum(by[i]['store'] == 'PrepMyMeal' for i in d[k]) <= 6

    assert sum(bool(r.get('rankable')) for r in d['rows']) == 167


def test_sc58_billa_clever_dry_soups_and_dup_redirects(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    for rid, dup_id in ((534, 994), (535, 995), (536, 996), (537, 997), (538, 998), (539, 999)):
        r = by[rid]
        assert r['store'] == 'Billa'
        assert r['dry'] is True
        assert r['rankable'] is False
        assert r['meal_class'] == 'dry'
        assert r['meal_check'] == {'ok': False, 'cls': 'dry', 'reason': 'Trockenprodukt'}
        assert r['rank_excluded_reason'] == 'Trockensuppe (kein Fertiggericht)'
        for k in ('size', 'portion', 'portion_g', 'pPor', 'p100g', 'ppk', 'protpack', 'kcalpack', 'protPor', 'kcalPor', 'kcal_meal', 'saltPor', 'saltPct', 'eur10p', 'eur100k', 'ppe'):
            assert r.get(k) is None, f'#{rid} {k} should be None, got {r.get(k)}'

        dup = by[dup_id]
        assert dup['dupOf'] == rid
        assert dup['dupOfUid'] == r['uid']
        assert dup['size'] is None
        assert dup['meal_class'] == 'dry'
        assert dup['rank_excluded_reason'] == 'Trockensuppe (kein Fertiggericht)'


def test_sc58_offswitches_preserve_prior_dataversions(tmp_path):
    d_sc58_off1 = _export(tmp_path, SNAP, SC58_FIXES='0')
    d_sc58_off2 = _export(tmp_path, SNAP, GOOD_CHOICE_DISABLE_SC58='1')
    assert d_sc58_off1['dataVersion'] == '4316234b1aa7'
    assert d_sc58_off2['dataVersion'] == '4316234b1aa7'
    assert sum(bool(r.get('rankable')) for r in d_sc58_off1['rows']) == 161

    d_sc55 = _export(tmp_path, SNAP, SC58_FIXES='0', SC55_VERSANDBOX='0')
    assert d_sc55['dataVersion'] == 'a9e298c0daba'
    assert sum(bool(r.get('rankable')) for r in d_sc55['rows']) == 161

    d_sc53 = _export(tmp_path, SNAP, SC54_PREPMYMEAL='0')
    assert d_sc53['dataVersion'] == 'ce8d8d111664'
    assert sum(bool(r.get('rankable')) for r in d_sc53['rows']) == 158
