import json,re
T='2026-10-12'
IP_CH="Richtwert (keine Herstellerangabe): Pot-in-Pot – Inhalt in hitzefeste Schale auf Dampfeinsatz, 250 ml Wasser in den Innentopf, Pressure Cook HIGH 4–6 Min., Quick Release; umrühren, Kerntemp. ≥75 °C prüfen."
IP_TK="Richtwert (keine Herstellerangabe): Tiefgekühlt – Pot-in-Pot, 250 ml Wasser, Pressure Cook HIGH 10–12 Min., Quick Release; umrühren, ≥75 °C prüfen."
IP_KN="Richtwert (keine Herstellerangabe): Knödel/Nockerl auf Dampfeinsatz, 250 ml Wasser, Steam LOW (TK) 8–10 Min., Quick Release (oder klassisch in Suppe/Wasser ziehen lassen)."
IP_CAN="Richtwert (keine Herstellerangabe): Dose/Glas in Topf entleeren, Sauté 'Less/Normal' 4–6 Min. unter Rühren erhitzen; oder Pot-in-Pot 250 ml Wasser, HIGH 3 Min., Quick Release."
IP_DOUGH="Kein Multipot-Gericht (Teig/Snack/Backofenprodukt) – Backofen/Air-Fry-Deckel lt. Packung."
IP_NUG="Richtwert: Instant Pot Pro ohne Air-Fry-Deckel ungeeignet (würde matschig) – Backofen/Air-Fryer lt. Packung; mit Air-Fry-Deckel ca. 200 °C 10–12 Min."
KEYS=['name','brand','store','price_eur','size_g','price_per_kg','url','image_url','kcal_100','protein_100','fat_100','satfat_100','carbs_100','sugar_100','fiber_100','salt_100','protein_pack','kcal_pack','nutriscore','manufacturer','producer_id','origin','bio','veg','prep','instantpot','category','packaging','price_source','price_date','ean','notes']
rows=[]
def add(**k):
  r={x:None for x in KEYS}; r.update(store='HOFER',bio=False); r.update(k)
  if r['price_eur'] and r['size_g'] and not r['price_per_kg']: r['price_per_kg']=round(r['price_eur']/r['size_g']*1000,2)
  if r['protein_100'] is not None and r['size_g']: r['protein_pack']=round(r['protein_100']*r['size_g']/100,1)
  if r['kcal_100'] is not None and r['size_g']: r['kcal_pack']=round(r['kcal_100']*r['size_g']/100)
  rows.append(r)
# OFF nutrition (AT tagged)
keep={h['code']:h for h in json.load(open('hg/keep.json'))}
def nut(code):
  h=keep.get(code); 
  if not h: return {}
  n=h.get('nutriments') or {}
  g=lambda k:n.get(k+'_100g')
  kc=g('energy-kcal')
  return dict(kcal_100=kc,protein_100=g('proteins'),fat_100=g('fat'),satfat_100=g('saturated-fat'),carbs_100=g('carbohydrates'),sugar_100=g('sugars'),fiber_100=g('fiber'),salt_100=g('salt'),image_url=h.get('image_front_url'),ean=code,producer_id=', '.join(c for c in (h.get('emb_codes') or []) if re.match(r'[A-Z]{2} ',c)) or None)
