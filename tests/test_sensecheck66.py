import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC67_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc66_p1_1_p1_2_and_p3_1(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC65 P1.1: All 32 second-dead-zone light_meal ready meals (250-300 kcal, >=15 g P + 5 Linz/Online hearty soups 308-440 kcal)
    expected_p11 = (
        # Löwenanteil (10 jars)
        (3136, 38.3),
        (3130, 38.3),
        (3125, 35.3),
        (3127, 34.7),
        (3135, 35.1),
        (3134, 33.5),
        (3128, 32.9),
        (3137, 32.1),
        (3138, 28.4),
        (3139, 29.7),
        # Billa (6)
        (606,  40.7),
        (1036, 33.9),
        (42,   27.2),
        (585,  38.3),
        (639,  28.9),
        (1007, 31.4),
        # Spar (3)
        (156,  38.5),
        (170,  39.1),
        (2663, 31.4),
        # dm (1)
        (1255, 47.5),
        # Online delivery to 4020 Linz (12)
        (3148, 38.1),
        (3158, 37.2),
        (3161, 37.0),
        (3162, 27.8),
        (3666, 34.6),
        (3670, 28.3),
        (3206, 24.3),
        (2931, 39.3),
        (2973, 35.2),
        (3005, 28.9),
        (3017, 37.4),
        (3062, 21.4),
    )
    for rid, exp_plil in expected_p11:
        r = by[rid]
        assert r['meal_class'] == 'light_meal'
        assert r['rankable'] is False and r['pli'] is None
        assert r['rankableLight'] is True and r['pliLight'] == exp_plil
        assert r['gang'] == 'haupt'
        assert r.get('rank_excluded_reason') is None

    # dm #1255 dmBio Gulasch vegan (pliLight 47.5) enters topLight top-5
    assert 1255 in d['topLight'][:5]

    # 2. SC65 P1.2(a): 5 legacy < 11 g P rows demoted from rankableLight so rankableLight === passesLightRank (148 === 148)
    for rid in (51, 52, 860, 1091, 2948):
        r = by[rid]
        assert r['rankable'] is False and r['rankableLight'] is False
        assert r['pli'] is None and r['pliLight'] is None
        assert r['rank_excluded_reason'] == '< 11 g Protein/Portion'
        assert rid not in d['topLight'] and rid not in d['topLightUncapped']

    # 3. SC65 P1.2(b): False-positive _NOISE duplicates #2820 & #877 rescued into rankable=True; self-twin keepers #212/#222/#1087 cleaned
    for rid in (212, 222, 1087, 2820, 877):
        assert 'Duplikat (nahe Name/Marke, Ranking)' not in (by[rid].get('flags') or [])

    r2820 = by[2820]
    assert r2820['store'] == 'PrepMyMeal' and r2820['rankable'] is True and r2820['rankableLight'] is False
    assert r2820['pli'] == 37.0 and r2820['pliLight'] is None and r2820.get('rank_excluded_reason') is None

    r877 = by[877]
    assert r877['store'] == 'Billa' and r877['rankable'] is True and r877['rankableLight'] is False
    assert r877['pli'] == 35.3 and r877['pliLight'] is None and r877.get('rank_excluded_reason') is None

    # 4. SC65 P3.1: All HelloFresh rows and unranked light_meal rows (< 15 g P / Score < 30) have explicit rank_excluded_reason
    hf_rows = [r for r in d['rows'] if r.get('store') == 'HelloFresh']
    assert len(hf_rows) == 94
    assert all(r.get('rank_excluded_reason') == 'Kochbox zum Selbstkochen (30–45 Min.) – nicht im Fertiggericht-Ranking' for r in hf_rows)

    unranked_lm_low = [
        r for r in d['rows']
        if r.get('meal_class') == 'light_meal'
        and not r.get('rankable')
        and not r.get('rankableLight')
        and r.get('dupOf') is None
        and ((r.get('score') is not None and r['score'] < 30) or (r.get('protPor') is not None and r['protPor'] < 15))
    ]
    assert all(bool(r.get('rank_excluded_reason')) for r in unranked_lm_low)

    # 5. Totals & dataVersion
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 182
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 148
    assert d['dataVersion'] == '8bb86dd879eb'


def test_sc66_off_switch_reproduces_sc64_bit_for_bit(tmp_path):
    for env_kw in ({'SC66_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC66': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == 'd252972a9be9'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 180
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 121
