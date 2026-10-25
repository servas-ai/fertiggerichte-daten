import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    e.setdefault('SC76_FIXES', '0')
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc75_p3_hofer_kasnudeln_ppk_whitespace_and_gtin_dedup(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # 1. SC75 P3.1: #1180 [Hofer] Kärntner Kasnudeln (370 g, 3.09 €, EAN 4099200227733)
    # Fix OFF 10x decimal-comma typo sugar: 12.0 -> 1.2 g/100g & portion: 185 -> 370 (pack_single)
    r1180 = by[1180]
    assert r1180['store'] == 'Hofer'
    assert r1180['ean'] == '4099200227733'
    assert r1180['sugar'] == 1.2
    assert r1180['size'] == 370.0 and r1180['portion'] == 370 and r1180['portion_g'] == 370
    assert r1180['portion_source'] == 'pack_single' and r1180['multi_portion'] is False
    assert r1180['kcalPor'] == 570 and r1180['kcal_meal'] == 570
    assert r1180['protPor'] == 24.4 and r1180['saltPor'] == 3.7 and r1180['saltPct'] == 62
    assert r1180['pPor'] == 3.09 and r1180['eur10p'] == 1.27 and r1180['eur100k'] == 0.54 and r1180['ppe'] == 7.9
    assert r1180['score'] == 30.7 and r1180['scoreV1'] == 36.4
    assert r1180['meal_class'] == 'meal' and r1180['meal_check']['ok'] is True
    assert r1180['rankable'] is True and r1180['rankableLight'] is False
    assert r1180['pli'] == 35.1 and r1180['pliLight'] is None
    assert r1180['rank_excluded_reason'] is None and r1180['variant_note'] is None
    # Twin #801 [Hofer] Kärntner Kasnudeln (stale price) linked as dupOf #1180
    r801 = by[801]
    assert r801['dupOf'] == 1180 and r801['dupOfUid'] == r1180['uid']
    assert r801['rankable'] is False and r801['rankableLight'] is False

    # 2. SC75 P3.2: #635 [Billa] Omis Schmankerl Hühnerpfandl mit Spätzle ppk & whitespace normalization
    r635 = by[635]
    assert r635['name'] == 'Omis Schmankerl Hühnerpfandl mit Spätzle'
    assert r635['price'] == 4.49 and r635['size'] == 350.0 and r635['ppk'] == 12.83

    for r in d['rows']:
        assert not re.search(r'\s{2,}', r.get('name') or ''), f"#{r['id']} name still has multiple whitespace: {r['name']!r}"
        if r.get('price') is not None and r.get('size'):
            assert r['ppk'] == round(r['price'] / (r['size'] / 1000.0), 2), f"#{r['id']} ppk mismatch: {r['ppk']}"

    # 3. SC75 P3.3: (store, GTIN) deduplication across ean, psrc, url, nutrition_source
    expected_dups = [
        (806, 691, 'Hofer', '4099200075563'),
        (804, 1217, 'Hofer', '4099200146256'),
        (821, 1425, 'Hofer', '4099200121543'),
        (1356, 1218, 'Hofer', '4099200146324'),
        (1357, 1220, 'Hofer', '4099200146263'),
        (59, 60, 'Spar', '9000295832493'),
        (287, 286, 'Spar', '01509439'),
        (346, 363, 'Spar', '9100000066189'),
    ]
    for loser_id, winner_id, store_nm, gtin in expected_dups:
        los = by[loser_id]
        win = by[winner_id]
        assert los['store'] == store_nm and win['store'] == store_nm
        assert los['ean'] == gtin and win['ean'] == gtin
        assert los['dupOf'] == winner_id and los['dupOfUid'] == win['uid']
        assert los['rankable'] is False and los['rankableLight'] is False
        assert los['pli'] is None and los['pliLight'] is None
        assert win.get('dupOf') is None

    # Global invariant: 0 active (dupOf is None) duplicate (store, GTIN) pairs
    seen_sg = {}
    for r in d['rows']:
        if r.get('dupOf') is not None:
            continue
        st = r.get('store') or ''
        if not st or st.startswith('unbekannt'):
            continue
        gtin = str(r.get('ean') or '').strip()
        if not re.fullmatch(r'\d{8,14}', gtin):
            for k in ('psrc', 'url', 'nutrition_source'):
                m = re.search(r'(?:/product/|\b)(\d{8,14})\b', str(r.get(k) or ''))
                if m:
                    gtin = m.group(1)
                    break
        if re.fullmatch(r'\d{8,14}', gtin):
            assert (st, gtin) not in seen_sg, f"Duplicate active (store, GTIN) ({st}, {gtin}): #{seen_sg[(st, gtin)]} and #{r['id']}"
            seen_sg[(st, gtin)] = r['id']

    # 4. Totals & dataVersion
    assert d['dataVersion'] == '72c601dd5d67'
    assert sum(1 for r in d['rows'] if r.get('rankable')) == 207
    assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155


def test_sc75_off_switches_reproduce_sc74_baseline(tmp_path):
    for kw in ({'SC75_FIXES': '0'}, {'GOOD_CHOICE_DISABLE_SC75': '1'}):
        d = _export(tmp_path, SNAP, **kw)
        assert d['dataVersion'] == '5d7674157f71'
        assert sum(1 for r in d['rows'] if r.get('rankable')) == 206
        assert sum(1 for r in d['rows'] if r.get('rankableLight')) == 155
