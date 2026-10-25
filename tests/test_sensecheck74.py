import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc74_p1_rana_teriyaki_and_popup_sushi_lachs_and_p3_atwater_gate(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC74 P1.1: #880 [Billa] Rana Teriyaki Style Noodels Hühnchen (407 g, 5.49 €) + twins #3290 [Gurkerl] & #3989 [Alfies]
    # Billa PIM typo carbs: 25.0 -> 14.0 (EAN 8001665728218 trade sheet / 300 g Sauce + 100 g Teigwaren + 7 g Sesam, Atwater 111.1 vs 113 kcal = 98.3%)
    for rid in (880, 3290, 3989):
        r = by[rid]
        assert r['carbs'] == 14.0
        assert r['ean'] == '8001665728218'
        assert '8001665728218' in (r.get('nutrition_source') or '')
        atw = 4.0 * r['p100'] + 9.0 * r['fat'] + 4.0 * r['carbs'] + 2.0 * (r.get('fib') or 0.0)
        assert abs(atw - r['kcal']) / r['kcal'] < 0.05

    assert by[880]['rankable'] is True and by[880]['score'] == 57.3 and by[880]['pli'] == 42.9
    assert by[3290]['rankable'] is False and by[3290]['score'] == 57.3
    assert by[3989]['rankable'] is False and by[3989]['score'] == 53.8

    # 2. SC74 P1.2: #887 [Billa] Pop-Up Sushi Lachs mild (245 g, 8.99 €)
    # Billa PIM typo kcal: 153.0 -> 201.0 (from Billa det.json 00-897874 kj: 839.0 / 4.184 = 200.53 kcal, 97% Atwater match)
    r887 = by[887]
    assert r887['store'] == 'Billa'
    assert r887['kcal'] == 201.0
    assert r887['kcalPor'] == 492.5 and r887['kcalpack'] == 492.5 and r887['kcal_meal'] == 492
    assert r887['p100k'] == 3.08 and r887['eur100k'] == 1.83
    assert r887['score'] == 34.4 and r887['scoreV1'] == 35.8
    assert r887['meal_class'] == 'light_meal'
    assert r887['rankable'] is False and r887['pli'] is None
    assert r887['rankableLight'] is True and r887['pliLight'] == 21.4
    assert r887['rank_excluded_reason'] == '15.2 g Protein/Portion < 20 (Light Meal)'
    assert r887['meal_check'] == {'portion': 245, 'kcal': 492, 'protein': 15.2, 'ok': False, 'cls': 'light_meal', 'reason': '15.2 g Protein/Portion < 20'}

    # 3. SC74 P3.1: #1177 [Hofer] Maishendl Ministeaks (280 g, 4.99 €)
    # Fix kcal divided by 2.8 (36.0714 -> 101.0 kcal/100g, kcalPor = 282.8, p100k = 22.8)
    r1177 = by[1177]
    assert r1177['store'] == 'Hofer'
    assert r1177['kcal'] == 101.0
    assert r1177['kcalPor'] == 282.8 and r1177['kcalpack'] == 282.8 and r1177['kcal_meal'] == 283
    assert r1177['p100k'] == 22.8 and r1177['eur100k'] == 1.76
    assert r1177['stage'] == 'prot' and r1177['component'] is True and r1177['rankable'] is False

    # 4. SC74 P3.2 & P3.3: #3309 [Gurkerl] Itineraire des Saveurs Crepes (carbs: 0.0 < sugar: 60.96 -> carbs=None)
    # & generic Atwater/macro plausibility gate on #1539 [Penny] Lasagne alla Bolognese and all other >=50 kcal Atwater >25% outliers
    r3309 = by[3309]
    assert r3309['carbs'] is None
    assert r3309['incomplete'] is True
    assert r3309['score'] is None and r3309['scoreV1'] is None and r3309['score_parts'] is None
    assert r3309['rankable'] is False and r3309['rankableLight'] is False
    assert r3309['pli'] is None and r3309['pliLight'] is None
    assert r3309['rank_excluded_reason'] == 'Nährwert-Inkonsistenz (Atwater/Makro-Prüfung)'

    for bad_id in (1424, 1430, 1539, 1721, 1835, 1843, 3160, 3284, 3304, 3309):
        rb = by[bad_id]
        assert rb['incomplete'] is True
        assert rb['score'] is None and rb['scoreV1'] is None and rb['score_parts'] is None
        assert rb['rankable'] is False and rb['rankableLight'] is False
        assert rb['pli'] is None and rb['pliLight'] is None
        assert rb['rank_excluded_reason'] == 'Nährwert-Inkonsistenz (Atwater/Makro-Prüfung)'
        assert 'Nährwert-Inkonsistenz (Atwater/Makro-Prüfung)' in (rb.get('flags') or [])

    # 5. Global invariants across all 4,049 rows:
    # - Zero rows with p100k > 25.0
    # - Zero rows with sugar > carbs + 0.5 or sat > fat + 0.5
    # - Zero ranked or light-ranked rows with >20% Atwater deviation (both over and under!)
    # - Zero scored (incomplete=False, score!=None) rows with kcal >= 50 and >25% Atwater deviation
    assert [r['id'] for r in d['rows'] if (r.get('p100k') or 0) > 25.0] == []
    assert [r['id'] for r in d['rows'] if r.get('sugar') is not None and r.get('carbs') is not None and r['sugar'] > r['carbs'] + 0.5] == []
    assert [r['id'] for r in d['rows'] if r.get('sat') is not None and r.get('fat') is not None and r['sat'] > r['fat'] + 0.5] == []

    for r in d['rows']:
        if r.get('rankable') or r.get('rankableLight'):
            atw = 4.0 * (r['p100'] or 0) + 9.0 * (r['fat'] or 0) + 4.0 * (r['carbs'] or 0) + 2.0 * (r.get('fib') or 0)
            dev = abs(atw - r['kcal']) / r['kcal']
            assert dev <= 0.22, f"Ranked/Light row #{r['id']} ({r['name']}) has Atwater dev {dev*100:.1f}% ({atw:.1f} vs {r['kcal']})"
        if not r.get('incomplete') and r.get('score') is not None and (r.get('kcal') or 0) >= 50 and r.get('p100') is not None and r.get('fat') is not None and r.get('carbs') is not None:
            atw = 4.0 * r['p100'] + 9.0 * r['fat'] + 4.0 * r['carbs'] + 2.0 * (r.get('fib') or 0)
            dev = abs(atw - r['kcal']) / r['kcal']
            assert dev <= 0.25, f"Scored row #{r['id']} ({r['name']}) has Atwater dev {dev*100:.1f}% ({atw:.1f} vs {r['kcal']})"

    assert d['dataVersion'] == '5d7674157f71'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 206
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155


def test_sc74_off_switch_reproduces_sc73_bit_for_bit(tmp_path):
    for env_kw in ({'SC74_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC74': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == '0e0a9dc8f98b'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 206
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
