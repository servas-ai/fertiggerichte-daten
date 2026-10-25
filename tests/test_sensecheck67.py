import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc67_p1_1_p2_1_p2_2_and_p3_1(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC67 P1.1: Rescue 3 real meals in Linz (#1277, #1031, #496) + clean false Tofu Proteinkomponente flag (#568, #3168)
    r1277 = by[1277]
    assert r1277['store'] == 'dm' and r1277['stage'] == 'meal' and r1277['segment'] == 'ready_meal'
    assert r1277['meal_class'] == 'light_meal' and r1277['gang'] == 'haupt' and r1277['component'] is False
    assert r1277['rankable'] is False and r1277['pli'] is None
    assert r1277['rankableLight'] is True and r1277['pliLight'] == 53.5 and r1277.get('rank_excluded_reason') is None
    assert d['topLight'][1] == 1277

    for rid in (1277, 568, 3168):
        assert by[rid]['component'] is False
        assert not any('Proteinkomponente' in f for f in (by[rid].get('flags') or []))
        assert 'Proteinkomponente' not in ((by[rid].get('meal_check') or {}).get('reason') or '')

    r1031 = by[1031]
    assert r1031['store'] == 'Billa' and r1031['rankable'] is True and r1031['rankableLight'] is False
    assert r1031['pli'] == 37.4 and r1031['pliLight'] is None and r1031.get('rank_excluded_reason') is None
    assert 'Duplikat (nahe Name/Marke, Ranking)' not in (r1031.get('flags') or [])

    r496 = by[496]
    assert r496['store'] == 'Spar' and r496['stage'] == 'meal' and r496['segment'] == 'ready_meal'
    assert r496['meal_class'] == 'light_meal' and r496['gang'] == 'haupt' and r496['component'] is False
    assert r496['rankable'] is False and r496['pli'] is None
    assert r496['rankableLight'] is True and r496['pliLight'] == 31.7 and r496.get('rank_excluded_reason') is None

    # 2. SC67 P2.1: 36 active screw-jar meals (plus hidden twin #3448) reclassified to pack='Glas'; #1266 to pack='Trocken/Instant'
    assert by[1266]['pack'] == 'Trocken/Instant'
    jar_ids = (
        156, 157, 158, 902, 1255, 1256, 1258, 1260, 1261, 1262, 1263, 1264,
        1265, 1267, 1268, 1272, 1273, 1275, 1277, 1278, 1585, 1586, 1660, 1713,
        1714, 1717, 1762, 1763, 1764, 1765, 1855, 1856, 2124, 2140, 2141, 2192,
    )
    for jid in jar_ids:
        assert by[jid]['pack'] == 'Glas'

    # 3. SC67 P2.2: Multi-portion normalization (#1020 + 4 bofrost multi-portion bags #3020, #2956, #2980, #3071)
    r1020 = by[1020]
    assert r1020['portion'] == 400 and r1020['portion_g'] == 400 and r1020['meal_class'] == 'light_meal'
    assert r1020['kcalPor'] == 352.0 and r1020['protPor'] == 10.4 and r1020['pPor'] == 3.25
    assert r1020['rankable'] is False and r1020['rankableLight'] is False
    assert r1020['rank_excluded_reason'] == '< 15 g Protein/Portion'

    assert by[3020]['portion'] == 375 and by[3020]['meal_class'] == 'light_meal' and by[3020]['rankableLight'] is True and by[3020]['pliLight'] == 41.3
    assert by[2956]['portion'] == 400 and by[2956]['meal_class'] == 'light_meal' and by[2956]['rankableLight'] is True and by[2956]['pliLight'] == 27.3
    assert by[2980]['portion'] == 385 and by[2980]['meal_class'] == 'meal' and by[2980]['rankable'] is True and by[2980]['pli'] == 26.9
    assert by[3071]['portion'] == 500 and by[3071]['meal_class'] == 'meal' and by[3071]['rankable'] is True and by[3071]['pli'] == 28.4

    # 4. SC67 P3.1: Zero unranked live 2026 (dupOf is None) rows have rank_excluded_reason == None
    unranked_missing_reason = [
        r['id'] for r in d['rows']
        if r.get('pstat') == 'live 2026'
        and r.get('dupOf') is None
        and not r.get('rankable')
        and not r.get('rankableLight')
        and not r.get('rank_excluded_reason')
    ]
    assert unranked_missing_reason == []

    # 5. Totals & dataVersion
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 185
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 152
    assert d['dataVersion'] == '684af70ab124'


def test_sc67_off_switch_reproduces_sc66_bit_for_bit(tmp_path):
    for env_kw in ({'SC67_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC67': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == '8bb86dd879eb'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 182
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 148
