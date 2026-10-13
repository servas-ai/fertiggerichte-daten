import json,re,collections
h=json.load(open('heisse_preise_raw.json'))
idx={(x['store'],x['name'].strip().lower()):x for x in h if x['store'] in('billa','spar')}
m=json.load(open('billa_spar_meal_prices.json'))
sc=json.load(open('scored.json'))
norm=lambda s:re.sub(r'\W+',' ',(s or '').lower()).strip()
st=lambda s:'billa' if 'billa' in (s or '').lower() else 'spar' if 'spar' in (s or '').lower() else (s or '').lower()
seen={(st(x['store']),norm(x['name'])) for x in sc}
C=[]
for x in m:
  r=idx.get((x['store'],x['name'].strip().lower()))
  C.append(dict(x,id=r['id'] if r else None,src='meal_prices'))
names={(c['store'],norm(c['name'])) for c in C}
MEAL=re.compile(r'fertiggericht|eintopf|gulasch|suppe\b|cremesuppe|lasagne|risotto|curry|chili con|knödel|nockerl|spätzle|gnocchi|tortellini|tortelloni|ravioli|reis.*(beutel|express|minuten)|express.?reis|mikrowell|langkornreis.*kochbeutel|kochbeutel|tiefkühl.*(gericht|pfanne)|gemüsepfanne|wok.?gemüse|rahmspinat|rahmgemüse|blattspinat|kaiser.?gemüse|brokkoli|erbsen|fisolen|gemüsemischung|sous.?vide|geschnetzel|pfannengericht|bami|nasi|paella|kartoffelgratin|kartoffelpüree|püree|rösti|germknödel|schinkenfleckerl|krautfleckerl|eiernockerl|cevapcici|faschierte laibchen|cordon|gefüllte paprika|fleischlaberl|bolognese|ripperl|hendl.*(gegrillt|keulen)',re.I)
BAD=re.compile(r'würfel|würze|fix\b|basis|sauce$|soße|brühe|fond|suppenwürze|hund|katze|chips|snack|tee\b|bonbon|keks|rohmasse|teig|samen|saat|pulver(?!.*suppe)',re.I)
GSIDE=re.compile(r'reis|knödel|kartoffel|püree|rösti|spinat|gemüse|brokkoli|erbsen|fisolen|nockerl|spätzle|gnocchi|pommes|kroketten',re.I)
add=0
for x in h:
  if x['store']!='spar' or not MEAL.search(x['name']) or BAD.search(x['name']): continue
  d=(x.get('priceHistory') or [{}])[0].get('date','')
  if d<'2026': continue
  k=('spar',norm(x['name']))
  if k in names: continue
  names.add(k); add+=1
  q=x.get('quantity');u=x.get('unit')
  C.append(dict(name=x['name'],store='spar',price_eur=x['price'],qty=q,unit=u,price_per_kg=round(x['price']/q*1000,2) if q and u in('g','ml') else None,bio=x.get('bio'),last_price_change=d,price_source='heisse-preise.io latest-canonical 2026-10-12',id=x['id'],src='hp_spar'))
C=[c for c in C if (c['store'],norm(c['name'])) not in seen]
print(add,len(C),collections.Counter((c['store'],c['src']) for c in C), sum(1 for c in C if not c['id']))
json.dump(C,open('cand.json','w'),ensure_ascii=False)
