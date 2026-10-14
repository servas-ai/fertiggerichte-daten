"""Sensecheck 8: every. (every-foods.com) online provider is in the app; online frozen providers are packed as TK;
pure finished-meal providers never show up as Beilage/Zutat/Protein component."""
import json
P='/workspace/fertig-app/public/data.json'
MEALPREP_ONLY={'PrepMyMeal','Juit','every.','LiveFresh','FitTaste'}

def _rows(): return json.load(open(P))['rows']

def test_every_rows_present_and_consistent():
    E=[r for r in _rows() if r.get('store')=='every.']
    assert len(E)>=45, len(E)
    assert all(r.get('brand')=='every.' and r.get('price') and r.get('size') for r in E)
    assert all(r.get('vegan') for r in E), 'every. range is plant-based → vegan'
    assert all(r.get('pack')=='Tiefkühl (TK)' and not r.get('dry') for r in E)
    assert sum(bool(r.get('rankable')) for r in E)>=10

def test_online_storage_tk_not_dry():
    R=[r for r in _rows() if r.get('src')=='online_mealprep.json']
    bad=[(r['store'],r['name'],r['pack']) for r in R if r.get('pack')!='Tiefkühl (TK)']
    assert not bad, bad[:10]

def test_mealprep_providers_are_meals():
    bad=[(r['store'],r['name'],r['stage']) for r in _rows() if r.get('src')=='online_mealprep.json' and r.get('store') in MEALPREP_ONLY and r.get('stage') not in ('meal','stew')]
    assert not bad, bad[:10]
