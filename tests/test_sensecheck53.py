import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _export(tmp_path, **env):
    out = tmp_path / 'o.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY='online_availability_2026-10-24.json', SC54_PREPMYMEAL='0', **env)
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))

def test_p1_sold_out_rows_have_uniform_fields(tmp_path):
    d = _export(tmp_path)
    so = [r for r in d['rows'] if r.get('sold_out')]
    assert {r['id'] for r in so} >= {2785, 2788, 2851, 3152, 3153}
    for r in so:
        assert r.get('pli') is None and r.get('pliLight') is None and not r.get('rankable')
        assert r.get('rank_excluded_reason') == 'ausverkauft (Shop: nicht verfügbar)'
        assert r.get('variant_note') == 'ausverkauft'
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 158

def test_p1_off_switch_restores_ddd0(tmp_path):
    d = _export(tmp_path, SC53_SOLDOUT='0')
    assert d['dataVersion'] == 'ddd0a39a9ce1'
