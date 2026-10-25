import json, os, subprocess, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'
NON_LINZ = {'Gurkerl', 'MPreis', 'Alfies', 'every.'}
SUPERMARKETS = {'Billa', 'Spar', 'Hofer', 'Lidl', 'dm', 'Penny'}


def _export(tmp_path, snap=SNAP, **env):
    os.makedirs(tmp_path, exist_ok=True)
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc78_p12_also_at_and_also_pack_clean_in_linz(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    for r in d['rows']:
        if r.get('delivers_4020') is not False:
            aa = r.get('alsoAt') or []
            assert not (set(aa) & NON_LINZ), f"Linz row #{r['id']} has non-Linz store in alsoAt: {aa}"
            if 'alsoAt' in r:
                assert len(r['alsoAt']) > 0, f"Empty alsoAt should be omitted on #{r['id']}"

            ap = r.get('alsoPack') or []
            for p in ap:
                if not p.get('sameStore'):
                    assert p.get('store') not in NON_LINZ, f"Linz row #{r['id']} has non-Linz store in alsoPack: {p}"
                    assert (by.get(p.get('id')) or {}).get('delivers_4020') is not False
            if 'alsoPack' in r:
                assert len(r['alsoPack']) > 0, f"Empty alsoPack should be omitted on #{r['id']}"

    # Spot-check SC78 P1.2 examples
    assert 'alsoAt' not in by[23]
    assert by[25].get('alsoAt') == ['Spar']
    assert by[29].get('alsoAt') == ['Spar']
    assert 'alsoAt' not in by[453]
    assert 'alsoAt' not in by[2335]
    assert 'alsoAt' not in by[2336]
    assert [p['store'] for p in by[495].get('alsoPack', [])] == ['Billa', 'Spar']


def test_sc78_p21_combos_strictly_4020_with_supermarket_mains(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}
    sides = {s['id']: s for s in d['sides']}
    combos = d['combos']

    assert len(combos) == 24
    super_cnt = 0
    for c in combos:
        m = by[c['main']]
        assert m.get('dupOf') is None
        assert m.get('delivers_4020') is not False
        assert m.get('store') not in NON_LINZ
        assert not m.get('price_stale') and m.get('pstat') != 'Preis veraltet'
        assert (m.get('price') or 0) > 0
        if m.get('store') in SUPERMARKETS:
            super_cnt += 1
        assert c['veg'] in sides and (sides[c['veg']].get('cost') or 0) > 0
        if c['side'] is not None:
            assert c['side'] in sides and (sides[c['side']].get('cost') or 0) > 0
        assert 500 <= c['kcal'] <= 900

    assert super_cnt >= 14, f'Expected at least 14 Linz supermarket mains in combos, got {super_cnt}'
    top_side_reuse = Counter(c['veg'] for c in combos).most_common(1)[0][1]
    assert top_side_reuse <= 5


def test_sc78_p31_prefix_brand_backfill(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 3 ranked Spar meals explicitly named in SC78 P3.1
    assert by[453]['brand'] == 'Youcook' and by[453]['brandN'] == 'Youcook' and by[453]['noBrand'] is False and by[453]['logo'] == 'analysis/logos/youcook.png'
    assert by[94]['brand'] == 'Inzersdorfer' and by[94]['brandN'] == 'Inzersdorfer' and by[94]['noBrand'] is False and by[94]['logo'] == 'analysis/logos/inzersdorfer.png'
    assert by[432]['brand'] == 'Inzersdorfer' and by[432]['brandN'] == 'Inzersdorfer' and by[432]['noBrand'] is False and by[432]['logo'] == 'analysis/logos/inzersdorfer.png'

    # Zero ranked meals in Linz have noBrand: True or empty brand
    ranked_nobrand = [r['id'] for r in d['rows'] if (r.get('rankable') or r.get('rankableLight')) and (r.get('noBrand') or not r.get('brand'))]
    assert ranked_nobrand == []

    # Spot-check other catalog brand backfills
    assert by[68]['brand'] == 'Hilcona' and by[68]['noBrand'] is False and by[68]['logo'] == 'analysis/logos/hilcona.svg'
    assert by[74]['brand'] == 'Iglo' and by[74]['brandN'] == 'iglo' and by[74]['noBrand'] is False and by[74]['logo'] == 'analysis/logos/iglo.png'
    assert by[113]['brand'] == 'Knorr' and by[113]['noBrand'] is False and by[113]['logo'] == 'analysis/logos/knorr.svg'
    assert by[332]['brand'] == 'S-BUDGET' and by[332]['brandN'] == 'S-Budget' and by[332]['noBrand'] is False and by[332]['logo'] == 'analysis/logos/s-budget.png'
    assert by[361]['brand'] == 'SPAR Natur*pur' and by[361]['noBrand'] is False and by[361]['logo'] == 'analysis/logos/spar-natur-pur.png'
    assert by[437]['brand'] == 'SPAR Feine Küche' and by[437]['noBrand'] is False and by[437]['logo'] == 'analysis/logos/spar-feine-kueche.png'
    assert by[1194]['brand'] == 'Good Choice' and by[1194]['noBrand'] is False and by[1194]['logo'] == 'analysis/logos/good-choice.png'
    assert by[1254]['brand'] == 'dmBio' and by[1254]['noBrand'] is False and by[1254]['logo'] == 'analysis/logos/dmbio.png'

    assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 156
    assert d['dataVersion'] == '381633b31413'


def test_sc78_fixes_off_switch_reproduces_sc77(tmp_path):
    d_off = _export(tmp_path / 'off', SNAP, SC78_FIXES='0')
    assert d_off['dataVersion'] == '3368eaec1025'
    assert sum(1 for r in d_off['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d_off['rows'] if r.get('rankableLight')) == 156

    d_dis = _export(tmp_path / 'dis', SNAP, GOOD_CHOICE_DISABLE_SC78='1')
    assert d_dis['dataVersion'] == '3368eaec1025'
