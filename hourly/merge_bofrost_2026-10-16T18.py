# hourly T18 (2026-10-16T18): merge bofrost* warm Nachspeisen (Mehlspeisen: Knödel, Schmarrn, Nockerl, Mohnnudeln, Strudel,
# Palatschinken) + warm Vorspeisen (Frühlingsrollen, Teigtaschen, Flammkuchen, gefüllte Palatschinken, Kaspressknödel) into
# connectors_new.json. Source: food-connectors bofrost adapter fetch(category="desserts"/"starters") on the public bofrost.at
# product pages (JSON-LD price, pack line, nutrition per 100 g, ingredients), 1.2 s/request, image HEAD-checked.
# Same row schema as bofrost_build.rows(); only published values, nothing invented. Idempotent (skips existing URLs/articles).
import json, os, re, sys
os.chdir('/workspace/fertig'); sys.path.insert(0, '.')
import bofrost_build as bb
SLOT = '2026-10-16T18'
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/h18/bof_new.json'
prods = json.load(open(SRC))
def consistent(n):
    k = n.get('kcal'); f, p, c = n.get('fat'), n.get('protein'), n.get('carbs')
    if k is None or not (5 <= k <= 600): return False
    if None in (f, p, c): return True
    if (n.get('sugar') or 0) > c + 0.5 or (n.get('satfat') or 0) > f + 0.5: return False
    return abs(9*f + 4*p + 4*c + 2*(n.get('fiber') or 0) - k) <= max(25, 0.25*k)
snap = '/tmp/h18/bof_snapshot.json'
json.dump({'fetched': '2026-10-16T18', 'products': prods}, open(snap, 'w'), ensure_ascii=False)
course = {p['source_url']: p['extra'].get('course') for p in prods}
cn = json.load(open('connectors_new.json'))
have = set()
for f in ('online_mealprep.json', 'connectors_new.json'):
    for r in json.load(open(f)):
        if 'bofrost' in str(r.get('url')): have.add(re.search(r'_(\d{4,6})\.html', r['url']).group(1))
new, rej = [], []
byurl = {p['source_url']: p for p in prods}
for r in bb.rows(snap):
    p = byurl[r['url']]; a = re.search(r'_(\d{4,6})\.html', r['url']).group(1)
    if a in have: rej.append((r['name'], 'schon vorhanden')); continue
    if not consistent(p['nutrition_100g']): rej.append((r['name'], f"Nährwerte inkonsistent {p['nutrition_100g']}")); continue
    if p['extra'].get('availability') not in ('InStock', None): rej.append((r['name'], f"nicht lieferbar ({p['extra'].get('availability')})")); continue
    r['gang_hint'] = course[r['url']]
    r['delivery'] = 'bofrost* Heimlieferung (eigene Fahrer, ganz Österreich; Niederlassung Sattledt OÖ)'
    r['added_slot'] = SLOT
    r['hourly_kind'] = 'Warme Nachspeise (Mehlspeise)' if course[r['url']] == 'dessert' else 'Warme Vorspeise / Snack'
    if p['extra'].get('ingredients'): r['ingredients'] = p['extra']['ingredients'][:2000]
    new.append(r); have.add(a)
# rows skipped by bofrost_build.rows (no image 200 / price / size / protein)
kept = {r['url'] for r in new} | {u for u in byurl if re.search(r'_(\d{4,6})\.html', u).group(1) in have}
for u, p in byurl.items():
    if u not in kept: rej.append((p['name'], 'kein Preis/Gewicht/Eiweiß/Foto an der Quelle'))
if not os.environ.get('DRY'):
    json.dump(cn + new, open('connectors_new.json', 'w'), ensure_ascii=False, indent=1)
json.dump({'slot': SLOT, 'added': new, 'rejected': rej}, open(f'hourly/added_{SLOT}.json', 'w'), ensure_ascii=False, indent=1)
print('added', len(new), 'rejected', len(rej)); [print(' -', *x) for x in rej]
