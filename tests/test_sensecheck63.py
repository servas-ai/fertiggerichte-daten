import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, SC64_FIXES='0', **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc63_p1b_p2b_p2c_p3(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. P1b.1: Gnocchi & Spätzle Ready Meals (#1489, #3054, #3015, #4005, #4025)
    for rid in (1489, 3054, 3015, 4005, 4025):
        r = by[rid]
        assert r['stage'] == 'meal' and r['gang'] == 'haupt' and r['component'] is False
        assert r['meal_class'] == 'light_meal' and r['meal_check']['cls'] == 'light_meal'
    assert by[1489]['rankableLight'] is True and by[1489]['pliLight'] == 30.4

    # 2. P1b.2: Dishes in sauce & Bratnudeln (#2931, #2335, #2336, #2345, #2346, #2948)
    for rid in (2931, 2335, 2336, 2345, 2346, 2948):
        r = by[rid]
        assert r['stage'] == 'meal' and r['gang'] == 'haupt' and r['component'] is False
        assert r['meal_class'] == 'light_meal' and r['meal_check']['cls'] == 'light_meal'
    assert by[2335]['rankableLight'] is True and by[2335]['pliLight'] == 29.7 and by[2335]['ean'] == '9008615514241'
    assert by[2336]['rankableLight'] is True and by[2336]['pliLight'] == 33.3 and by[2336]['ean'] == '9008615514234'
    assert by[2948]['rankableLight'] is True and by[2948]['pliLight'] == 21.7

    # 3. P1b.3: Sushi boxes, stews, salads, noodle pouches, canned ravioli & #3467/#3728/#3763
    assert by[887]['stage'] == 'meal' and by[887]['component'] is False and by[887]['rankableLight'] is True and by[887]['pliLight'] == 23.1
    assert by[873]['stage'] == 'meal' and by[873]['component'] is False and by[873]['meal_class'] == 'meal' and by[873]['rankable'] is False
    assert by[3356]['stage'] == 'stew' and by[3356]['component'] is False and by[3356]['meal_class'] == 'light_meal'
    assert by[3317]['stage'] == 'meal' and by[3317]['component'] is False and by[3317]['meal_class'] == 'light_meal'
    for rid in (2327, 2572, 2573):
        r = by[rid]
        assert r['stage'] == 'meal' and r['component'] is False and r['dry'] is False and r['meal_class'] == 'light_meal'
        assert not any('Trockenprodukt' in f for f in (r.get('flags') or []))
    for rid in (61, 902, 958, 1586, 1763, 1781, 1823, 2005):
        r = by[rid]
        assert r['stage'] == 'meal' and r['gang'] == 'haupt' and r['component'] is False and r['meal_class'] == 'light_meal'
    for rid in (3467, 3728, 3763):
        assert by[rid]['stage'] == 'meal' and by[rid]['component'] is False

    # 4. P1a invariant still holds across all stage in ('base', 'side', 'veg')
    bad_p1a = [
        r['id'] for r in d['rows']
        if r.get('stage') in ('base', 'side', 'veg')
        and (
            r.get('meal_class') in ('meal', 'light_meal')
            or not r.get('component')
            or r.get('rankable')
            or r.get('rankableLight')
        )
    ]
    assert bad_p1a == []

    # 5. P2b.1: Demoted nonfood, spices, soup greens/bones, popcorn, tahina, Back-Camembert & desserts
    assert by[321]['nonfood'] is True and by[321]['stage'] == 'base' and by[321]['component'] is True
    for rid in (162, 207, 272, 275, 276, 277, 412):
        assert by[rid]['stage'] == 'base' and by[rid]['dry'] is True and by[rid]['meal_class'] == 'dry'
    for rid in (179, 250, 198, 73, 18):
        assert by[rid]['stage'] == 'base' and by[rid]['component'] is True and by[rid]['meal_class'] == 'raw_ingredient'
    for rid in (3178, 3960):
        assert by[rid]['stage'] == 'base' and by[rid]['component'] is True and by[rid]['meal_class'] == 'condiment_or_base'
    for rid in (316, 317, 318):
        assert by[rid]['stage'] == 'side' and by[rid]['gang'] == 'snack' and by[rid]['meal_class'] == 'snack_side'
    for rid in (3923, 3623, 3624, 3625, 3626):
        assert by[rid]['stage'] == 'prot' and by[rid]['component'] is True and by[rid]['meal_class'] == 'protein_component'
    for rid in (3258, 3329, 3399, 3400, 3401, 3365, 3366, 3381, 3395, 3396):
        assert by[rid]['gang'] == 'dessert' and by[rid]['meal_class'] == 'dessert' and by[rid]['rankable'] is False

    # 6. P2b.2: Zero stage == 'prot' rows may have meal_class in ('meal', 'light_meal', 'multi_portion', 'unknown', 'snack_side')
    bad_prot = [
        r['id'] for r in d['rows']
        if r.get('stage') == 'prot'
        and (
            not r.get('component')
            or r.get('meal_class') not in ('protein_component', 'raw_ingredient', 'dry', 'baby', 'dessert')
            or r.get('rankable')
            or r.get('rankableLight')
        )
    ]
    assert bad_prot == []

    # 7. P2c: #2670 vs #2416 Spar Dr. Oetker Ristorante Pizza Tonno
    assert by[2670]['rankable'] is True and by[2670]['pli'] == 47.7
    assert by[2670]['variant_note'] == 'auch als Einzelpackung (355 g)' and by[2670]['variantIds'] == [2416]
    assert by[2416]['rankable'] is False and by[2416]['pli'] is None
    assert by[2416]['rank_excluded_reason'] == 'Duplikat (nahe Name/Marke, Ranking)'
    assert 'Duplikat (nahe Name/Marke, Ranking)' in (by[2416].get('flags') or [])

    # 8. P3.2: #530 Billa Clever Lasagne Bolognese (1000 g) -> meal_class = 'multi_portion'
    assert by[530]['meal_class'] == 'multi_portion' and by[530]['meal_check']['cls'] == 'multi_portion'

    # 9. Totals and dataVersion
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 186
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 110
    assert d['dataVersion'] == 'c934224654b7'


def test_sc63_off_switch_reproduces_sc62_bit_for_bit(tmp_path):
    for env_kw in ({'SC63_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC63': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == '4644adb26ffa'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 187
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 105
