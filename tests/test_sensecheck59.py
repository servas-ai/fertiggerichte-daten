import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'


def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_sc59_fittogo_per100g_and_full_meal_reclassification(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}
    ftg_ids = list(range(1435, 1465)) + [2749]

    # All 31 Fit to Go rows must have true per-100g kcal (88–166 kcal/100g) and sat/salt None (not estimated)
    for rid in ftg_ids:
        r = by[rid]
        assert r['store'] == 'Fit to Go'
        assert 85.0 <= r['kcal'] <= 170.0, f"#{rid} kcal={r['kcal']} out of per-100g range"
        assert r['sat'] is None and r['salt'] is None
        assert r['incomplete'] is True

    # #1445 (576 kcal portion in raw other.json) is normalized to 144.0 kcal/100g
    assert by[1445]['kcal'] == 144.0 and by[1445]['kcalPor'] == 576.0

    # 5 reclassified Fit to Go full meals (#1436, #1437, #1441, #1443, #1455)
    for rid, port, kcal_por, prot_por in (
        (1436, 400, 488, 46.0),
        (1437, 360, 537, 38.9),
        (1441, 450, 552, 30.1),
        (1443, 400, 456, 36.0),
        (1455, 420, 483, 29.0),
    ):
        r = by[rid]
        assert r['stage'] == 'meal'
        assert r['gang'] == 'haupt'
        assert r['meal_class'] == 'meal'
        assert r['component'] is False
        assert r['meal_check'] == {'portion': port, 'kcal': kcal_por, 'protein': prot_por, 'ok': True, 'cls': 'meal', 'reason': None}
        assert not any('Proteinkomponente' in f or 'Brot/Snack/Instant' in f for f in (r.get('flags') or []))


def test_sc59_billa_and_hofer_backfills_and_reclassifications(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # Billa #876 Aumaerk Beef Loyal Sous Vide backfilled from label photo + classified as protein_component
    r876 = by[876]
    assert r876['ean'] == '9120077263045'
    assert r876['priceOnly'] is False and r876['incomplete'] is False
    assert (r876['kcal'], r876['p100'], r876['fat'], r876['sat'], r876['carbs'], r876['sugar'], r876['salt']) == (154.0, 26.6, 5.1, 2.2, 0.3, 0.3, 1.53)
    assert r876['score'] == 40.9
    assert r876['stage'] == 'prot' and r876['meal_class'] == 'protein_component' and r876['component'] is True
    assert r876['rankable'] is False

    # Other 8 Billa non-ready-meal rows
    for rid in (0, 1, 6):
        assert by[rid]['stage'] == 'prot' and by[rid]['meal_class'] == 'raw_ingredient' and by[rid]['component'] is True
    assert by[3536]['stage'] == 'sauce' and by[3536]['meal_class'] == 'condiment_or_base' and by[3536]['dry'] is True and 'kiloErr' not in by[3536]
    for rid in (3579, 3580, 3581, 3583):
        assert by[rid]['stage'] == 'sweet' and by[rid]['meal_class'] == 'dessert'

    # Hofer #860, #861, #862 Asia Green Garden Udon bowls backfilled from OFF
    assert by[860]['ean'] == '4061461867645' and by[860]['priceOnly'] is False and by[860]['score'] == 30.6
    assert by[860]['meal_class'] == 'light_meal' and by[860]['pliLight'] == 26.0 and by[860]['rankableLight'] is True
    assert by[861]['ean'] == '4061461867669' and by[861]['priceOnly'] is False and by[861]['score'] == 32.5 and by[861]['meal_class'] == 'light_meal'
    assert by[862]['ean'] == '4061461867683' and by[862]['priceOnly'] is False and by[862]['score'] == 28.5 and by[862]['meal_class'] == 'light_meal'

    # Hofer #1228, #1229, #1235 backfilled from OFF while preserving delisted status
    assert by[1228]['ean'] == '4061458049443' and by[1228]['priceOnly'] is False and by[1228]['score'] == 28.7
    assert by[1228]['meal_class'] == 'multi_portion' and 'evtl. ausgelistet' in (by[1228].get('variant_note') or '')
    assert by[1229]['ean'] == '4061458049436' and by[1229]['priceOnly'] is False and by[1229]['score'] == 29.2
    assert by[1229]['meal_class'] == 'multi_portion' and 'evtl. ausgelistet' in (by[1229].get('variant_note') or '')
    assert by[1235]['ean'] == '4061458041997' and by[1235]['priceOnly'] is False and by[1235]['score'] == 0
    assert by[1235]['meal_class'] == 'snack_side' and 'evtl. ausgelistet' in (by[1235].get('variant_note') or '')

    # Hofer #859 canned mushrooms & #3487 XXL Lasagne EAN
    assert by[859]['stage'] == 'veg' and by[859]['meal_class'] == 'component' and by[859]['component'] is True
    assert by[3487]['ean'] == '4069365963722' and by[3487]['priceOnly'] is True


def test_sc59_offswitch_reproduces_sc58_and_prior_versions_bit_exact(tmp_path):
    d_sc59_off1 = _export(tmp_path, SNAP, SC59_LINZ_LOKAL='0')
    d_sc59_off2 = _export(tmp_path, SNAP, GOOD_CHOICE_DISABLE_SC59='1')
    assert d_sc59_off1['dataVersion'] == 'e85580421d3b'
    assert d_sc59_off2['dataVersion'] == 'e85580421d3b'
    assert sum(bool(r.get('rankable')) for r in d_sc59_off1['rows']) == 167
    assert sum(bool(r.get('rankableLight')) for r in d_sc59_off1['rows']) == 92
