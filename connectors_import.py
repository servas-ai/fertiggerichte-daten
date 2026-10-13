"""Convert food-connectors output (/tmp/fetch.json or argv) into scored.json-compatible rows -> connectors_new.json"""
import json,re,sys
src=sys.argv[1] if len(sys.argv)>1 else '/tmp/fetch.json'
P=json.load(open(src))['products']
S=json.load(open('scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={k(x['name']) for x in S}; urls={x.get('url') for x in S}
OK=re.compile(r'Fertiggerichte|Kochboxen|Menüs & Dosengerichte|Schnelle Küche > Suppen',re.I)
BAD=re.compile(r'Baby|Basisfix|Suppenwürfel|Pasta, Reis|Frische Pasta',re.I)
out,seen=[],set()
for p in P:
    n=p['nutrition_100g']; c=p.get('category') or ''
    if p['source']=='gurkerl' and (not OK.search(c) or BAD.search(c)): continue
    if not(p['price_eur'] and n.get('protein') is not None and n.get('kcal') and p['size_g']): continue
    if k(p['name']) in names or p['source_url'] in urls or k(p['name']) in seen: continue
    if re.search(r'teig|wonton|nuggets|sticks|gebackene champignons|safari|flügerl|frühlingsrollen|palatschinken|mohnnudeln|grießnockerl',p['name'],re.I) or c.endswith('Knödel') or 'Asia Nudeln' in c: continue
    seen.add(k(p['name'])); g=p['size_g']
    pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Kühlregal (Menüschale/frisch)' if 'Kühlregal' in c else 'Konserve/Dose/Glas' if 'Vorratsschrank' in c else None
    out.append(dict(name=p['name'],brand=p['brand'],store=p['store'],price_eur=p['price_eur'],size_g=g,
      price_per_kg=round(p['price_eur']/g*1000,2),url=p['source_url'],image_url=p['image_url'],
      **{f'{x}_100':n.get(x) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
      protein_pack=round(n['protein']*g/100,1),kcal_pack=round(n['kcal']*g/100),manufacturer=p['producer'],producer_id=p['producer_id'],
      origin=p['origin'],category=c.split(' > ')[-1],price_source=f"food-connectors/{p['source']} {p['fetched_at'][:10]}",price_date=p['fetched_at'][:10],
      nut_source=f"{p['store']} API",packaging_hint=pk,ean=p['ean'],delivery='Gurkerl.at liefert NICHT nach Linz (nur Wien/NÖ-Umland, geprüft 2026-10-13)' if p['source']=='gurkerl' else None))
json.dump(out,open('connectors_new.json','w'),ensure_ascii=False,indent=1)
print(len(out)); [print(' ',x['name'],x['price_eur'],x['protein_100'],x['category']) for x in out]
