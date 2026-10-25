import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC74_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc73_p0_penny_lidl_unverified_cleanup_and_p3_podravka_stage(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC73 P0.1 & P0.2: #1212 [Lidl] CHEF SELECT Lasagne Bolognese (1000 g)
    # lidl.at has no online price (hofer_lidl.json: price_eur=None) and OFF 4056489412359 has fib=None.
    r1212 = by[1212]
    assert r1212['store'] == 'Lidl'
    assert r1212['ean'] == '4056489412359'
    assert r1212['price'] is None
    assert r1212['price_status'] == 'unknown'
    assert r1212['fib'] is None
    assert r1212['veg_pct'] is None
    assert r1212['rankable'] is False
    assert r1212['pli'] is None
    assert r1212['rank_excluded_reason'] == 'Kein Preis hinterlegt'

    # 2. SC73 P0.1 & P0.2: #1537 [Penny] Condeli Lasagne* (800 g, 4.99 €)
    # Remove wrong mapping to German 400 g EAN 4337256372008 (Penny Ready, 25.2% Atwater error) and nova_source='estimate'.
    r1537 = by[1537]
    assert r1537['store'] == 'Penny'
    assert r1537['price'] == 4.99 and r1537['size'] == 800.0
    assert r1537['ean'] is None
    assert r1537['kcal'] is None and r1537['p100'] is None and r1537['fib'] is None and r1537['salt'] is None
    assert r1537['nova_source'] != 'estimate'
    assert r1537['incomplete'] is True
    assert r1537['rankable'] is False
    assert r1537['pli'] is None
    assert 'Score unvollständig' in (r1537.get('rank_excluded_reason') or '')

    # 3. SC73 P0.1 & P0.2: #1504 [Lidl] McEnnedy Crispy Chicken Burger (500 g, 4.99 €)
    # Remove non-existent GTIN 4056489149491 and unverified sat=1.5; classify chicken patties without buns as stage='prot', component=True.
    r1504 = by[1504]
    assert r1504['store'] == 'Lidl'
    assert r1504['price'] == 4.99 and r1504['size'] == 500.0
    assert r1504['ean'] is None
    assert r1504['sat'] is None
    assert r1504['stage'] == 'prot'
    assert r1504['meal_class'] == 'protein_component'
    assert r1504['component'] is True
    assert r1504['rankable'] is False
    assert r1504['pli'] is None

    # 4. SC73 P0.2: #1211 [Lidl] MCENNEDY Nudelauflauf Mac & Cheese (1000 g, 3.79 €)
    # Remove sat/sugar/fib/salt that are None in OFF 4056489149507 -> incomplete=True, rankable=False.
    r1211 = by[1211]
    assert r1211['store'] == 'Lidl'
    assert r1211['ean'] == '4056489149507'
    assert r1211['price'] == 3.79 and r1211['size'] == 1000.0
    assert r1211['kcal'] == 137.0 and r1211['p100'] == 4.8 and r1211['fat'] == 4.7 and r1211['carbs'] == 18.5
    assert r1211['sat'] is None and r1211['sugar'] is None and r1211['fib'] is None and r1211['salt'] is None
    assert r1211['incomplete'] is True
    assert r1211['rankable'] is False
    assert r1211['pli'] is None
    assert 'Score unvollständig' in (r1211.get('rank_excluded_reason') or '')

    # 5. SC73 P3.1: #2236 [Penny] Podravka Rindergulasch 400 g (4.99 €)
    # Keep as verified rankable=True and stage='stew' (matching #88, #551, #956).
    r2236 = by[2236]
    assert r2236['store'] == 'Penny'
    assert r2236['ean'] == '3850104020032'
    assert r2236['price'] == 4.99
    assert r2236['fib'] is None
    assert r2236['nova_source'] == 'ingredients_markers'
    assert r2236['stage'] == 'stew'
    assert r2236['rankable'] is True
    assert r2236['pli'] == 37.1

    # 6. Global gates: zero nova_source='estimate' across all 4,049 rows, and zero severe Atwater under-reports (< 0.80 * kcal) on ranked rows
    est_nova = [r['id'] for r in d['rows'] if r.get('nova_source') == 'estimate']
    assert est_nova == [], f"Unexpected nova_source='estimate' rows: {est_nova}"

    for r in d['rows']:
        if r.get('rankable'):
            atw = 4.0 * (r['p100'] or 0) + 9.0 * (r['fat'] or 0) + 4.0 * (r['carbs'] or 0) + 2.0 * (r.get('fib') or 0)
            assert atw >= 0.80 * r['kcal'], f"Ranked row #{r['id']} ({r['name']}) fails Atwater check: {atw:.1f} vs {r['kcal']} kcal"

    rankable = [r for r in d['rows'] if r.get('rankable')]
    rankable_light = [r for r in d['rows'] if r.get('rankableLight')]
    assert len(rankable) == 206
    assert len(rankable_light) == 155


def test_sc73_p1_1_and_p1_2_linz_stores():
    # 1. walk.py uses word-boundary regex and excludes trafik/tankstelle/apotheke
    walk_py = open(os.path.join(ROOT, 'stores_walk', 'walk.py')).read()
    assert r'\b(trafik|tankstelle|apotheke)\b' in walk_py
    assert r'\b{re.escape(c.lower())}\b' in walk_py

    # 2. stores_linz_walk.json: no Zeitlhofer/Trafik tagged as Hofer, no duplicate Spar Holzstraße 13, all 11 chain branches <=2km have street addresses
    for rel in ['stores_walk/stores_linz_walk.json', 'stores_linz_walk.json']:
        dw = json.load(open(os.path.join(ROOT, rel)))
        by_osm = {s['osm']: s for s in dw['stores']}
        assert 'node/737157872' in by_osm
        zeitl = by_osm['node/737157872']
        assert zeitl['name'] == 'Tabak Trafik Zeitlhofer Michael'
        assert zeitl['chain'] is None
        assert zeitl['type'] != 'chain'

        for s in dw['stores']:
            if s.get('chain'):
                assert not re.search(r'\b(trafik|tankstelle|apotheke)\b', (s.get('name') or '').lower()), f"False chain store: {s}"

        # Deduplicated Spar Holzstraße 13 (way/112573309 kept with address, way/37655226 removed)
        assert 'way/37655226' not in by_osm
        assert 'way/93055919' not in by_osm
        assert by_osm['way/112573309']['addr'] == 'Holzstraße 13, 4020 Linz'
        assert by_osm['node/10839691328']['addr'] == 'Holzstraße 15, 4020 Linz'
        assert by_osm['node/2309636166']['addr'] == 'Lederergasse 33b, 4020 Linz'
        assert by_osm['node/1566303942']['addr'] == 'Eisenhandstraße 42, 4020 Linz'
        assert by_osm['node/10102892642']['addr'] == 'Landstraße 12, 4020 Linz'
        assert by_osm['node/527809213']['addr'] == 'Blütenstraße 15, 4040 Linz'

        chain_stores_2km = [s for s in dw['stores'] if s.get('chain') and s.get('dist_m', 9999) <= 1300]
        missing_addr = [s['osm'] for s in chain_stores_2km if not (s.get('addr') or '').strip()]
        assert missing_addr == [], f"Chain stores <=2km missing addr: {missing_addr}"

    # 3. stores_linz_2026-10-13.json: osm_id 456359594 (Nah & Frisch) tagged as 'Nah&Frisch', not 'Unimarkt'
    dl = json.load(open(os.path.join(ROOT, 'stores_linz_2026-10-13.json')))
    s456 = next(s for s in dl['stores'] if s.get('osm_id') == 456359594)
    assert s456['name'] == 'Nah & Frisch'
    assert s456['chain'] == 'Nah&Frisch'


def test_sc73_off_switch_reproduces_sc72(tmp_path):
    d_off = _export(tmp_path, SNAP, SC73_FIXES='0')
    assert d_off['dataVersion'] == 'd4f919f69d38'
    assert sum(1 for r in d_off['rows'] if r.get('rankable')) == 208
    assert sum(1 for r in d_off['rows'] if r.get('rankableLight')) == 155

    d_off2 = _export(tmp_path, SNAP, GOOD_CHOICE_DISABLE_SC73='1')
    assert d_off2['dataVersion'] == 'd4f919f69d38'
