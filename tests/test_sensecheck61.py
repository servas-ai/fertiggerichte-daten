import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC62_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc61_hofer_udon_bowls_860_861_862_and_sc59_flag_hygiene(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # Hofer #860 (Sesam-Teriyaki, 249 g, 351 kcal, 8.5 g P, score 30.6): rankableLight=True, pliLight=26.0
    r860 = by[860]
    assert r860['store'] == 'Hofer' and r860['ean'] == '4061461867645'
    assert r860['meal_class'] == 'light_meal' and r860['score'] == 30.6
    assert r860['rankable'] is False and r860['rankableLight'] is True and r860['pliLight'] == 26.0
    assert r860['rank_excluded_reason'] == '351 kcal/Portion < 400 (Light Meal)'
    assert r860['cprot'] == ['vegetarisch']

    # Hofer #861 (Erdnuss-Satay, 252 g, 430.9 kcal, 12.1 g P, score 32.5): rankableLight=True, pliLight=31.5
    r861 = by[861]
    assert r861['store'] == 'Hofer' and r861['ean'] == '4061461867669'
    assert r861['meal_class'] == 'light_meal' and r861['score'] == 32.5
    assert r861['kcalPor'] == 430.9 and r861['protPor'] == 12.1
    assert r861['rankable'] is False and r861['rankableLight'] is True and r861['pliLight'] == 31.5
    assert r861['rank_excluded_reason'] == '12.1 g Protein/Portion < 20 (Light Meal)'
    assert r861['cprot'] == ['vegetarisch']

    # Hofer #862 (Soja Ingwer, 249 g, 361.1 kcal, 8.0 g P, score 28.5 < 30): rankableLight=False, pliLight=None
    r862 = by[862]
    assert r862['store'] == 'Hofer' and r862['ean'] == '4061461867683'
    assert r862['meal_class'] == 'light_meal' and r862['score'] == 28.5
    assert r862['rankable'] is False and r862['rankableLight'] is False and r862['pliLight'] is None
    assert r862['rank_excluded_reason'] == '361 kcal/Portion < 400, Score 28.5 < 30 (Light Meal)'
    assert r862['cprot'] == ['vegetarisch']

    # All 7 SC59-backfilled rows have complete salt & satfat and no stale 'Score unvollständig' flag
    for rid in (860, 861, 862, 876, 1228, 1229, 1235):
        r = by[rid]
        assert r['incomplete'] is False and r['salt'] is not None and r['sat'] is not None
        assert not any('Score unvollständig' in f for f in (r.get('flags') or []))


def test_sc61_linz_spar_verified_nutrition_backfills(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # #69 Spar | Hilcona Tortellini Bolognese (250 g, p/2020005979116, EAN 7610227954746)
    r69 = by[69]
    assert r69['store'] == 'Spar' and r69['ean'] == '7610227954746'
    assert r69['priceOnly'] is False and r69['incomplete'] is False
    assert (r69['kcal'], r69['p100'], r69['fat'], r69['sat'], r69['carbs'], r69['sugar'], r69['fib'], r69['salt']) == (
        252.0, 9.7, 5.4, 1.9, 40.0, 2.7, 2.3, 1.5
    )
    assert r69['score'] == 35.2 and r69['stage'] == 'side' and r69['meal_class'] == 'snack_side'
    assert r69['rankable'] is False and r69['rank_excluded_reason'] == 'Frische gefüllte Pasta (braucht Sauce) – Zutat/Beilage'

    # #79 Spar | Iglo Lasagne al Forno (700 g, por 350 g, p/577052, dupOf #1114)
    r79 = by[79]
    assert r79['store'] == 'Spar' and r79['dupOf'] == 1114
    assert r79['priceOnly'] is False and r79['incomplete'] is False
    assert (r79['kcal'], r79['p100'], r79['fat'], r79['sat'], r79['carbs'], r79['sugar'], r79['salt']) == (
        157.0, 6.5, 5.8, 2.0, 19.0, 3.0, 0.82
    )
    assert r79['score'] == 39.5 and r79['meal_class'] == 'meal' and r79['rankable'] is False

    # #89 & #90 Spar | Inzersdorfer Erdäpfelgulasch (400 g & 800 g 2 Portionen)
    r89, r90 = by[89], by[90]
    assert r89['sat'] == 1.4 and r89['incomplete'] is False and r89['score'] == 19.9
    assert r90['ean'] == '9017100004778' and r90['priceOnly'] is False and r90['incomplete'] is False
    assert (r90['kcal'], r90['p100'], r90['fat'], r90['sat'], r90['carbs'], r90['sugar'], r90['salt']) == (
        94.0, 2.2, 5.8, 1.9, 7.7, 1.2, 1.2
    )
    assert r90['portion'] == 400 and r90['kcalPor'] == 376.0 and r90['protPor'] == 8.8
    assert r90['score'] == 27.8 and r90['meal_class'] == 'light_meal' and r90['rankable'] is False

    # #93 Spar | Inzersdorfer Paprikahendlragout mit Nockerln (300 g, p/5442348)
    r93 = by[93]
    assert r93['store'] == 'Spar' and r93['priceOnly'] is False and r93['incomplete'] is False
    assert (r93['kcal'], r93['p100'], r93['fat'], r93['sat'], r93['carbs'], r93['sugar'], r93['salt']) == (
        158.0, 7.9, 7.6, 2.7, 14.0, 2.3, 1.5
    )
    assert r93['kcalPor'] == 474.0 and r93['protPor'] == 23.7 and r93['score'] == 24.6
    assert r93['meal_class'] == 'meal' and r93['rankable'] is False
    assert r93['rank_excluded_reason'] == 'Gesundheits-Score unter 30 (24.6)'

    # #145 & #1163 Spar | Little Lunch Thai Curry Eintopf (350 g, p/2020005794535, EAN 4280000878946)
    for rid in (145, 1163):
        r = by[rid]
        assert r['store'] == 'Spar' and r['ean'] == '4280000878946'
        assert r['priceOnly'] is False and r['incomplete'] is False
        assert (r['kcal'], r['p100'], r['fat'], r['sat'], r['carbs'], r['sugar'], r['salt']) == (
            60.0, 1.6, 1.9, 0.4, 8.0, 3.1, 1.1
        )
        assert r['score'] == 35.8 and r['kcalPor'] == 210.0 and r['protPor'] == 5.6
        assert r['meal_class'] == 'snack_side' and r['rankable'] is False

    # #493 Spar | Inzersdorfer Bohnen mit Speck 2 Portionen (800 g, por 400 g) & #2727 Bauernschmaus (400 g)
    r493, r2727 = by[493], by[2727]
    assert r493['priceOnly'] is False and r493['incomplete'] is False and r493['score'] == 20.7 and r493['rankable'] is False
    assert r2727['priceOnly'] is False and r2727['incomplete'] is False and r2727['score'] == 16.6 and r2727['rankable'] is False

    # Totals: rankable stays 169, rankableLight increases from 93 -> 94 (+1 from Hofer #861)
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 169
    assert sum(bool(r.get('rankableLight')) for r in d['rows']) == 94


def test_sc61_offswitch_reproduces_sc60_bit_exact(tmp_path):
    d_sc61_off1 = _export(tmp_path, SNAP, SC61_FIXES='0')
    d_sc61_off2 = _export(tmp_path, SNAP, GOOD_CHOICE_DISABLE_SC61='1')
    assert d_sc61_off1['dataVersion'] == 'ab290185f561'
    assert d_sc61_off2['dataVersion'] == 'ab290185f561'
    assert sum(bool(r.get('rankable')) for r in d_sc61_off1['rows']) == 169
    assert sum(bool(r.get('rankableLight')) for r in d_sc61_off1['rows']) == 93
