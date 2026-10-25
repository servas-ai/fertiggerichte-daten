import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from health_off import build_health_off, load_merged_off_by_ean
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC77_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc76_p31_health_off_and_export_additives_ns_merge(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. Verify analysis/health_off.json in both repos is deterministic, >770 entries & >770 unique EANs
    p_fertig = os.path.join(ROOT, 'analysis', 'health_off.json')
    p_app = '/workspace/fertig-app/public/analysis/health_off.json'
    h_fertig = json.load(open(p_fertig))
    h_app = json.load(open(p_app))
    assert h_fertig == h_app
    rebuilt = build_health_off(root=ROOT)
    assert h_fertig == rebuilt

    uniq_eans = {x['ean'] for x in h_fertig}
    assert len(h_fertig) > 770, f"Expected >770 entries in health_off.json, got {len(h_fertig)}"
    assert len(uniq_eans) > 770, f"Expected >770 unique EANs in health_off.json, got {len(uniq_eans)}"

    required_keys = {'name', 'store', 'ean', 'additives', 'nova', 'ns', 'labels', 'analysis', 'origins', 'mplace', 'ingr', 'url'}
    for item in h_fertig:
        assert set(item.keys()) == required_keys
        assert isinstance(item['additives'], list)
        assert isinstance(item['labels'], list)
        assert isinstance(item['analysis'], list)
        assert item['url'].startswith('https://world.openfoodfacts.org/product/')

    # 2. Verify all 13 P3.1 ranked Linz meals are in health_off.json and enriched on d['rows']
    p31_ranked_ids = [
        453,   # [Spar] Youcook Tikka Huhn India Style (4260334165042)
        2262,  # [Spar] Youcook Pasta Caesar Chicken (4260334162201)
        1255,  # [dm] dmBio Gulasch vegan (4070765058246)
        1256,  # [dm] dmBio Chili sin Carne (4066447892482)
        1257,  # [dm] Little Lunch Protein Bowl Kichererbsen & Linsen (4260614720343)
        1258,  # [dm] Tressbrüder Butter Chicken Curry (4260189683630)
        1259,  # [dm] Little Lunch Chili Sin Carne (4280000878519)
        1268,  # [dm] Tressbrüder Eintopf Kichererbsen Erdnuss Curry (4260189683609)
        1277,  # [dm] dmBio Chili con Tofu High Protein (4070765057522)
        1278,  # [dm] dmBio Veganes No-Chicken Curry (4070765057560)
        1947,  # [Billa] Dr. Oetker Ristorante Pizza Tonno (4001724038993)
        2417,  # [Spar] Dr. Oetker Pietro Pizzi Margherita (4001724046042)
        3233,  # [myProduct] Bio Chili Sin Carne 350g - 6er Vorteilspack - Fertiggericht von Little Lunch (4280000878519)
        3236,  # [myProduct] Bio Protein Bowl 350g - 6er Vorteilspack - Fertiggericht von Little Lunch (4260614720343)
    ]
    for rid in p31_ranked_ids:
        r = by[rid]
        assert str(r['ean']) in uniq_eans, f"#{rid} EAN {r['ean']} missing from health_off.json"
        assert isinstance(r.get('additives'), list), f"#{rid} additives not populated as list"
        if rid != 1278:  # 1278 has OFF nutriscore_grade == 'not-applicable'
            assert r.get('ns') in ('A', 'B', 'C', 'D', 'E'), f"#{rid} ns not populated: {r.get('ns')}"

    assert by[453]['additives'] == ['E412', 'E471'] and by[453]['ns'] == 'C'
    assert by[2262]['additives'] == ['E14XX', 'E250'] and by[2262]['ns'] == 'C'
    assert by[1255]['additives'] == ['E412'] and by[1255]['ns'] == 'C'
    assert by[1256]['additives'] == [] and by[1256]['ns'] == 'A'
    assert by[1257]['additives'] == ['E412'] and by[1257]['ns'] == 'C'
    assert by[1258]['additives'] == [] and by[1258]['ns'] == 'C'
    assert by[1259]['additives'] == [] and by[1259]['ns'] == 'A'
    assert by[1268]['additives'] == [] and by[1268]['ns'] == 'C'
    assert by[1277]['additives'] == [] and by[1277]['ns'] == 'A'
    assert by[3233]['additives'] == [] and by[3233]['ns'] == 'A'
    assert by[3236]['additives'] == ['E412'] and by[3236]['ns'] == 'C'

    # Global active row coverage for additives & Nutri-Score
    active_add = sum(1 for r in d['rows'] if r.get('dupOf') is None and isinstance(r.get('additives'), list))
    active_ns = sum(1 for r in d['rows'] if r.get('dupOf') is None and r.get('ns') in ('A', 'B', 'C', 'D', 'E'))
    assert active_add >= 570, f"Expected >=570 active rows with additives list, got {active_add}"
    assert active_ns >= 1780, f"Expected >=1780 active rows with Nutri-Score A-E, got {active_ns}"


def test_sc76_p32_nova_enrichment_and_score_under_30_formatting(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. All 19 ranked EAN meals previously missing NOVA + their twins are enriched
    expected_p32 = [
        # (id, nova, nova_source, veg_pct, score, pli_or_pliLight, is_full_meal)
        (861,  4, 'off',                 3.0,  30.5, 30.5, False),
        (880,  4, 'ingredients_markers', 20.0, 55.3, 41.9, True),
        (1162, 4, 'ingredients_markers', 18.0, 43.2, 40.1, True),
        (1947, 3, 'off',                 19.5, 43.3, 43.9, True),
        (2257, 4, 'ingredients_markers', 32.0, 39.5, 37.9, True),
        (2335, 4, 'ingredients_markers', 0.0,  39.7, 26.2, False),
        (2336, 4, 'ingredients_markers', 0.0,  46.9, 29.8, False),
        (2417, 3, 'ingredients_markers', 14.0, 38.0, 38.6, True),
        (2450, 4, 'ingredients_markers', 23.0, 36.1, 27.1, False),
        (2663, 4, 'ingredients_markers', 28.0, 32.7, 31.4, False),
        (3140, 3, 'ingredients_markers', 48.0, 49.2, 29.7, False),
        (3143, 3, 'ingredients_markers', 72.0, 68.1, 39.7, False),
        (3144, 3, 'ingredients_markers', 28.0, 42.7, 26.6, False),
        (3145, 3, 'ingredients_markers', 62.0, 57.0, 33.0, False),
        (3157, 4, 'ingredients_markers', 28.0, 49.9, 29.2, False),
        (3206, 4, 'ingredients_markers', 18.0, 36.4, 23.0, False),
        (3207, 4, 'ingredients_markers', 51.0, 36.9, 23.8, False),
        (3208, 4, 'ingredients_markers', 45.0, 52.3, 31.8, False),
        (3240, 3, 'off',                 84.0, 45.1, 32.0, False),
    ]
    for rid, exp_nova, exp_src, exp_veg, exp_score, exp_pli, is_full in expected_p32:
        r = by[rid]
        assert r['nova'] == exp_nova, f"#{rid} nova: {r['nova']} != {exp_nova}"
        assert r['nova_source'] == exp_src, f"#{rid} nova_source: {r['nova_source']} != {exp_src}"
        assert r['veg_pct'] == exp_veg, f"#{rid} veg_pct: {r['veg_pct']} != {exp_veg}"
        assert r['ing'] and len(r['ing']) > 30, f"#{rid} missing ing"
        assert isinstance(r.get('additives'), list), f"#{rid} missing additives list"
        assert r['score'] == exp_score, f"#{rid} score: {r['score']} != {exp_score}"
        assert r['score_parts']['nova'] == ({4: -10.0, 3: 0.0}[exp_nova])
        if is_full:
            assert r['rankable'] is True and r['pli'] == exp_pli
        else:
            assert r['rankableLight'] is True and r['pliLight'] == exp_pli

    # Check #861 fiber backfill from OFF 4061461867669
    assert by[861]['fib'] == 2.5 and by[861]['day_pct']['fiber'] == 21 and by[861]['ns'] == 'C'

    # Check twins (#3290, #3989, #2445, #1863, #1912, #2416, #3884, #1779, #2345, #2346, #1879, #2340, #3879, #2007, #1574)
    for tid in (3290, 3989, 2445, 1863, 1912, 2416, 3884, 1779, 2345, 2346, 1879, 2340, 3879, 2007, 1574):
        rt = by[tid]
        assert rt['nova'] in (3, 4), f"Twin #{tid} missing nova"
        assert rt['nova_source'] in ('off', 'ingredients_markers'), f"Twin #{tid} invalid nova_source: {rt['nova_source']}"
        assert rt['ing'] and len(rt['ing']) > 30, f"Twin #{tid} missing ing"

    # Global invariant: 0 ranked EAN meals have nova is None or nova_source in (None, 'unknown', 'estimate')
    ranked_ean_null_nova = [
        r['id'] for r in d['rows']
        if r.get('dupOf') is None and (r.get('rankable') or r.get('rankableLight'))
        and r.get('ean') and (r.get('nova') is None or r.get('nova_source') in (None, 'unknown', 'estimate'))
    ]
    assert ranked_ean_null_nova == [], f"Ranked EAN meals still missing verified NOVA: {ranked_ean_null_nova}"

    # 2. #2363 [MPreis] Dr. Oetker Ristorante Pizza Hawaii (score=29.9) no longer says 'Health-Score 30 < 30'
    r2363 = by[2363]
    assert r2363['score'] == 29.9
    assert 'Health-Score 29,9 < 30' in r2363['rank_excluded_reason']
    assert 'Health-Score 30 < 30' not in r2363['rank_excluded_reason']

    for r in d['rows']:
        rer = r.get('rank_excluded_reason') or ''
        assert not re.search(r'Health-Score \d+ < 30', rer), f"#{r['id']} still has integer Health-Score < 30: {rer!r}"

    # 3. Totals & dataVersion
    assert d['dataVersion'] == '6fa43d749824'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155


def test_sc76_off_switches_reproduce_sc75_baseline_bit_for_bit(tmp_path):
    for kw in ({'SC76_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC76': '1'}):
        d = _export(tmp_path, SNAP, **kw)
        assert d['dataVersion'] == '72c601dd5d67'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
