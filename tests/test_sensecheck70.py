import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc70_p1_1_p2_and_p3_2(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC70 P1.1: Denn's rows (#2204, #2205, #2206) completed with verified manufacturer / OFF data
    r2204 = by[2204]
    assert r2204['store'] == "Denn's" and r2204['ean'] == '4250073460614'
    assert r2204['size'] == 200.0 and r2204['portion'] == 200 and r2204['portion_source'] == 'pack_single'
    assert r2204['kcalPor'] == 452.0 and r2204['protPor'] == 26.0 and r2204['score'] == 49.8
    assert r2204['stage'] == 'prot' and r2204['meal_class'] == 'protein_component' and r2204['component'] is True
    assert r2204['rankable'] is False and r2204['rankableLight'] is False
    assert r2204['rank_excluded_reason'] == 'Proteinkomponente (keine vollständige Mahlzeit)'
    assert "Denn's" in by[2040].get('alsoAt', []) and "Denn's" in by[4018].get('alsoAt', [])

    r2205 = by[2205]
    assert r2205['store'] == "Denn's" and r2205['ean'] == '4026584133640'
    assert r2205['size'] == 200.0 and r2205['portion'] == 200 and r2205['portion_source'] == 'pack_single'
    assert r2205['kcalPor'] == 434.0 and r2205['protPor'] == 20.0 and r2205['pPor'] == 3.99 and r2205['score'] == 64.0
    assert r2205['stage'] == 'meal' and r2205['meal_class'] == 'meal' and r2205['component'] is False
    assert r2205['rankable'] is True and r2205['pli'] == 44.5 and r2205['rankableLight'] is False
    assert r2205.get('rank_excluded_reason') is None

    r2206 = by[2206]
    assert r2206['store'] == "Denn's" and r2206['ean'] == '4012344902069'
    assert r2206['size'] == 380.0 and r2206['portion'] == 380 and r2206['portion_source'] == 'pack_single'
    assert r2206['kcalPor'] == 357.2 and r2206['protPor'] == 49.4 and r2206['pPor'] == 3.99 and r2206['score'] == 54.9
    assert r2206['stage'] == 'stew' and r2206['meal_class'] == 'light_meal' and r2206['component'] is False
    assert r2206['rankable'] is False and r2206['rankableLight'] is True and r2206['pliLight'] == 58.4
    assert r2206.get('rank_excluded_reason') is None

    # 2. SC70 P2.1: 1000 g Lasagne Bolognese family trays (#172 Spar, #530 Billa, #3057 bofrost) -> 500 g (pack_2portions, rankable=True)
    for lid, store, kpor, ppor, prpor, score, pli in (
        (172, 'Spar', 695.0, 29.0, 2.0, 34.3, 53.4),
        (530, 'Billa', 710.0, 28.0, 2.0, 30.6, 50.3),
        (3057, 'bofrost', 690.0, 33.5, 6.75, 37.7, 31.3),
    ):
        rl = by[lid]
        assert rl['store'] == store and rl['portion'] == 500 and rl['portion_source'] == 'pack_2portions'
        assert rl['multi_portion'] is True and rl['kcalPor'] == kpor and rl['protPor'] == ppor
        assert rl['pPor'] == prpor and rl['pPorEff'] == prpor and rl['score'] == score
        assert rl['meal_class'] == 'meal' and rl['rankable'] is True and rl['rankableLight'] is False
        assert rl['pli'] == pli and rl.get('rank_excluded_reason') is None

    # 3. SC70 P2.2: 800 g Inzersdorfer Gefüllte Paprika (#428 Spar & #923 Billa) -> 400 g (pack_2portions)
    for pid, store, prpor in ((428, 'Spar', 3.15), (923, 'Billa', 3.2)):
        rp = by[pid]
        assert rp['store'] == store and rp['portion'] == 400 and rp['portion_source'] == 'pack_2portions'
        assert rp['multi_portion'] is True and rp['kcalPor'] == 456.0 and rp['protPor'] == 14.0 and rp['pPor'] == prpor
        assert rp['meal_class'] == 'light_meal' and rp['rankable'] is False and rp['rankableLight'] is False
        assert rp['rank_excluded_reason'] == 'Health-Score < 30'

    # 4. SC70 P2.3: 7 bofrost multi-portion items & 4 myProduct value packs
    for bid, por, kpor, ppor, prpor, mc in (
        (2621, 320, 752.0, 18.6, 7.25, 'light_meal'),
        (2624, 245, 531.6, 20.1, 6.75, 'meal'),
        (2636, 270, 723.6, 31.3, 6.39, 'meal'),
        (2637, 270, 796.5, 33.8, 6.39, 'meal'),
        (2939, 260, 720.2, 32.5, 7.75, 'meal'),
        (2969, 303, 745.4, 30.0, 5.75, 'meal'),
        (2982, 338, 662.5, 30.1, 6.39, 'meal'),
    ):
        rbf = by[bid]
        assert rbf['portion'] == por and rbf['portion_source'] == 'pack_2portions' and rbf['multi_portion'] is True
        assert rbf['kcalPor'] == kpor and rbf['protPor'] == ppor and rbf['pPor'] == prpor
        assert rbf['meal_class'] == mc and rbf['rankable'] is False and rbf['rankableLight'] is False
        assert rbf['rank_excluded_reason'] == 'Health-Score < 30'

    r3218 = by[3218]
    assert r3218['portion'] == 108 and r3218['portion_source'] == 'multipack_unit' and r3218['multi_portion'] is True
    assert r3218['pPor'] == 3.79 and r3218['pPorEff'] == 5.11 and r3218['kcalPor'] == 331.6 and r3218['protPor'] == 17.5
    for mpid, kpor, ppor in ((3224, 298.4, 6.0), (3225, 295.8, 6.5), (3226, 300.1, 6.3)):
        rmp = by[mpid]
        assert rmp['portion'] == 85 and rmp['portion_source'] == 'multipack_unit' and rmp['multi_portion'] is True
        assert rmp['pPor'] == 2.39 and rmp['pPorEff'] == 3.71 and rmp['kcalPor'] == kpor and rmp['protPor'] == ppor

    # 5. SC70 P3.2: Rows with portion is None must have None for pPor, pPorEff, protPor, kcalPor, kcal_meal, saltPor, saltPct
    for r in d['rows']:
        if r.get('portion') is None:
            for k in ('pPor', 'pPorEff', 'protPor', 'kcalPor', 'kcal_meal', 'saltPor', 'saltPct'):
                assert r.get(k) is None, f"Row #{r['id']} has portion=None but {k}={r.get(k)}"

    # 6. Totals & invariants
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 200
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
    assert [r['id'] for r in d['rows'] if r.get('stage') == 'meal' and r.get('component')] == []
    assert [
        r['id'] for r in d['rows']
        if not r.get('rankable') and not r.get('rankableLight') and r.get('dupOf') is None and not r.get('rank_excluded_reason')
    ] == []


def test_sc70_off_switch_reproduces_sc69_bit_for_bit(tmp_path):
    for env_kw in ({'SC70_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC70': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == '5652b8975c85'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 196
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