WK='wokostswas.at Kategorie Fertigprodukte (k54/k30), Hofer-Regalpreis, abgerufen'
WKU='https://wokostswas.at/k54/fertigprodukte'
# 1) wokostswas Good Choice / Cucina Nobile chilled (current)
wk=[("Cevapcici mit Letscho und Reis","Good Choice",3.06,400,'https://wokostswas.at/p3517/good-choice-cevapcici-mit-letscho-und-reis-400g',None,IP_CH,'Kühlschale (Fertiggericht)'),
("Faschierte Laibchen mit Kartoffelpüree","Good Choice",3.06,430,WKU,'4099200146256',IP_CH,'Kühlschale (Fertiggericht)'),
("Gelbes Gemüsecurry mit Basmatireis","Good Choice",3.39,400,'https://wokostswas.at/p3524/good-choice-gelbes-gemuesecurry-mit-basmatireis-400g','4099200146324',IP_CH,'Kühlschale (Fertiggericht)'),
("Kärntner Kasnudeln","Good Choice",3.09,370,WKU,None,IP_CH,'Kühlschale (Fertiggericht)'),
("Pinzgauer Käsespätzle","Good Choice",3.06,380,'https://wokostswas.at/p3514/good-choice-pinzgauer-kaesespaetzle-380g',None,IP_CH,'Kühlschale (Fertiggericht)'),
("Schwammerlsauce mit Serviettenknödel","Good Choice",3.06,380,WKU,'4099200146263',IP_CH,'Kühlschale (Fertiggericht)'),
("Tortelloni Carne","Good Choice",2.29,400,WKU,'4099200229034',"Richtwert: frische Pasta – Pressure Cook nicht nötig; in Wasser/Sauté kochen 2–3 Min. lt. Packung (oder HIGH 1 Min. mit Wasser bedeckt, Quick Release).",'Kühlbeutel/Schale, Frischpasta (Schutzatmosphäre)'),
("Tortelloni mit Käsefüllung","Good Choice",2.29,400,'https://wokostswas.at/p3540/good-choice-tortelloni-mit-kaesefuellung-400g','4099200229058',"Richtwert: frische Pasta – Sauté/Wasser 2–3 Min. lt. Packung (oder HIGH 1 Min. bedeckt, Quick Release).",'Kühlbeutel/Schale, Frischpasta (Schutzatmosphäre)'),
("Tortelloni mit Spinat & Ricotta","Good Choice",2.29,400,WKU,None,"Richtwert: frische Pasta – Sauté/Wasser 2–3 Min. lt. Packung (oder HIGH 1 Min. bedeckt, Quick Release).",'Kühlbeutel/Schale, Frischpasta (Schutzatmosphäre)'),
("Burger Cheese","Good Choice",2.69,300,WKU,None,IP_DOUGH,'Kühlverpackung Snack'),
("Burger Chicken","Good Choice",2.69,300,WKU,None,IP_DOUGH,'Kühlverpackung Snack'),
("Eiersalat","Good Choice",2.29,400,WKU,None,"Kalt verzehren – kein Kochen.",'Kühlbecher Feinkost'),
("Nudelsalat","Good Choice",2.29,400,WKU,None,"Kalt verzehren – kein Kochen.",'Kühlbecher Feinkost'),
("Steinofenpizza Diavolo","Cucina Nobile",3.39,430,WKU,None,IP_DOUGH,'TK-Pizza Karton/Folie'),
("Steinofenpizza Prosciutto","Cucina Nobile",3.39,430,WKU,None,IP_DOUGH,'TK-Pizza Karton/Folie')]
fq={}
for x in json.load(open('frozen_quick.json')):
  m=re.search(r'/product/(\d+)',x.get('url') or '')
  if m: fq[m.group(1)]=x
for n,b,p,s,u,ean,ip,pk in wk:
  r=dict(name=n,brand=b,price_eur=p,size_g=s,url=u,instantpot=ip,packaging=pk,price_source=WK+' '+T,price_date=T,category='ready_meal' if 'Fertig' in pk or 'pasta' in pk.lower() else 'other')
  if ean:
    nn=nut(ean) or {}
    if not nn and ean in fq:
      x=fq[ean]; nn={k:x[k] for k in ['kcal_100','protein_100','fat_100','satfat_100','carbs_100','sugar_100','fiber_100','salt_100','image_url','producer_id']}; nn['ean']=ean
    r.update(nn); r['notes']='Nährwerte Open Food Facts EAN '+ean+('; OFF-Packungsgröße 400 g' if ean=='4099200146256' else '')
  if n=='Eiersalat': r['notes']='wokostswas schreibt "Eisalat"'
  add(**r)
