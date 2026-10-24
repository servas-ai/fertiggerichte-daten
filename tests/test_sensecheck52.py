"""sensecheck 52 P1: fresh availability snapshot marks #2851 sold out, #2783/#2824 move up."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_snapshot_2026_10_24_sold_out(tmp_path):
    out = tmp_path / 'd.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY='online_availability_2026-10-24.json')
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    d = json.load(open(out))
    by = {r['uid']: r for r in d['rows']}
    assert by['zc8jvxvyj9']['sold_out'] is True and not by['zc8jvxvyj9']['rankable']
    assert 2851 not in d['topPLI'] and 2851 not in d['topPE']
    assert 2783 in d['topPLI'] and 2824 in d['topPE']
    for k in ('topPLI', 'topHealth', 'topPE', 'topLight'):
        assert len(d[k]) == 30, k
