import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc64_p1_2_p2_2_p2_3_and_p3_2(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC63 P1.2(a): Zero incomplete rows may be rankable or rankableLight (#1447, #1454)
    bad_inc = [r['id'] for r in d['rows'] if r.get('incomplete') and (r.get('rankable') or r.get('rankableLight') or r.get('pli') is not None or r.get('pliLight') is not None)]
    assert bad_inc == []
    assert by[1447]['rankableLight'] is False and by[1447]['pliLight'] is None and by[1447]['meal_class'] == 'dessert'
    assert by[1454]['rankableLight'] is False and by[1454]['pliLight'] is None

    # 2. SC63 P1.2(b): Fingerfood snacks #564 (BILLA Mini Samosas) & #650 (BILLA Bio Quinoa Ecken) demoted to snack_side
    for rid in (564, 650):
        r = by[rid]
        assert r['stage'] == 'side' and r['gang'] == 'snack' and r['component'] is True
        assert r['meal_class'] == 'snack_side' and r['rankable'] is False and r['rankableLight'] is False

    # 3. SC63 P1.2(c): All 14 dead-zone light_meal ready meals (400-684 kcal, 15.8-19.6 g P, score >= 30.3) promoted to rankableLight=True
    expected_deadzone = (
        (5,    30.0),
        (587,  27.5),
        (863,  27.5),
        (864,  29.5),
        (1336, 21.5),
        (1497, 28.7),
        (2198, 31.8),
        (3385, 28.0),
        (2933, 26.1),
        (2935, 26.8),
        (2943, 27.3),
        (3140, 23.2),
        (3144, 21.6),
        (3207, 22.3),
    )
    for rid, exp_plil in expected_deadzone:
        r = by[rid]
        assert r['meal_class'] == 'light_meal'
        assert r['rankable'] is False and r['pli'] is None
        assert r['rankableLight'] is True and r['pliLight'] == exp_plil
        assert '(Light Meal)' in (r.get('rank_excluded_reason') or '')

    # 4. SC63 P2.2: variantIds deduplicated across all rows + 7 same-store pack-size duplicate pairs linked & demoted
    for r in d['rows']:
        vids = r.get('variantIds') or []
        assert len(vids) == len(set(vids)), f"Row #{r['id']} has duplicate variantIds: {vids}"
    assert by[2809]['variantIds'] == [2838]
    assert by[2850]['variantIds'] == [2855]

    for win_id, los_id, exp_note in (
        (432,  431,  'auch als Einzelportion (400 g)'),
        (1114, 1113, 'auch als Einzelportion (350 g)'),
        (2809, 2838, 'auch als Einzelportion (500 g)'),
        (2850, 2855, 'auch als Einzelportion (500 g)'),
        (1162, 96,   'auch als Einzelportion (400 g)'),
        (495,  2256, 'auch als Einzelportion (400 g)'),
        (1033, 959,  'auch als Einzelportion (400 g)'),
    ):
        w, l = by[win_id], by[los_id]
        assert w['variant_note'] == exp_note
        assert los_id in (w.get('variantIds') or [])
        assert w['rankable'] is True or w['rankableLight'] is True
        assert l['rankable'] is False and l['rankableLight'] is False
        assert l['pli'] is None and l['pliLight'] is None and l.get('badge') is None
        assert l['rank_excluded_reason'] == 'Duplikat (nahe Name/Marke, Ranking)'
        assert 'Duplikat (nahe Name/Marke, Ranking)' in (l.get('flags') or [])

    # 5. SC63 P2.3: bofrost & Alfies non-complete meal components have component=True
    for rid in (2940, 2941, 2643, 2647, 3964):
        assert by[rid]['stage'] == 'prot' and by[rid]['component'] is True and by[rid]['meal_class'] == 'protein_component'
    for rid in (2958, 3201, 2642, 3200, 3203, 4008, 4009):
        assert by[rid]['stage'] in ('side', 'veg') and by[rid]['component'] is True and by[rid]['meal_class'] == 'snack_side'
    assert by[3956]['stage'] == 'side' and by[3956]['gang'] == 'dessert' and by[3956]['component'] is True and by[3956]['meal_class'] == 'dessert'

    # 6. SC62 P3.2: #172 Spar S-BUDGET Lasagne Bolognese (1000 g) matches #530 Billa Clever Lasagne Bolognese (250 g label_portion, multi_portion)
    r172 = by[172]
    assert r172['portion'] == 250 and r172['portion_g'] == 250 and r172['portion_source'] == 'label_portion'
    assert r172['kcalPor'] == 347.5 and r172['protPor'] == 14.5 and r172['pPor'] == 1.0
    assert r172['meal_class'] == 'multi_portion' and r172['meal_check']['cls'] == 'multi_portion'
    assert r172['rankable'] is False and r172['rankableLight'] is False

    # Remaining 800-g 2-Portionen cans in Linz have 400 g portion_g & pack_2portions
    for rid in (936, 1002, 1014, 396, 1034, 1469):
        rc = by[rid]
        assert rc['portion'] == 400 and rc['portion_g'] == 400 and rc['portion_source'] == 'pack_2portions'
        assert not any('Mehrportionen-Packung' in f for f in (rc.get('flags') or []))

    # 7. Totals & dataVersion
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 180
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 121
    assert d['dataVersion'] == 'd252972a9be9'


def test_sc64_off_switch_reproduces_sc63_bit_for_bit(tmp_path):
    for env_kw in ({'SC64_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC64': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == 'c934224654b7'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 186
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 110