# 2) wokostswas Primana TK (Hofer)
for n,p,s,ip,pk in [("Chicken Nuggets",4.49,750,IP_NUG,'TK-Beutel'),("Frittaten Suppeneinlage",4.49,700,"Suppeneinlage: in heißer Suppe (Sauté) 2–3 Min. ziehen lassen.",'TK-Beutel'),("Grießnockerl",4.49,700,IP_KN,'TK-Beutel'),("Leberknödel",4.49,700,IP_KN,'TK-Beutel'),("Snackbox Crispy Chili Cheese Nuggets",2.49,250,IP_NUG,'TK-Karton'),("Snackbox Crispy Mozzarella Sticks",2.49,250,IP_NUG,'TK-Karton'),("Snackbox Frischkäse Jalapenos",2.49,250,IP_NUG,'TK-Karton')]:
  add(name=n,brand='Primana',price_eur=p,size_g=s,url='https://wokostswas.at/k30/fertigprodukte' if n!='Leberknödel' else 'https://wokostswas.at/p3062/primana-leberknoedel-700g',instantpot=ip,packaging=pk,price_source='wokostswas.at k30, Hofer-Preis, abgerufen '+T,price_date=T,category='frozen')
# 3) hofer.at live (Aktion / neu)
add(name='Hot Dog',brand='Good Choice',price_eur=2.49,size_g=280,url='https://www.hofer.at/de/produkt/good-choice-hot-dog-000000000000741950',image_url='https://dm.emea.cms.aldi.cx/is/image/aldiprodeu/product/jpg/scaleWidth/232/6584088d-2277-4d87-9ccf-265c5363f95e/Hot%20Dog',instantpot=IP_DOUGH,packaging='Kühlverpackung Snack',price_source='hofer.at Produktsuche live '+T+' (verfügbar seit 02.10.2026)',price_date=T,category='other')
add(name='XXL Lasagne',brand='Primana',price_eur=7.49,url='https://www.hofer.at/de/produkt/primana-xxl-lasagne-000000000000739541',instantpot="Richtwert: große Schale passt meist nicht – portionsweise Pot-in-Pot HIGH 6–8 Min., Quick Release; sonst Backofen.",packaging='Kühlschale XXL',price_source='hofer.at Produktsuche live '+T+' (Aktion, verfügbar seit 02.10.2026; Größe auf Kachel nicht angegeben)',price_date=T,category='ready_meal')
add(name='XXL Chicken Nuggets',brand='Primana',price_eur=7.49,size_g=1500,url='https://www.hofer.at/de/produkt/primana-xxl-chicken-nuggets-000000000000494358',instantpot=IP_NUG,packaging='TK-Beutel',price_source='hofer.at Produktsuche live '+T+' (Aktion; Grundpreis 4,99 €/kg → 7,49 € berechnet)',price_date=T,category='frozen')
add(name='Pikante Knödel',brand='Primana',price_eur=2.39,size_g=1000,url='https://www.billiga.at/at/angebot/hofer-central-20261009-h42-p14-023',instantpot=IP_KN,packaging='TK-Beutel',price_source='Hofer-Flugblatt KW41/2026 S.14 via billiga.at, Aktion gültig bis 10.10.2026 (regulär 3,99 €)',price_date='2026-10-09',category='frozen')
# 4) OFF AT-tagged meals without current price
used={r['ean'] for r in rows if r['ean']}
pk_map=lambda n,c: 'Dose' if re.search('suppe|chili|curry|bohnen',n,re.I) and c.startswith('40992001215') or c=='4099200121574' else ('Beutel (Instant)' if re.search('Le Gusto',n) else None)
for c,h in keep.items():
  if c in used: continue
  n=h.get('product_name') or h.get('product_name_de'); b=(h.get('brands') or [''])[0]
  if re.search(r'teig|Aufstrich|Leberwurst|Manzana|Salatcup|Kartoffelsalat|Basis für|Pizza Snack|Wrap',n,re.I): continue
  q=h.get('quantity') or ''; m=re.match(r'([\d.,]+)\s*(g|kg)',q.strip(),re.I); s=None
  if m: s=float(m.group(1).replace(',','.'))*(1000 if m.group(2).lower()=='kg' else 1)
  cats=' '.join(h.get('categories_tags') or [])
  froz='frozen' in cats
  can = c.startswith('40992001215') or c=='4099200121574'
  pk='Dose' if can else ('TK' if froz else ('Trockenbeutel' if b=='Le Gusto' else 'Kühlschale/gekühlt (lt. OFF-Kategorie unklar)'))
  ip=IP_CAN if can else (IP_KN if re.search('knödel',n,re.I) else (IP_TK if froz else IP_CH))
  if b=='Le Gusto': ip="Instant-Suppe/Mix: mit heißem Wasser (Sauté) lt. Packung zubereiten."
  if 'pizza' in n.lower(): ip=IP_DOUGH
  r=dict(name=n,brand=b.replace("'",'').title() if b.islower() or b.isupper() else b.replace("Leibspeis'","Leibspeis"),size_g=s,url='https://world.openfoodfacts.org/product/'+c,instantpot=ip,packaging=pk,category='ready_meal',price_source='kein aktueller 2026-Preis gefunden',notes='Open Food Facts, Land AT, zuletzt bearbeitet '+__import__('time').strftime('%Y-%m-%d',__import__('time').gmtime(h.get('last_modified_t',0)))+'; aktuelle Verfügbarkeit bei Hofer nicht bestätigt')
  r.update(nut(c)); add(**r)
