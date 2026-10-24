import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = 'online_availability_2026-10-24.json'
TMP = 'online_availability_9999-sc54-test.json'

def _export(tmp_path, snap, **env):
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
    d = _export(tmp_path, SNAP)
    assert d['dataVersion'] == 'ce8d8d111664'
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 158
