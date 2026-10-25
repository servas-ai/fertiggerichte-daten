import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'
MEAT_PROT = {'Ripperl/Spareribs', 'Huhn', 'Pute', 'Rind', 'Schwein', 'Lamm', 'Wild', 'Fisch', 'Meeresfrüchte', 'Ente'}
NON_LINZ = {'Gurkerl', 'MPreis', 'Alfies'}


def _export(tmp_path, snap=SNAP, **env):
    os.makedirs(tmp_path, exist_ok=True)
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc79_p11_plant_based_protected_and_chili_sin_carne_vegan(tmp_path):
    d = _export(tmp_path, SNAP)
    rows = d['rows']
    by = {r['id']: r for r in rows}

    # All Chili sin Carne rows must be vegan + Hülsenfrüchte and never meat
    sin_carne = [r for r in rows if re.search(r'\bsin\s+carne\b', r.get('name', ''), re.I)]
    assert len(sin_carne) >= 18
    for r in sin_carne:
        cp = set(r.get('cprot') or [])
        assert r.get('vegan') is True, f"#{r['id']} {r['name']} should be vegan=True"
        assert 'vegan' in cp and 'Hülsenfrüchte' in cp, f"#{r['id']} {r['name']} missing vegan/Hülsenfrüchte: {cp}"
        assert not (cp & MEAT_PROT), f"#{r['id']} {r['name']} has meat tag: {cp}"

    # Spot-check SC79 P1.1 examples
    for rid in (155, 458, 1256, 1259):
        assert by[rid]['vegan'] is True
        assert 'Hülsenfrüchte' in by[rid]['cprot'] and 'vegan' in by[rid]['cprot']
        assert not (set(by[rid]['cprot']) & MEAT_PROT)

    # Plant-based chicken/meat substitutes and Muschelnudeln
    assert by[1278]['cprot'] == ['Seitan/Fleischersatz', 'vegan'] and by[1278]['vegan'] is True
    assert by[2563]['cprot'] == ['Seitan/Fleischersatz', 'vegan'] and by[2563]['vegan'] is True
    assert by[2914]['cprot'] == ['Seitan/Fleischersatz', 'vegan'] and by[2914]['vegan'] is True
    assert 'Meeresfrüchte' not in by[891]['cprot'] and 'vegetarisch' in by[891]['cprot']

    # Zero vegan/vegetarisch rows carry meat/fish tags
    for r in rows:
        cp = set(r.get('cprot') or [])
        if r.get('vegan') or 'vegan' in cp or 'vegetarisch' in cp:
            assert not (cp & MEAT_PROT), f"Plant-based row #{r['id']} {r['name']} has meat tag: {cp}"


def test_sc79_p31_linz_supermarkets_have_zero_ohne_marke(tmp_path):
    d = _export(tmp_path, SNAP)
    rows = d['rows']
    by = {r['id']: r for r in rows}

    linz_unbranded = [
        r['id'] for r in rows
        if r.get('dupOf') is None and not r.get('nonfood') and r.get('delivers_4020') is not False and not str(r.get('store', '')).startswith('unbekannt')
        and (r.get('noBrand') or not (r.get('brand') or '').strip() or (r.get('brandN') or '').strip() in ('(ohne Marke)', 'Ohne Marke', ''))
    ]
    assert linz_unbranded == []

    # Spot-check assigned brands & own-brand metadata
    assert by[1170]['brand'] == 'Good Choice' and by[1170]['brandParent'] == 'Hofer' and by[1170]['noBrand'] is False
    assert by[1188]['brand'] == 'Natur aktiv' and by[1188]['brandParent'] == 'Hofer' and by[1188]['noBrand'] is False
    assert by[1193]['brand'] == 'Genuss aus Österreich' and by[1193]['brandParent'] == 'Hofer' and by[1193]['noBrand'] is False
    assert by[1325]['brand'] == 'BILLA' and by[1325]['brandParent'] == 'Billa' and by[1325]['noBrand'] is False
    assert by[2559]['brand'] == 'Die Grillerei' and by[2559]['brandParent'] == 'Billa' and by[2559]['noBrand'] is False
    assert by[3465]['brand'] == 'Penny Ready' and by[3465]['brandParent'] == 'Penny' and by[3465]['noBrand'] is False


def test_sc79_p12_analysis_jsons_in_sync_with_current_data(tmp_path):
    analysis_tmp = tmp_path / 'analysis'
    d = _export(tmp_path, SNAP, GOOD_CHOICE_REGEN_ANALYSIS='1', GOOD_CHOICE_ANALYSIS_DIR=str(analysis_tmp))
    by = {r['id']: r for r in d['rows']}

    # 1. packaging_v2.json
    pkg = json.load(open(analysis_tmp / 'packaging_v2.json'))
    pkg_by_type = {t['type']: t for t in pkg['types']}
    assert 'dm' in pkg_by_type['Pouch/Retort']['stores']
    assert pkg_by_type['Pouch/Retort']['stats']['n_rankable'] >= 5
    for t in pkg['types']:
        assert not (NON_LINZ & set(t['stores'])), f"Non-Linz store in {t['type']}: {t['stores']}"
        for item in t['top']:
            r = by[item['id']]
            assert r['name'] == item['name'] and r['uid'] == item['uid']

    # 2. brands.json
    br = json.load(open(analysis_tmp / 'brands.json'))
    for b in br['brands']:
        assert b['brand'] not in ('Stangl', 'Barilla', 'Mamia', 'Hipp', 'HiPP', 'Holle')
        for k in ('cheapest', 'best_protein_value'):
            if b.get(k):
                r = by[b[k]['id']]
                assert r['name'] == b[k]['name'] and r['uid'] == b[k]['uid']
                assert r.get('stage') in ('meal', 'stew') and not r.get('nonfood')

    # 3. producers_nutrients.json
    pn = json.load(open(analysis_tmp / 'producers_nutrients.json'))
    for item in pn['pareto_health_vs_protein_per_euro'] + pn['traps']['expensive_low_protein'] + pn['traps']['salt_bombs'] + pn['traps']['best_protein_per_euro']:
        r = by[item['id']]
        assert r['name'] == item['name'] and r['uid'] == item['uid']
        assert r.get('stage') in ('meal', 'stew') and not r.get('nonfood')

    # 4. chains_categories.json
    cc = json.load(open(analysis_tmp / 'chains_categories.json'))
    for m_cat in ('Ripperl', 'Pute', 'Huhn', 'Fisch', 'Rind', 'Schwein'):
        assert cc['heatmap_chain_category']['counts']['dm'][m_cat] == 0
    for cat, bmap in cc['best_per_category'].items():
        for k, item in bmap.items():
            r = by[item['id']]
            assert r['name'] == item['name'] and r['uid'] == item['uid']

    assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 156
    assert d['dataVersion'] == '4147f1af8324'


def test_sc79_fixes_off_switch_reproduces_sc78(tmp_path):
    d_off = _export(tmp_path / 'off', SNAP, SC79_FIXES='0')
    assert d_off['dataVersion'] == '381633b31413'
    assert sum(1 for r in d_off['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d_off['rows'] if r.get('rankableLight')) == 156

    d_dis = _export(tmp_path / 'dis', SNAP, GOOD_CHOICE_DISABLE_SC79='1')
    assert d_dis['dataVersion'] == '381633b31413'
