import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC72_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc71_p2_1_p2_2_and_p3(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC71 P2.1: Second tranche of bofrost 750-1000 g family pans -> 2 portions (pack_2portions)
    for bid, por, kpor, ppor, prpor, score, pli in (
        (2985, 500, 660.0, 28.5, 7.5, 35.0, 27.0),
        (2991, 375, 686.2, 21.8, 7.89, 32.4, 23.1),
        (2995, 375, 558.8, 21.0, 7.14, 32.3, 23.5),
        (2996, 450, 490.5, 56.2, 8.49, 53.1, 43.1),
        (2935, 500, 830.0, 31.5, 7.25, 31.7, 26.7),
        (3005, 375, 431.2, 25.5, 6.0, 36.5, 28.9),
    ):
        r = by[bid]
        assert r['store'] == 'bofrost' and r['portion'] == por and r['portion_source'] == 'pack_2portions'
        assert r['multi_portion'] is True and r['kcalPor'] == kpor and r['protPor'] == ppor
        assert r['pPor'] == prpor and r['pPorEff'] == prpor and r['score'] == score
        assert r['meal_class'] == 'meal' and r['component'] is False
        assert r['rankable'] is True and r['pli'] == pli
        assert r['rankableLight'] is False and r['pliLight'] is None
        assert r.get('rank_excluded_reason') is None

    for bid, por, kpor, ppor, prpor, score, plil in (
        (3007, 375, 491.2, 19.9, 7.0, 43.5, 28.9),
        (3010, 375, 341.2, 15.8, 7.14, 41.4, 26.2),
        (3011, 375, 450.0, 16.5, 7.14, 36.9, 24.2),
    ):
        r = by[bid]
        assert r['store'] == 'bofrost' and r['portion'] == por and r['portion_source'] == 'pack_2portions'
        assert r['multi_portion'] is True and r['kcalPor'] == kpor and r['protPor'] == ppor
        assert r['pPor'] == prpor and r['pPorEff'] == prpor and r['score'] == score
        assert r['meal_class'] == 'light_meal' and r['component'] is False
        assert r['rankable'] is False and r['pli'] is None
        assert r['rankableLight'] is True and r['pliLight'] == plil
        assert r.get('rank_excluded_reason') is None

    for bid, por, kpor, ppor, prpor, mc in (
        (2998, 375, 607.5, 27.0, 6.75, 'meal'),
        (3012, 375, 408.8, 16.9, 7.0, 'light_meal'),
    ):
        r = by[bid]
        assert r['portion'] == por and r['portion_source'] == 'pack_2portions' and r['multi_portion'] is True
        assert r['kcalPor'] == kpor and r['protPor'] == ppor and r['pPor'] == prpor
        assert r['meal_class'] == mc and r['rankable'] is False and r['rankableLight'] is False
        assert r['rank_excluded_reason'] == 'Health-Score < 30'

    # 2. SC71 P2.2: Four 800 g cans at Spar/Billa normalized from por=200 g to por=400 g (pack_2portions)
    for cid, store, prpor, kpor, ppor, rer in (
        (91, 'Spar', 2.9, 328.0, 14.0, '< 15 g Protein/Portion'),
        (545, 'Billa', 1.25, 304.0, 7.6, '< 15 g Protein/Portion'),
        (958, 'Billa', 2.15, 376.0, 8.4, 'Health-Score < 30'),
    ):
        rc = by[cid]
        assert rc['store'] == store and rc['portion'] == 400 and rc['portion_source'] == 'pack_2portions'
        assert rc['multi_portion'] is True and rc['pPor'] == prpor and rc['kcalPor'] == kpor and rc['protPor'] == ppor
        assert rc['meal_class'] == 'light_meal' and rc['rankable'] is False and rc['rankableLight'] is False
        assert rc['rank_excluded_reason'] == rer
    r343 = by[343]
    assert r343['store'] == 'Spar' and r343['portion'] == 400 and r343['portion_source'] == 'pack_2portions'
    assert r343['multi_portion'] is True and r343['pPor'] == 1.5

    # 3. SC71 P3: Penny (#2236 Podravka Rindergulasch 400 g & #1537 Condeli Lasagne 800 g) & Lidl (#1212 Chef Select Lasagne Bolognese 1000 g + GTIN backfills)
    r2236 = by[2236]
    assert r2236['store'] == 'Penny' and r2236['ean'] == '3850104020032'
    assert r2236['size'] == 400.0 and r2236['portion'] == 400 and r2236['portion_source'] == 'pack_single'
    assert r2236['kcalPor'] == 452.0 and r2236['protPor'] == 44.0 and r2236['pPor'] == 4.99 and r2236['score'] == 30.2
    assert r2236['meal_class'] == 'meal' and r2236['rankable'] is True and r2236['pli'] == 37.1
    assert r2236.get('rank_excluded_reason') is None

    r1537 = by[1537]
    assert r1537['store'] == 'Penny' and r1537['ean'] == '4337256372008'
    assert r1537['size'] == 800.0 and r1537['portion'] == 400 and r1537['portion_source'] == 'pack_2portions'
    assert r1537['multi_portion'] is True and r1537['kcalPor'] == 568.0 and r1537['protPor'] == 23.6 and r1537['pPor'] == 2.5
    assert r1537['score'] == 31.8 and r1537['meal_class'] == 'meal' and r1537['rankable'] is True and r1537['pli'] == 39.5
    assert r1537.get('rank_excluded_reason') is None

    r1212 = by[1212]
    assert r1212['store'] == 'Lidl' and r1212['ean'] == '4056489412359'
    assert r1212['size'] == 1000.0 and r1212['portion'] == 500 and r1212['portion_source'] == 'pack_2portions'
    assert r1212['multi_portion'] is True and r1212['price'] == 3.99 and r1212['pstat'] == 'live 2026'
    assert r1212['kcalPor'] == 685.0 and r1212['protPor'] == 36.0 and r1212['pPor'] == 2.0 and r1212['score'] == 34.5
    assert r1212['meal_class'] == 'meal' and r1212['rankable'] is True and r1212['pli'] == 62.2
    assert r1212.get('rank_excluded_reason') is None and r1212.get('price_status') is None

    assert by[1211]['ean'] == '4056489149507' and by[1211]['portion'] == 500 and by[1211]['kcalPor'] == 685.0 and by[1211]['protPor'] == 24.0
    assert by[1211]['score'] == 18.5 and by[1211]['rank_excluded_reason'] == 'Health-Score < 30'
    assert by[1214]['ean'] == '4335619221598' and by[1214]['kcalPor'] == 628.3 and by[1214]['protPor'] == 23.6
    assert by[1214]['score'] == 24.6 and by[1214]['rank_excluded_reason'] == 'Health-Score < 30'
    assert by[1504]['ean'] == '4056489149491' and by[1504]['portion'] == 250 and by[1504]['kcalPor'] == 567.5 and by[1504]['protPor'] == 35.0
    assert by[1504]['meal_class'] == 'snack_side' and by[1504]['rank_excluded_reason'] == 'Brot/Snack/Instant – keine Mahlzeit'
    assert by[774]['ean'] == '0632674581143' and by[774]['size'] == 300.0
    assert by[782]['ean'] == '4056489862727' and by[782]['size'] == 330.0
    assert by[1502]['multi_portion'] is True

    # 4. Totals & invariants
    assert d['dataVersion'] == '21d092e2d842'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 209
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 156
    assert [i for i, r in enumerate(d['rows']) if r.get('id') != i] == []
    assert [r['id'] for r in d['rows'] if r.get('stage') == 'meal' and r.get('component')] == []
    assert [
        r['id'] for r in d['rows']
        if not r.get('rankable') and not r.get('rankableLight') and r.get('dupOf') is None and not r.get('rank_excluded_reason')
    ] == []


def test_sc71_off_switch_reproduces_sc70_bit_for_bit(tmp_path):
    for env_kw in ({'SC71_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC71': '1'}):
        d = _export(tmp_path, SNAP, **env_kw)
        assert d['dataVersion'] == 'cd044f054ed6'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 200
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
