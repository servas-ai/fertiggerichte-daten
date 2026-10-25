import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PUB = '/workspace/fertig-app/public'
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC70_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc69_p1_2_p2_and_p3(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC69 P1.2: Chain normalization in stores_linz_walk.json, stores_linz_providers.json, stores_linz_2026-10-13.json
    for walk_path in (
        os.path.join(ROOT, 'stores_walk', 'stores_linz_walk.json'),
        os.path.join(APP_PUB, 'stores_linz_walk.json'),
    ):
        wk = json.load(open(walk_path))
        by_osm = {s['osm']: s for s in wk['stores']}
        assert by_osm['node/3150023279']['chain'] == "Denn's"
        assert by_osm['node/3150023279']['type'] == 'chain'
        assert by_osm['node/3150023279']['availability_level'] == 'chain'
        assert by_osm['node/3677955200']['chain'] == "Denn's"
        assert by_osm['node/8062586934']['chain'] == 'Nah&Frisch'
        assert by_osm['node/8062586934']['type'] == 'chain'
        assert by_osm['node/8062586934']['availability_level'] == 'chain'

    prov = json.load(open(os.path.join(APP_PUB, 'stores_linz_providers.json')))
    nordsee_chains = {s['chain'] for s in prov['stores'] if 'nordsee' in (s.get('name') or '').lower()}
    assert nordsee_chains == {'NORDSEE'}

    s13 = json.load(open(os.path.join(APP_PUB, 'stores_linz_2026-10-13.json')))
    denns_chains = {s.get('chain') for s in s13['stores'] if 'denn' in (s.get('name') or '').lower()}
    assert denns_chains == {"Denn's"}

    # 2. SC69 P2.1: 4 dm jars/pouches with off_serving artefacts normalized to pack_single
    r1256 = by[1256]
    assert r1256['store'] == 'dm' and r1256['portion'] == 400 and r1256['portion_source'] == 'pack_single'
    assert r1256['kcalPor'] == 280.0 and r1256['protPor'] == 20.4 and r1256['pPor'] == 2.35 and r1256['pPorEff'] == 2.35
    assert r1256['meal_class'] == 'light_meal' and r1256['rankable'] is False and r1256['rankableLight'] is True
    assert r1256['pliLight'] == 50.5 and r1256.get('rank_excluded_reason') is None

    r1258 = by[1258]
    assert r1258['store'] == 'dm' and r1258['portion'] == 375 and r1258['portion_source'] == 'pack_single'
    assert r1258['kcalPor'] == 442.5 and r1258['protPor'] == 17.25 and r1258['pPor'] == 2.95 and r1258['pPorEff'] == 2.95
    assert r1258['meal_class'] == 'light_meal' and r1258['rankable'] is False and r1258['rankableLight'] is True
    assert r1258['pliLight'] == 34.0 and r1258.get('rank_excluded_reason') is None

    r1269 = by[1269]
    assert r1269['store'] == 'dm' and r1269['portion'] == 350 and r1269['portion_source'] == 'pack_single'
    assert r1269['kcalPor'] == 175.0 and r1269['protPor'] == 3.9 and r1269['meal_class'] == 'snack_side'
    assert r1269['rankable'] is False and r1269['rankableLight'] is False
    assert r1269['rank_excluded_reason'] == '175 kcal/Portion – Snack/Beilage'

    r2087 = by[2087]
    assert r2087['store'] == 'dm' and r2087['portion'] == 250 and r2087['portion_source'] == 'pack_single'
    assert r2087['kcalPor'] == 282.5 and r2087['protPor'] == 7.0 and r2087['meal_class'] == 'light_meal'
    assert r2087['rankable'] is False and r2087['rankableLight'] is False
    assert r2087['rank_excluded_reason'] == '< 15 g Protein/Portion'

    # 3. SC69 P2.2: 6 Billa portion normalizations (+4 rankable, +1 rankableLight)
    for rid, por, psrc, kpor, ppor, prpor, pli in (
        (1018, 500, 'pack_single', 459.0, 30.5, 5.49, 38.2),
        (1016, 500, 'pack_single', 510.0, 27.0, 5.49, 29.9),
        (870,  500, 'pack_2portions', 585.0, 40.0, 9.0, 32.1),
        (871,  500, 'pack_2portions', 415.0, 35.0, 6.5, 35.1),
    ):
        rb = by[rid]
        assert rb['store'] == 'Billa' and rb['portion'] == por and rb['portion_source'] == psrc
        assert rb['kcalPor'] == kpor and rb['protPor'] == ppor and rb['pPor'] == prpor and rb['pPorEff'] == prpor
        assert rb['meal_class'] == 'meal' and rb['rankable'] is True and rb['rankableLight'] is False
        assert rb['pli'] == pli and rb.get('rank_excluded_reason') is None

    r563 = by[563]
    assert r563['store'] == 'Billa' and r563['portion'] == 200 and r563['portion_source'] == 'pack_2portions'
    assert r563['kcalPor'] == 312.0 and r563['protPor'] == 18.4 and r563['pPor'] == 2.0 and r563['pPorEff'] == 2.0
    assert r563['meal_class'] == 'light_meal' and r563['rankable'] is False and r563['rankableLight'] is True
    assert r563['pliLight'] == 45.2 and r563.get('rank_excluded_reason') is None

    r562 = by[562]
    assert r562['store'] == 'Billa' and r562['portion'] == 200 and r562['portion_source'] == 'pack_2portions'
    assert r562['kcalPor'] == 292.0 and r562['protPor'] == 10.2 and r562['pPor'] == 2.0
    assert r562['meal_class'] == 'light_meal' and r562['rankable'] is False and r562['rankableLight'] is False
    assert r562['rank_excluded_reason'] == '< 15 g Protein/Portion'

    # 4. SC69 P2.3: Remaining 5 bofrost twin-pack pizzas normalized to 2 portions
    for pz_id, por, kpor, ppor, prpor, mc, rer in (
        (2963, 360, 792.0, 36.0, 6.5,  'meal', 'Health-Score < 30'),
        (2964, 360, 741.5, 32.4, 6.5,  'meal', 'Health-Score < 30'),
        (2965, 383, 900.0, 45.2, 6.75, 'meal', 'Health-Score < 30'),
        (3053, 455, 987.5, 46.0, 6.75, 'multi_portion', '988 kcal/Portion > 900'),
        (3055, 480, 1027.0, 34.1, 6.0, 'multi_portion', '1027 kcal/Portion > 900'),
    ):
        rpz = by[pz_id]
        assert rpz['portion'] == por and rpz['portion_source'] == 'pack_2portions'
        assert rpz['kcalPor'] == kpor and rpz['protPor'] == ppor and rpz['pPor'] == prpor
        assert rpz['meal_class'] == mc and rpz['rankable'] is False and rpz['rankableLight'] is False
        assert rpz['rank_excluded_reason'] == rer

    # 5. SC69 P3.1: 3 pure burger patties without bun at Billa -> stage='prot', meal_class='protein_component'
    for pid in (2386, 2387, 3584):
        rp = by[pid]
        assert rp['stage'] == 'prot' and rp['meal_class'] == 'protein_component' and rp['component'] is True
        assert rp['rank_excluded_reason'] == 'Proteinkomponente (ohne Beilage) – nicht als Vollmahlzeit gerankt'

    # 6. SC69 P3.2: Zero rows across entire dataset (0/4049) have stage == 'meal' and component == True
    assert [r['id'] for r in d['rows'] if r.get('stage') == 'meal' and r.get('component')] == []
    for jid in (2887, 2903):
        assert by[jid]['stage'] == 'meal' and by[jid]['component'] is False
        assert by[jid]['rank_excluded_reason'] == 'Kein aktueller Preis 2026'

    # 7. SC69 P3.3: Cross-store duplicate hint strings updated after #1018/#1016/#871 rescue
    for did in (2001, 3882, 1806):
        assert by[did]['rank_excluded_reason'] == 'Online-Duplikat: Produkt auch in Linz (Billa), dort aber nicht rankbar (Health-Score 21,0 < 30)'
    for did in (2002, 3892, 1805):
        assert by[did]['rank_excluded_reason'] == 'Online-Duplikat: Produkt auch in Linz (Billa), dort aber nicht rankbar (Health-Score 29,6 < 30)'
    assert by[1987]['rank_excluded_reason'] == 'Online-Duplikat (gleiches Produkt in Linz bei Billa – dort gerankt)'

    # 8. Totals & dataVersion
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 196
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
    assert d['dataVersion'] == '5652b8975c85'
    assert [
        r['id'] for r in d['rows']
        if not r.get('rankable') and not r.get('rankableLight') and r.get('dupOf') is None and not r.get('rank_excluded_reason')
    ] == []


def test_sc69_off_switch_reproduces_sc68_bit_for_bit(tmp_path):
    for env_kw in ({'SC69_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC69': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == 'bc6cbb567dc7'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 192
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 152
