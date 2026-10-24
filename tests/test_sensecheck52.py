"""sensecheck 52 P1: fresh availability snapshot marks #2851 sold out, #2783/#2824 move up."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_snapshot_2026_10_24_sold_out(tmp_path):
    out = tmp_path / 'd.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY='online_availability_2026-10-24.json', SC54_PREPMYMEAL='0')
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    d = json.load(open(out))
    by = {r['uid']: r for r in d['rows']}
    assert by['zc8jvxvyj9']['sold_out'] is True and not by['zc8jvxvyj9']['rankable']
    assert 2851 not in d['topPLI'] and 2851 not in d['topPE']
    assert 2783 in d['topPLI'] and 2824 in d['topPE']
    for k in ('topPLI', 'topHealth', 'topPE', 'topLight'):
        assert len(d[k]) == 30, k


def _run(tmp_path, name, avail):
    out = tmp_path / f'{name}.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY=avail, SC54_PREPMYMEAL='0')
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    return json.load(open(out))


def test_p2_toplight_refills_to_30_when_light_dish_sold_out(tmp_path):
    """sensecheck 52 P2: topLight is rebuilt with _collapse, so a sold-out light dish is replaced (not shrunk to 29)."""
    base = _run(tmp_path, 'base', 'online_availability_2026-10-24.json')
    by_id = {r['id']: r for r in base['rows']}
    victim = base['topLight'][0]
    snap = json.load(open(os.path.join(ROOT, 'analysis', 'online_availability_2026-10-24.json')))
    snap['unavailable_uids'] = snap['unavailable_uids'] + [by_id[victim]['uid']]
    fn = '_test_sc52p2_availability.json'
    p = os.path.join(ROOT, 'analysis', fn)
    json.dump(snap, open(p, 'w'))
    try:
        d = _run(tmp_path, 'p2', fn)
    finally:
        os.remove(p)
    assert victim not in d['topLight'] and victim not in d['topLightUncapped']
    assert len(d['topLight']) == 30 and len(d['topLightUncapped']) == 30
    assert d['topLight'][:29] == [i for i in base['topLight'] if i != victim][:29]


def test_p2_xl_regex_matches_unbracketed_portions():
    src = open(os.path.join(ROOT, 'export_app.py')).read()
    import re as _re
    line = next(l for l in src.splitlines() if l.startswith('_XL=re.compile'))
    ns = {'re': _re}; exec(line, ns)
    assert ns['_XL'].search('Inzersdorfer Weinbeuschel 2 Portionen')
    assert ns['_XL'].search('Hähnchen Bowl Thai (XL, 2 Portionen)')


def test_p3_p4_dupof_links(tmp_path):
    d = _run(tmp_path, 'p3', 'online_availability_2026-10-24.json')
    by = {r['id']: r for r in d['rows']}
    for dup, keep in ((2859, 2854), (2822, 2821), (1534, 2861), (1535, 2805), (1536, 2863), (1770, 1769)):
        assert by[dup]['dupOf'] == keep and not by[dup]['rankable'], dup
        assert by[dup]['dupOfUid'] == by[keep]['uid'], dup
        assert by[keep].get('dupOf') is None, keep
        for k in ('topPLI', 'topPLIUncapped', 'topHealth', 'topHealthUncapped', 'topPE', 'topPEUncapped', 'topLight', 'topLightUncapped'):
            assert dup not in d[k], (dup, k)
    assert by[2854]['rankable']
    assert by[1769]['alsoAt'] == ['Billa'] and 'Billa #455' in by[1769]['rank_excluded_reason']
    assert sum(bool(r.get('rankable')) for r in d['rows']) == 158


def test_p3_off_switch_restores_pre_p3(tmp_path):
    out = tmp_path / 'off.json'
    e = dict(os.environ, GOOD_CHOICE_OUT=str(out), GOOD_CHOICE_AVAILABILITY='online_availability_2026-10-24.json', SC52_DUPOF='0', SC53_SOLDOUT='0')
    e.pop('ENFORCE_SHIPBOX_CAP', None)
    subprocess.run([sys.executable, 'export_app.py'], cwd=ROOT, env=e, check=True, capture_output=True)
    d = json.load(open(out))
    assert d['dataVersion'] == 'ccb1d68ff387' and sum(bool(r.get('rankable')) for r in d['rows']) == 159
