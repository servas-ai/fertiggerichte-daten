import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc77_p31_derived_kpis_recomputed_consistently(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. All 16 active rows + 2 dup rows have p100k = round(p100 * 100 / kcal, 1)
    expected_p100k = {
        69: 3.8,
        90: 2.3,
        93: 5.0,
        199: 3.0,
        246: 5.0,
        493: 3.7,
        860: 2.4,
        861: 2.8,
        862: 2.2,
        876: 17.3,
        1163: 2.7,
        1228: 4.5,
        1229: 4.9,
        1235: 2.3,
        1379: 1.7,
        2727: 2.2,
        79: 4.1,
        145: 2.7,
    }
    for rid, exp_val in expected_p100k.items():
        r = by[rid]
        assert r['p100k'] == exp_val, f"#{rid} p100k: {r['p100k']} != {exp_val}"
        assert r['p100k'] == round(r['p100'] * 100.0 / r['kcal'], 1)

    # Specifically verify #861 [Hofer] Asia Green Garden Udon Nudelschüssel (ranked Light Meal)
    assert by[861]['rankableLight'] is True
    assert by[861]['pliLight'] == 30.5
    assert by[861]['p100k'] == 2.8

    # Global invariant: 0 rows with p100 and kcal > 0 have p100k is None
    missing_p100k = [
        r['id'] for r in d['rows']
        if r.get('p100') is not None and (r.get('kcal') or 0) > 0 and r.get('p100k') is None
    ]
    assert missing_p100k == [], f"Rows still missing p100k: {missing_p100k}"

    # 2. All 4 active rows + 1 dup row have protpack and kcalpack
    expected_packs = {
        199: (66.0, 2230),
        246: (130.0, 2600),
        1173: (0.6, 0),
        1379: (27.0, 1566),
        848: (0.6, 0),
    }
    for rid, (exp_pp, exp_kp) in expected_packs.items():
        r = by[rid]
        assert r['protpack'] == exp_pp, f"#{rid} protpack: {r['protpack']} != {exp_pp}"
        assert r['kcalpack'] == exp_kp, f"#{rid} kcalpack: {r['kcalpack']} != {exp_kp}"

    missing_protpack = [
        r['id'] for r in d['rows']
        if (r.get('size') or 0) > 0 and r.get('p100') is not None and r.get('protpack') is None
    ]
    missing_kcalpack = [
        r['id'] for r in d['rows']
        if (r.get('size') or 0) > 0 and r.get('kcal') is not None and r.get('kcalpack') is None
    ]
    assert missing_protpack == [], f"Rows still missing protpack: {missing_protpack}"
    assert missing_kcalpack == [], f"Rows still missing kcalpack: {missing_kcalpack}"

    # 3. All 5 rows (#1399, #3408, #3422, #3425, #3432) + newly backfilled (#199, #246, #1379) have ppe & eur10p
    expected_ppe_eur10p = {
        1399: (5.9, 1.7),
        3408: (5.3, 1.89),
        3422: (6.7, 1.5),
        3425: (6.5, 1.53),
        3432: (3.3, 2.99),
        199: (8.3, 1.21),
        246: (16.3, 0.61),
        1379: (1.6, 6.29),
    }
    for rid, (exp_ppe, exp_eur10p) in expected_ppe_eur10p.items():
        r = by[rid]
        assert r['ppe'] == exp_ppe, f"#{rid} ppe: {r['ppe']} != {exp_ppe}"
        assert r['eur10p'] == exp_eur10p, f"#{rid} eur10p: {r['eur10p']} != {exp_eur10p}"

    missing_ppe_eur10p = [
        r['id'] for r in d['rows']
        if (r.get('price') or 0) > 0 and (r.get('protpack') or 0) > 0
        and (r.get('ppe') is None or r.get('eur10p') is None)
    ]
    assert missing_ppe_eur10p == [], f"Rows still missing ppe/eur10p: {missing_ppe_eur10p}"


def test_sc77_p31_row_3425_rescued_to_rankable_light_and_stale_off_flags_cleaned(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    r3425 = by[3425]
    assert r3425['store'] == 'Billa'
    assert r3425['name'] == 'Thunfischsalat Toskana Art'
    assert r3425['price'] == 2.69
    assert r3425['size'] == 160
    assert r3425['stage'] == 'meal'
    assert r3425['gang'] == 'haupt'
    assert r3425['segment'] == 'ready_meal'
    assert r3425['component'] is False
    assert r3425['meal_class'] == 'light_meal'
    assert r3425['pPor'] == 2.69
    assert r3425['pPorEff'] == 2.69
    assert r3425['p100g'] == 1.68
    assert r3425['ppe'] == 6.5
    assert r3425['eur10p'] == 1.53
    assert r3425['eur100k'] == 1.11
    assert r3425['rankable'] is False
    assert r3425['pli'] is None
    assert r3425['rankableLight'] is True
    assert r3425['pliLight'] == 39.8
    assert r3425['rank_excluded_reason'] == '243 kcal/Portion < 400 (Light Meal)'
    assert r3425['flags'] == ['Mahlzeit-Check: 243 kcal/Portion < 400']

    # Global invariant: 0 priced store rows carry stale 'nur Open Food Facts, kein Laden/Preis'
    stale_off_priced = [
        r['id'] for r in d['rows']
        if (r.get('price') or 0) > 0 and r.get('store') and not str(r.get('store')).startswith('unbekannt')
        and (
            'nur Open Food Facts, kein Laden/Preis' in (r.get('rank_excluded_reason') or '')
            or any('nur Open Food Facts, kein Laden/Preis' in f for f in (r.get('flags') or []))
        )
    ]
    assert stale_off_priced == [], f"Priced store rows still carrying stale OFF no-price flag/reason: {stale_off_priced}"


def test_sc77_p31_noodels_typo_fixed_and_totals(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    assert by[880]['name'] == 'Rana Teriyaki Style Noodles Hühnchen'
    assert by[3290]['name'] == 'Rana Teriyaki Style Noodles mit Huhn'
    assert [r['id'] for r in d['rows'] if 'Noodels' in (r.get('name') or '')] == []

    assert d['dataVersion'] == '3368eaec1025'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 156


def test_sc77_off_switches_reproduce_sc76_baseline_bit_for_bit(tmp_path):
    for kw in ({'SC77_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC77': '1'}):
        d = _export(tmp_path, SNAP, **kw)
        assert d['dataVersion'] == '6fa43d749824'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
