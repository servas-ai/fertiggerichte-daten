import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'
TMP = 'online_availability_9999-sc54-test.json'

def _export(tmp_path, snap=SNAP, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=snap, **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))

def test_p1_back_in_stock_gets_pli_back(tmp_path):
    a = json.load(open(os.path.join(ROOT, 'analysis', SNAP)))
    a['unavailable_uids'] = [u for u in a['unavailable_uids'] if u != 'npikslzflt']  # #3153 Oriental Bowl back in stock
    a['file'] = TMP
    p = os.path.join(ROOT, 'analysis', TMP)
    json.dump(a, open(p, 'w'))
    try:
        d = _export(tmp_path, TMP)
        off = _export(tmp_path, TMP, SC54_BACKINSTOCK='0')
    finally:
        os.remove(p)
    r = next(x for x in d['rows'] if x['id'] == 3153)
    assert not r.get('sold_out') and r.get('variant_note') != 'ausverkauft'
    assert r.get('rankable') and r.get('pli') is not None
    r0 = next(x for x in off['rows'] if x['id'] == 3153)
    assert r0.get('pli') is None  # bug reproduced without the fix

def test_p1_current_snapshot_unchanged(tmp_path):
    d = _export(tmp_path, SNAP, SC54_PREPMYMEAL='0')
    assert d['dataVersion'] == 'ce8d8d111664'
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 158
    d_alt = _export(tmp_path, SNAP, GOOD_CHOICE_DISABLE_SC54_PREPMYMEAL='1')
    assert d_alt['dataVersion'] == 'ce8d8d111664'
    assert sum(bool(r.get('rankable')) for r in d_alt['rows']) == 158

def test_p1_2_xl_butter_chicken_and_kasespatzle_back_in_stock(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}
    r2785 = by[2785]
    assert r2785['uid'] == 'honb7zkubm'
    assert r2785['url'] == 'https://prepmymeal.at/products/butter-chicken-xl-2-portionen'
    assert r2785['size'] == 1000.0
    assert r2785['price'] == 12.48 and r2785['ppk'] == 12.48
    assert not r2785.get('sold_out') and r2785.get('rank_excluded_reason') is None and r2785.get('variant_note') is None
    assert r2785['rankable'] is True and r2785['pli'] == 41.7

    r2788 = by[2788]
    assert r2788['uid'] == 'd1u0iuvtkz'
    assert r2788['url'] == 'https://prepmymeal.at/products/kasespatzle-mit-hahnchen'
    assert r2788['size'] == 1000.0
    assert r2788['price'] == 12.48 and r2788['ppk'] == 12.48
    assert not r2788.get('sold_out') and r2788.get('rank_excluded_reason') is None and r2788.get('variant_note') is None
    assert r2788['rankable'] is True and r2788['pli'] == 43.2

    snap = json.load(open(os.path.join(ROOT, 'analysis', SNAP)))
    assert 'honb7zkubm' not in snap['unavailable_uids']
    assert 'd1u0iuvtkz' not in snap['unavailable_uids']

def test_p1_3_prepmymeal_legacy_and_lachs_reconciliation(tmp_path):
    d = _export(tmp_path, SNAP)
    by = {r['id']: r for r in d['rows']}

    # #1533 Hähnchen im Kokosmantel -> live handle, 500 g, €10.49, ppk 20.98, rankable
    r1533 = by[1533]
    assert r1533['uid'] == 'nh0zjp4tq5'
    assert r1533['url'] == 'https://prepmymeal.at/products/hahnchen-im-kokosmantel-1'
    assert r1533['size'] == 500.0 and r1533['price'] == 10.49 and r1533['ppk'] == 20.98
    assert r1533['rankable'] is True and r1533['pli'] == 40.5

    # #1532 Kichererbsen mit Harissa -> ausgelistet / sold_out
    r1532 = by[1532]
    assert r1532['uid'] == 'mumdjo42mt'
    assert r1532['sold_out'] is True and r1532['rankable'] is False
    assert r1532['pli'] is None and r1532['rank_excluded_reason'] == 'ausverkauft (Shop: nicht verfügbar)'
    assert r1532['variant_note'] == 'ausverkauft'

    # #1534, #1535, #1536 -> size backfilled while keeping dupOf (2861, 2805, 2863) intact
    for rid, sz, keep in ((1534, 450.0, 2861), (1535, 400.0, 2805), (1536, 460.0, 2863)):
        r = by[rid]
        assert r['size'] == sz and r['size'] == by[keep]['size']
        assert r['dupOf'] == keep and r['dupOfUid'] == by[keep]['uid']
        assert r['rankable'] is False and r['pli'] is None

    # #2847 Lachs, Reis, grüne Bohnen -> live handle -1, 490 g, €12.49, ppk 25.49
    r2847 = by[2847]
    assert r2847['uid'] == 'jydu61eatc'
    assert r2847['url'] == 'https://prepmymeal.at/products/lachs-reis-grune-bohnen-1'
    assert r2847['size'] == 490.0 and r2847['price'] == 12.49 and r2847['ppk'] == 25.49
    assert r2847['rankable'] is True and r2847['pli'] == 35.6

    # Active 6er-Box URLs (e.g. #2837) remain untouched
    assert by[2837]['url'] == 'https://prepmymeal.at/products/lachs-blumenkohl-grune-bohnen'
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 161
