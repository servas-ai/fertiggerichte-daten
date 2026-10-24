import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc60_spar_verified_satfat_backfills_and_off_1382(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. Spar #176 S-BUDGET Rindsgulasch 400 G (p/7442025): sat=1.6, fib=0.9 from official SPAR Produktwelt -> score 48.8, pli 55.8, rankable
    r176 = by[176]
    assert r176['store'] == 'Spar' and r176['name'] == 'S-BUDGET Rindsgulasch 400 G'
    assert r176['sat'] == 1.6 and r176['fib'] == 0.9
    assert r176['incomplete'] is False
    assert r176['score'] == 48.8 and r176['pli'] == 55.8
    assert r176['meal_class'] == 'meal' and r176['rankable'] is True
    assert r176['img'] == 'https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/7442025/dt_main.jpg'
    assert not any('Score unvollständig' in f for f in (r176.get('flags') or []))

    # 2. Spar #1162 Inzersdorfer Rindsgulasch 800 G (p/145930): sat=1.6, EAN 9017100001050, 2 portions (400 g) from INTERSPAR twin #97 -> score 45.7, pli 41.3, rankable
    r1162 = by[1162]
    assert r1162['store'] == 'Spar' and r1162['name'] == 'Inzersdorfer Rindsgulasch 800 G'
    assert r1162['sat'] == 1.6 and r1162['ean'] == '9017100001050'
    assert r1162['portion'] == 400 and r1162['portion_g'] == 400 and r1162['portion_source'] == 'name_portions'
    assert r1162['pPor'] == 5.25 and r1162['protPor'] == 38.8 and r1162['kcalPor'] == 444.0
    assert r1162['incomplete'] is False
    assert r1162['score'] == 45.7 and r1162['pli'] == 41.3
    assert r1162['meal_class'] == 'meal' and r1162['rankable'] is True
    assert not any('Score unvollständig' in f or 'Mehrportionen-Packung' in f for f in (r1162.get('flags') or []))

    # MPreis twin #2445 reflects that Spar in Linz is now ranked
    r2445 = by[2445]
    assert 'gleiches Produkt in Linz bei Spar – dort gerankt' in (r2445.get('rank_excluded_reason') or '')

    # 3. Spar #95 Inzersdorfer Riesenbohnengulasch 400 G (p/412568): sat=2.1 -> score 25.4 (< 30, excluded by health score)
    r95 = by[95]
    assert r95['store'] == 'Spar' and r95['name'] == 'Inzersdorfer Riesenbohnengulasch 400 G'
    assert r95['sat'] == 2.1 and r95['incomplete'] is False
    assert r95['score'] == 25.4 and r95['rankable'] is False and r95['pli'] is None
    assert r95['rank_excluded_reason'] == 'Gesundheits-Score unter 30 (25.4)'
    assert r95['dishKey'] == 'gulasch' and r95['cprot'] == ['Schwein', 'Rind', 'Hülsenfrüchte']

    # 4. OFF #1382 Suppe Thai Chili: 2.0 g pack size artefact cleared and classified as dry soup
    r1382 = by[1382]
    assert r1382['store'] == 'unbekannt (OFF)' and r1382['name'] == 'Suppe Thai Chili'
    assert r1382['size'] is None and r1382['portion'] is None and r1382['portion_g'] is None
    assert r1382['dry'] is True and r1382['meal_class'] == 'dry'
    assert r1382['rank_excluded_reason'] == 'Trockensuppe (kein Fertiggericht)'
    assert r1382['rankable'] is False

    # Total rankable meals increased from 167 -> 169 (+2 Linz Spar meals #176 and #1162)
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 169


def test_sc60_offswitch_reproduces_sc59_bit_exact(tmp_path):
    d_sc60_off1 = _export(tmp_path, SNAP, SC60_FIXES='0')
    d_sc60_off2 = _export(tmp_path, SNAP, GOOD_CHOICE_DISABLE_SC60='1')
    assert d_sc60_off1['dataVersion'] == '77f334029405'
    assert d_sc60_off2['dataVersion'] == '77f334029405'
    assert sum(bool(r.get('rankable')) for r in d_sc60_off1['rows']) == 167
    assert sum(bool(r.get('rankableLight')) for r in d_sc60_off1['rows']) == 93
