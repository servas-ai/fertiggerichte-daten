import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, SC63_FIXES='0', **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc62_p1b_p1a_p2_p3_and_supermarket_backfills(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. P1b: Rescued complete meals from stage in ('base', 'side', 'veg')
    for rid, exp_pli in ((23, 32.5), (1484, 26.6), (3050, 26.4), (3668, 35.1), (3037, 30.2)):
        r = by[rid]
        assert r['stage'] == 'meal' and r['gang'] == 'haupt' and r['component'] is False
        assert r['rankable'] is True and r['pli'] == exp_pli

    for rid, exp_plil in ((3660, 28.7), (3662, 32.6), (3672, 32.8), (35, 26.9), (2119, 33.5)):
        r = by[rid]
        assert r['stage'] == 'meal' and r['gang'] == 'haupt' and r['component'] is False
        assert r['rankable'] is False and r['rankableLight'] is True and r['pliLight'] == exp_plil

    assert by[561]['stage'] == 'meal' and by[561]['component'] is False and by[561]['rankable'] is False

    # 2. P1a: Zero rows with stage in ('base', 'side', 'veg') may have meal_class in ('meal', 'light_meal') or component==False
    bad_p1a = [
        r['id'] for r in d['rows']
        if r.get('stage') in ('base', 'side', 'veg')
        and (
            r.get('meal_class') in ('meal', 'light_meal')
            or not r.get('component')
            or r.get('rankable')
            or r.get('rankableLight')
            or (r.get('meal_check') or {}).get('ok') is not False
        )
    ]
    assert bad_p1a == []

    # Specifically verify raw meats and canned beans cited in sensecheck-61 P1a
    for rid in (1323, 3362):
        assert by[rid]['stage'] == 'base' and by[rid]['component'] is True and by[rid]['meal_class'] == 'raw_ingredient'
    for rid in (529, 579, 582, 596, 597, 643):
        assert by[rid]['stage'] == 'base' and by[rid]['component'] is True and by[rid]['meal_class'] == 'raw_ingredient'

    # 3. P2a & P2b: Linz complete meals & 800-g 2-Portionen cans
    for rid, exp_pli in (
        (626, 43.6), (938, 27.6), (922, 23.8), (2777, 23.8),
        (400, 30.4), (598, 29.0), (3151, 35.9),
        (1033, 35.3), (495, 37.0), (2257, 37.4), (395, 34.4), (397, 36.1),
    ):
        r = by[rid]
        assert r['stage'] in ('meal', 'stew') and r['gang'] == 'haupt' and r['component'] is False
        assert r['meal_class'] == 'meal' and r['meal_check']['ok'] is True
        assert r['rankable'] is True and r['pli'] == exp_pli

    # #1031 Billa Felix Linsen mit Speck is a 400g-portion meal demoted as cross-store twin of Spar #2257
    assert by[1031]['portion'] == 400 and by[1031]['meal_class'] == 'meal' and by[1031]['rankable'] is False

    for rid, exp_plil in ((612, 36.0), (614, 28.0), (605, 24.0)):
        r = by[rid]
        assert r['stage'] == 'meal' and r['gang'] == 'haupt' and r['component'] is False
        assert r['meal_class'] == 'light_meal' and r['rankableLight'] is True and r['pliLight'] == exp_plil

    # 4. P3 & Verified Supermarket Nutrition Backfills
    assert by[2878]['fat'] == 5.0
    assert by[3317]['p100'] == 8.5 and by[3317]['protpack'] == 17.0 and by[3317]['score'] == 40.2
    for rid in (199, 246, 1379):
        assert by[rid]['meal_class'] == 'dry'
    assert by[453]['rankable'] is True and by[453]['pli'] == 31.9 and by[453]['score'] == 34.8
    assert by[2663]['incomplete'] is False and by[2663]['score'] == 32.7
    assert by[496]['incomplete'] is False and by[496]['score'] == 35.1
    assert by[102]['incomplete'] is False and by[102]['score'] == 28.7
    for rid, exp_plil in ((1091, 18.9), (51, 25.5), (52, 23.3)):
        assert by[rid]['rankableLight'] is True and by[rid]['pliLight'] == exp_plil

    assert sum(1 for r in d['rows'] if r.get('rankable')) == 187
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 105
    assert d['dataVersion'] == '4644adb26ffa'


def test_sc62_off_switch_reproduces_sc61(tmp_path):
    d = _export(tmp_path, SNAP, SC62_FIXES='0')
    assert d['dataVersion'] == 'b5508366fdef'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 169
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 94

    sub = tmp_path / 'sub'
    sub.mkdir()
    d2 = _export(sub, SNAP, GOOD_CHOICE_DISABLE_SC62='1')
    assert d2['dataVersion'] == 'b5508366fdef'
