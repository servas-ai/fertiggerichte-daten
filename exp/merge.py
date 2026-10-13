import json,re,glob
S=json.load(open('../scored.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={k(x['name']) for x in S}; urls={x.get('url') for x in S}
P=[]
for f in glob.glob('gk_*.json'):
  try: d=json.load(open(f))
  except: continue
  P+=d['products'] if isinstance(d,dict) else d
P+=json.load(open('billa_new.json'))
OK=re.compile(r'Fertiggericht|Menüschalen|Menüs & Dosengerichte|Suppen|Joghurt & Desserts > (Pudding|Desserts|Milchreis)|Kühlwaren > Desserts|Salate & Bowls|Mehlspeisen|Tiefkühlgerichte|Pikante & Süße Knödel|Süßes & Desserts|Desserts ungekühlt|Rein Pflanzlich > Kühlregal > Desserts|Salate & Dressing > Salate',re.I)
BAD=re.compile(r'Baby|Basisfix|Basis- & Fix|Suppenwürfel|Suppen & Fonds > Fonds|Dressing$|Eis|^BILLA:Salate',re.I)
NAME_BAD=re.compile(r'\bfond\b|suppenwürfel|würze|brühe(?!.*mit)|bouillon|teig\b|teigblätter|strudelteig|dressing|sauce$|sugo|pesto|einlage|frittaten|nockerl$|backerbsen|croutons|pulver|\bfix\b|basis|gewürz|nuggets|sticks|fruchtzwerge|fond\b|grießnockerl|mini-frühlingsrollen|pommes|kroketten|rösti$|eiscreme|drink|shake',re.I)
def course(n,c):
  t=(n+' '+c).lower()
  if re.search(r'dessert|pudding|milchreis|grieß|mousse|tiramisu|panna|strudel|schmarrn|germknödel|marillen|topfenknödel|zwetschken|nougat|mehlspeis|kuchen|creme|kompott|schoko|vanille',t): return 'Nachspeise'
  if re.search(r'suppe|salat|antipasti|vorspeise|carpaccio',t) and not re.search(r'suppentopf|eintopf|bowl',t): return 'Vorspeise'
  return 'Hauptspeise'
out,seen=[],set()
for p in P:
  n=p.get('nutrition_100g') or {}; c=p.get('category') or ''
  if not OK.search(c) or BAD.search(c) or (p['source']=='billa' and c.endswith('> Salate') and not re.search(r'nudel|reis|bowl|couscous|bulgur|quinoa|linsen|huhn|thunfisch',p['name'],re.I)) or NAME_BAD.search(p['name']): continue
  if not(p.get('price_eur') and p.get('size_g') and p.get('image_url')): continue
  if k(p['name']) in names or p['source_url'] in urls or k(p['name']) in seen: continue
  seen.add(k(p['name'])); g=p['size_g']
  pk='Tiefkühl (TK)' if 'Tiefkühl' in c else 'Kühlregal (Menüschale/frisch)' if re.search('Kühl',c) else 'Konserve/Dose/Glas' if re.search('Vorratsschrank|ungekühlt',c) else None
  has=n.get('protein') is not None and n.get('kcal')
  out.append(dict(name=p['name'],brand=p['brand'],store=p['store'],price_eur=p['price_eur'],size_g=g,
    price_per_kg=round(p['price_eur']/g*1000,2),url=p['source_url'],image_url=p['image_url'],
    **{f'{x}_100':n.get(x) for x in ('kcal','protein','fat','satfat','carbs','sugar','fiber','salt')},
    protein_pack=round(n['protein']*g/100,1) if has else None,kcal_pack=round(n['kcal']*g/100) if has else None,
    manufacturer=p.get('producer'),producer_id=p.get('producer_id'),origin=p.get('origin'),category=c.split(' > ')[-1],
    course=course(p['name'],c),
    price_source=f"food-connectors/{p['source']} {p['fetched_at'][:10]}",price_date=p['fetched_at'][:10],
    nut_source=(f"{p['store']} API" if n else None),packaging_hint=pk,ean=p.get('ean'),delivery=None))
json.dump(out,open('../expand_v5.json','w'),ensure_ascii=False,indent=1)
import collections
print(len(out),collections.Counter(x['store'] for x in out),collections.Counter(x['course'] for x in out),sum(1 for x in out if x['protein_100'] is not None))
