import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC73_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc72_p0_1_p0_2_and_p0_3(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC72 P0.1: #2206 [Denn's] MyDeli Bio-Hühnersuppe (Art. 564131, EAN 4012344902014, 380 g, 3.99 €)
    r2206 = by[2206]
    assert r2206['store'] == "Denn's"
    assert r2206['name'] == 'MyDeli Bio-Hühnersuppe'
    assert r2206['ean'] == '4012344902014'
    assert r2206['kcal'] == 25.0 and r2206['p100'] == 3.4
    assert r2206['fat'] == 0.4 and r2206['sat'] == 0.2 and r2206['carbs'] == 2.1 and r2206['sugar'] == 1.1 and r2206['salt'] == 1.55
    assert r2206['veg_pct'] == 14.0 and r2206['nova'] == 3
    assert r2206['size'] == 380.0 and r2206['portion'] == 380 and r2206['portion_source'] == 'pack_single'
    assert r2206['kcalPor'] == 95.0 and r2206['protPor'] == 12.9 and r2206['saltPor'] == 5.89 and r2206['saltPct'] == 98
    assert r2206['pPor'] == 3.99 and r2206['pPorEff'] is None
    assert r2206['score'] == 46.9
    assert r2206['stage'] == 'stew' and r2206['gang'] == 'vorspeise' and r2206['meal_class'] == 'snack_side'
    assert r2206['component'] is False
    assert r2206['rankable'] is False and r2206['pli'] is None
    assert r2206['rankableLight'] is False and r2206['pliLight'] is None
    assert r2206['rank_excluded_reason'] == '95 kcal/Portion – Snack/Beilage'
    assert r2206['flags'] == ['Mahlzeit-Check: 95 kcal/Portion – Snack/Beilage']
    assert '564131' in (r2206.get('variant_note') or '') and '4012344902014' in (r2206.get('variant_note') or '')
    assert 2206 not in d['topLight'] and 2206 not in d['topLightUncapped']
    assert d['topLight'][0] == 548

    # 2. SC72 P0.2: #2205 [Denn's] SOTO Veganes / Vegetarisches Bio-Fingerfood (SOTO Bio Falafel Traditionell 200 g)
    r2205 = by[2205]
    assert r2205['store'] == "Denn's"
    assert r2205['ean'] == '4026584133640'
    assert r2205['stage'] == 'prot' and r2205['meal_class'] == 'protein_component' and r2205['component'] is True
    assert r2205['rankable'] is False and r2205['pli'] is None
    assert r2205['rankableLight'] is False and r2205['pliLight'] is None
    assert r2205['rank_excluded_reason'] == 'Proteinkomponente (keine vollständige Mahlzeit)'
    assert r2205['flags'] == ['Mahlzeit-Check: Proteinkomponente (keine vollständige Mahlzeit)']
    assert 2205 not in d['topPLI'] and 2205 not in d['topPLIUncapped']
    # Consistent with all 12 other Falafel packs in data.json
    for fid in (648, 657, 2342, 3249, 3250, 3252, 3253, 3254, 3255, 3367, 3383, 3524):
        rf = by[fid]
        assert rf['stage'] == 'prot' and rf['meal_class'] == 'protein_component' and rf['component'] is True
        assert rf['rankable'] is False

    # 3. SC72 P0.3: All 5 Denn's products carry verified product images (100% photo coverage for Denn's)
    assert by[2204]['img'] == by[2040]['img'] and by[2204]['img'].startswith('https://cdn.gurkerl.at/')
    assert by[2205]['img'].startswith('https://images.openfoodfacts.org/images/products/402/658/413/3640/')
    assert by[2206]['img'].startswith('https://images.openfoodfacts.org/images/products/401/234/490/2014/')
    denns_rows = [r for r in d['rows'] if r.get('store') == "Denn's" and not r.get('nonfood')]
    assert len(denns_rows) == 5 and all(r.get('img') for r in denns_rows)

    # 4. Totals & invariants
    assert d['dataVersion'] == 'd4f919f69d38'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 208
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
    assert [i for i, r in enumerate(d['rows']) if r.get('id') != i] == []
    assert [r['id'] for r in d['rows'] if r.get('stage') == 'meal' and r.get('component')] == []
    assert [
        r['id'] for r in d['rows']
        if not r.get('rankable') and not r.get('rankableLight') and r.get('dupOf') is None and not r.get('rank_excluded_reason')
    ] == []


def test_sc72_off_switch_reproduces_sc71_bit_for_bit(tmp_path):
    for env_kw in ({'SC72_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC72': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == '21d092e2d842'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 209
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 156
