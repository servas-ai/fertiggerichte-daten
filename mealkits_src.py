"""mealkits_2026-10-13.json (food-connectors adapters/mealkits.py) -> mealkits_src.json, an input for score.py.
Only rows with nutrition. segment='meal_kit' rows are ranked separately (score.py sets rankable=False, rankable_mealkit)."""
import json
P = json.load(open('mealkits_2026-10-13.json'))
STORE = {'hellofresh': 'HelloFresh', 'marleyspoon': 'Marley Spoon'}
MAN = {'hellofresh': 'HelloFresh Österreich GmbH', 'marleyspoon': 'MarleySpoon GmbH'}
out = []
for r in P['rows']:
    np, n1 = r.get('nutrition_portion') or {}, r.get('nutrition_100g') or {}
    if not np.get('kcal'): continue
    sg = r.get('serving_g')
    out.append(dict(name=r['name'] + (' ' + r['headline'] if r.get('headline') else ''), brand=STORE[r['provider']], store=STORE[r['provider']],
        price_eur=r.get('price_per_portion'), size_g=sg, price_per_kg=round(r['price_per_portion'] / sg * 1000, 2) if sg and r.get('price_per_portion') else None,
        url=r['url'], image_url=r.get('image_url'),
        kcal_100=n1.get('kcal'), protein_100=n1.get('protein'), fat_100=n1.get('fat'), satfat_100=n1.get('satfat'), carbs_100=n1.get('carbs'),
        sugar_100=n1.get('sugar'), fiber_100=n1.get('fiber'), salt_100=n1.get('salt'), protein_pack=np.get('protein'), kcal_pack=np.get('kcal'),
        manufacturer=MAN[r['provider']], packaging_raw='Kochbox', category='Kochbox (Meal-Kit, selbst kochen)', segment='meal_kit',
        delivers_4020=r.get('delivers_4020'), delivery_source=r.get('delivery_source'), allergens=r.get('allergens'), ingredients=r.get('ingredients'),
        provider_type='meal_kit', price_source=f"{r.get('price_source')} {r.get('fetched_at')} ({r.get('price_kind')})" if r.get('price_per_portion') else None,
        price_date=r.get('fetched_at'), price_kind=r.get('price_kind'), menu_week=r.get('week'), nutrition_basis_note=r.get('nutrition_100g_basis')))
json.dump(out, open('mealkits_src.json', 'w'), ensure_ascii=False, indent=1)
print(len(out))
