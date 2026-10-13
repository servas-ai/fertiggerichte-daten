"""public/linz_providers.json (ready_meal rows only) -> linz_providers_src.json, an input for score.py.
grocery rows stay out. Keeps segment + delivers_4020. Store labels match build.py store()."""
import json, re
P = json.load(open('/workspace/fertig-app/public/linz_providers.json'))
STORE = {'fit2go': 'Fit to Go', 'fittaste': 'FitTaste', 'nordsee': 'NORDSEE', 'subway': 'Subway'}
PACK = {'fit2go': 'TK', 'fittaste': None, 'nordsee': None, 'subway': None}
CAT = {'fit2go': 'Fertiggericht TK Meal-Prep', 'fittaste': 'Fertiggericht im Glas', 'nordsee': 'to-go frisch', 'subway': 'to-go frisch'}
import re
nk = lambda t: re.sub(r'[^a-z0-9]', '', (t or '').lower())
try:
    OLD = {(nk(x.get('name')), x.get('store')): x for x in json.load(open('scored.json'))}
except Exception:
    OLD = {}
out = []
for r in P['rows']:
    if r['segment'] != 'ready_meal' or not r.get('kcal'): continue
    out.append(dict(name=r['name'], brand=r['brand'], store=STORE[r['provider']], price_eur=r.get('price'), size_g=r.get('size'),
        price_per_kg=r.get('ppk'), url=(r['url'] + '#' + re.sub(r'[^a-z0-9]+', '-', r['name'].lower()).strip('-')) if r['provider'] == 'subway' else r['url'], image_url=r.get('img'),
        kcal_100=r.get('kcal'), protein_100=r.get('p100'), fat_100=r.get('fat'), satfat_100=r.get('sat'), carbs_100=r.get('carbs'),
        sugar_100=r.get('sugar'), fiber_100=r.get('fib'), salt_100=r.get('salt'), protein_pack=r.get('protpack'), kcal_pack=r.get('kcalpack'),
        manufacturer={'fit2go': 'Fit2go GmbH', 'fittaste': 'FITTASTE23 GmbH', 'nordsee': 'NORDSEE', 'subway': 'Subway'}[r['provider']],
        packaging_raw=PACK[r['provider']], category=CAT[r['provider']], segment='ready_meal', delivers_4020=r.get('delivers_4020'), delivery_source=r.get('delivery_source'),
        allergens=r.get('allergens'), ingredients=r.get('ingredients'), provider_type=r.get('provider_type'),
        price_source=f"food-connectors/{r['provider']} {(r.get('fetched_at') or '')[:10]}" if r.get('price') else None,
        price_date=(r.get('fetched_at') or '')[:10] or None, nutrition_basis_note=r.get('nut_basis')))
for o in out:  # dedupe against existing rows: reuse their size so score.py's (name,size,store) key merges them
    old = OLD.get((nk(o['name']), o['store']))
    if old and old.get('size_g'): o['size_g'] = old['size_g']; o['_merged_into_existing'] = True
print('merged into existing:', sum(1 for o in out if o.get('_merged_into_existing')))
json.dump(out, open('linz_providers_src.json', 'w'), ensure_ascii=False, indent=1)
print(len(out))