# 5) hofer.at Sortiment pages w/ 2025 prices (heisse-preise), only brand matches, not dup
hl=[x for x in json.load(open('hofer_lidl.json')) if x['store']=='HOFER' and re.search(r'^(GOOD CHOICE|PRIMANA|CUCINA)',x['name'])]
names={r['name'].lower() for r in rows}
for x in hl:
  nm=re.sub(r'^(GOOD CHOICE|PRIMANA|CUCINA NOBILE|CUCINA)\s+','',x['name']).strip(); br=re.match(r'^(GOOD CHOICE|PRIMANA|CUCINA NOBILE|CUCINA)',x['name']).group(1).title()
  nm2=re.sub(r'\s*\d+\s*g\s*$','',nm).strip()
  if any(nm2.lower().startswith(n2) or n2 in nm2.lower() for n2 in ['pinzgauer käsespätzle','schwammerlsauce mit serviettenknödel']): continue
  can=re.search('Suppe|Chili',nm2) and br=='Primana'
  kn='Knödel' in nm2
  add(name=nm2,brand=br,price_eur=None,size_g=x['size_g'],url=x['url'],instantpot=IP_CAN if can else (IP_KN if kn else IP_CH),packaging='Dose' if can else ('TK-Beutel' if kn else 'Kühlschale (Fertiggericht)'),category='ready_meal',price_source='nur Altpreis: heisse-preise.io Stand 2025-07-03 = %.2f € (kein 2026-Preis gefunden)'%x['price_eur'],price_date=None,notes='hofer.at Sortiment-URL aus 2025, aktuelle Listung nicht bestätigt; Verpackung abgeleitet')
# Swiss-tagged Good Choice items in frozen_quick: exclude, note
for r in rows:
  r['brand']=r['brand'].replace('Leibspeis\'','Leibspeis') if r['brand'] else r['brand']
json.dump(rows,open('hofer_goodchoice.json','w'),ensure_ascii=False,indent=1)
print(len(rows),sum(1 for r in rows if r['price_date'] and r['price_date'].startswith('2026')),sum(1 for r in rows if r['protein_100'] is not None))
for r in rows: print(r['brand'],'|',r['name'],r['size_g'],r['price_eur'],r['protein_100'],r['packaging'])
