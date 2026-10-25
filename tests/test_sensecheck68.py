import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc68_p1_1_p2_1_p2_2_and_p3_1(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC68 P1.1: Rescue 2 Billa meals in Linz (#1067, #1478) + bidirectional alsoPack on Spar Weinbeuschel (#431 <-> #432)
    r1067 = by[1067]
    assert r1067['store'] == 'Billa' and r1067['stage'] == 'meal' and r1067['segment'] == 'ready_meal'
    assert r1067['meal_class'] == 'meal' and r1067['gang'] == 'haupt' and r1067['component'] is False
    assert r1067['rankable'] is True and r1067['rankableLight'] is False
    assert r1067['pli'] == 31.6 and r1067['pliLight'] is None and r1067.get('rank_excluded_reason') is None

    r1478 = by[1478]
    assert r1478['store'] == 'Billa' and r1478['portion'] == 300 and r1478['portion_g'] == 300
    assert r1478['portion_source'] == 'pack_2portions'
    assert r1478['kcalPor'] == 456.0 and r1478['protPor'] == 23.1 and r1478['pPor'] == 4.25 and r1478['pPorEff'] == 4.25
    assert r1478['stage'] == 'meal' and r1478['segment'] == 'ready_meal' and r1478['meal_class'] == 'meal'
    assert r1478['component'] is False and r1478['rankable'] is True and r1478['pli'] == 28.7 and r1478.get('rank_excluded_reason') is None

    r431, r432 = by[431], by[432]
    assert any(p.get('id') == 432 and p.get('sameStore') is True and p.get('kind') == 'size' for p in (r431.get('alsoPack') or []))
    assert any(p.get('id') == 431 and p.get('sameStore') is True and p.get('kind') == 'size' for p in (r432.get('alsoPack') or []))

    # 2. SC68 P2.1: Zero active live 2026 rows have stage == 'meal' and component == True
    contra_meal_comp = [
        r['id'] for r in d['rows']
        if r.get('pstat') == 'live 2026' and r.get('dupOf') is None and r.get('stage') == 'meal' and r.get('component')
    ]
    assert contra_meal_comp == []
    for pid in (662, 867, 1288, 1332, 2082, 2440, 2503, 2504, 2506, 2535, 2952, 3387, 3896):
        assert by[pid]['stage'] == 'prot' and by[pid]['meal_class'] == 'protein_component' and by[pid]['component'] is True
    for cid in (438, 1337, 1517, 1546, 1676, 1807, 3251, 594, 1279, 1748, 2502, 3540):
        assert by[cid]['stage'] == 'meal' and by[cid]['component'] is False
        assert 'Proteinkomponente' not in (by[cid].get('rank_excluded_reason') or '')
        assert not any('Proteinkomponente' in f for f in (by[cid].get('flags') or []))

    # 3. SC68 P2.2: 5 bofrost twin-pack pizzas normalized to 1 pizza per portion (2 portions)
    for pz_id, por, kpor, ppor, prpor, pli in (
        (2968, 376, 778.5, 39.5, 6.75, 34.1),
        (2966, 419, 884.0, 46.1, 6.75, 33.9),
        (2967, 416, 844.5, 40.0, 6.75, 30.8),
        (2970, 370, 766.0, 37.8, 6.5,  30.7),
        (3052, 397, 774.0, 33.4, 6.75, 27.8),
    ):
        rpz = by[pz_id]
        assert rpz['portion'] == por and rpz['portion_g'] == por and rpz['portion_source'] == 'pack_2portions'
        assert rpz['kcalPor'] == kpor and rpz['protPor'] == ppor and rpz['pPor'] == prpor
        assert rpz['meal_class'] == 'meal' and rpz['rankable'] is True and rpz['pli'] == pli and rpz.get('rank_excluded_reason') is None

    # 4. SC68 P3.1: Side/veg/sauce rows (#44, #660, #1282, #1284, #1339, #3159, #3379, #3669) have side-dish reason and zero whitespace artefacts
    for sid in (44, 660, 1282, 1284, 1339, 3159, 3379, 3669):
        assert by[sid]['rank_excluded_reason'] == 'Snack / Beilage (keine Hauptmahlzeit)'
    ws_rer = [r['id'] for r in d['rows'] if isinstance(r.get('rank_excluded_reason'), str) and (r['rank_excluded_reason'] != r['rank_excluded_reason'].strip() or '  ' in r['rank_excluded_reason'])]
    ws_flg = [r['id'] for r in d['rows'] if any(isinstance(f, str) and (f != f.strip() or '  ' in f) for f in (r.get('flags') or []))]
    assert ws_rer == [] and ws_flg == []

    # 5. Totals & dataVersion
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 192
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 152
    assert d['dataVersion'] == 'bc6cbb567dc7'

    # 6. SC68 P3.1: All 54 live=None rows have rank_excluded_reason == 'Kein aktueller Preis 2026' (0 unranked dupOf=None rows without reason)
    missing_rer = [
        r['id'] for r in d['rows']
        if not r.get('rankable') and not r.get('rankableLight') and r.get('dupOf') is None and not r.get('rank_excluded_reason')
    ]
    assert missing_rer == []
    live_none_rer = [
        r['id'] for r in d['rows']
        if r.get('dupOf') is None and r.get('live') is None and r.get('rank_excluded_reason') == 'Kein aktueller Preis 2026'
    ]
    assert len(live_none_rer) == 54

    # 7. SC68 P2.3: online_providers.json (bofrost store match, every. delivers_linz=None, FitTaste card)
    op = json.load(open(os.path.join(ROOT, 'analysis', 'online_providers.json')))
    by_name = {p['name']: p for p in op['providers']}
    assert by_name['bofrost*']['store'] == 'Online: bofrost' and by_name['bofrost*']['delivers_linz'] is True
    assert by_name['every.']['delivers_linz'] is None
    assert 'FitTaste' in by_name and by_name['FitTaste']['store'] == 'Online: FitTaste' and by_name['FitTaste']['delivers_linz'] is True


def test_sc68_off_switch_reproduces_sc67_bit_for_bit(tmp_path):
    for env_kw in ({'SC68_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC68': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == '684af70ab124'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 185
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 152
