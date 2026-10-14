"""Sensecheck 6: no baby/infant food (HiPP etc.) in the sides list; plain veg named 'Babykarotten' may stay."""
import json,os,re,pytest
P='/workspace/fertig-app/public/data.json'
BABY=re.compile(r'\b(hipp|alete|bebivita|beba|aptamil|babylove|freche freunde)\b|babynahrung|beikost|gläschen|kleinkind|säugling|\bbaby\b',re.I)
@pytest.mark.skipif(not os.path.exists(P),reason='no app data.json')
def test_no_baby_food_in_sides():
    S=json.load(open(P))['sides']
    bad=[s['name'] for s in S if BABY.search((s.get('name') or '')+' '+(s.get('brand') or ''))]
    assert not bad, bad
    assert not any(re.search('hipp',(s.get('name') or '')+' '+(s.get('brand') or ''),re.I) for s in S)
    ids={s['id'] for s in S}
    assert all(c['veg'] in ids and (c['side'] is None or c['side'] in ids) for c in json.load(open(P))['combos'])
