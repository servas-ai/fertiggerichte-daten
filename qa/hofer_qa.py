import json,re,collections
s=json.load(open('scored.json'))
H=[x for x in s if x.get('store')=='HOFER']
K=['name','brand','url','price_eur','size_g','kcal_100','protein_100','salt_100','producer_id','price_date','image_url']
for x in H:
  for k in K: x.setdefault(k,None)
  x['url']=x['url'] or ''
fx=[]
def add(name,url,action,field=None,old=None,new=None,reason=''):
  fx.append(dict(store='HOFER',name=name,url=url,action=action,field=field,old=old,new=new,reason=reason))
notmeal={'24228664':'Rohkost-Salat (Gemüse roh), kein Fertiggericht','24601221':'Chips/Snack','4099200183145':'Mürbteig (Backzutat), kein Gericht','4099200013312':'trockene Lasagneblätter (354 kcal = Trockenware)','4099200008196':'Suppenkonzentrat – Werte nicht verzehrfertig','4099200021966':'Suppenkonzentrat – 0 kcal unplausibel','4099200015729':'Instant-Trockensuppe 61 g – Werte trocken (328 kcal)','4099200016252':'keine Nährwerte, Name unspezifisch'}
for x in H:
  u=x['url']; e=u.split('/')[-1] if 'openfoodfacts' in u else None
  if e in notmeal: add(x['name'],u,'remove',reason=notmeal[e])
  if 'Mango Curry' in x['name']: add(x['name'],u,'remove',reason='BRUNCH Mango Curry = Brotaufstrich, kein Gericht')
  if 'Snackbox' in x['name'] or x['name'] in('Frittaten Suppeneinlage','Grießnockerl','Eiersalat','Mürbteig'): add(x['name'],u,'flag_side',field='category',new='Beilage/Snack',reason='kein Hauptgericht – aus Rankings nehmen')
  if e=='4099200135892': add(x['name'],u,'fix','kcal_100',x['kcal_100'],None,'36 kcal bei 23 g Protein unmöglich (>=92 kcal); OFF-Fehlwert -> null, rankable=false bis Etikett geprüft')
  if e=='4099200227733': add(x['name'],u,'fix','producer_id',x['producer_id'],None,'FSC-C010395 ist FSC-Verpackungszertifikat, kein Identitätskennzeichen (OFF emb_codes falsch)')
  if e=='4061459137125': add(x['name'],u,'flag','salt_100',None,None,'Salz fehlt')
  if e=='4061459137095': add(x['name'],u,'flag','dry',None,True,'3,1 g Salz/100 g unplausibel für verzehrfertig -> wohl Trockenprodukt; aus Ranking')
  if e=='4099200121574': add(x['name'],u,'fix','kcal_100/protein_100/salt_100',[x['kcal_100'],x['protein_100'],x['salt_100']],[99,4.7,2.8],'OFF aktuell 99 kcal / 4,7 g P / 2,8 g Salz')
  if x['name']=='Faschierte Laibchen mit Kartoffelpüree' and x['size_g']==430: add(x['name'],u,'fix','size_g',430,400,'Packung 400 g (OFF)')
  if x['name']=='XXL Lasagne' or x['name'].startswith('Gefüllte Gnocchi'): add(x['name'],u,'fix','size_g',None,'nachtragen','size_g fehlt -> €/kg und Protein/€ nicht berechenbar')
  if x['name']=='Pikante Knödel': add(x['name'],u,'flag','price_eur',2.39,None,'Preis aus Flugblatt (billiga.at, Aktion ab 09.10.2026) – als Aktionspreis kennzeichnen')
def key(n):
  n=n.lower(); n=re.sub(r'(bio|good choice|primana|cucina nobile|cucina|mamia|italienische|fertiggerichte?|pasta|\d+\s?k?g)','',n); return re.sub(r'[^a-zäöüß]','',n)
g=collections.defaultdict(list)
for x in H: g[key(x['name'])].append(x)
for k,v in g.items():
  if len(v)>1:
    keep=max(v,key=lambda x:((x['price_date'] or '')>'2026',x['kcal_100'] is not None,x['price_eur'] is not None,x['brand'] is not None))
    for x in v:
      if x is not keep: add(x['name'],x['url'],'remove_duplicate',reason=f"Duplikat von '{keep['name']}' ({keep['url'][:70]}); Preis/Nährwerte/Bild mergen")
for x in H:
  if not x['brand']: add(x['name'],x['url'],'fix','brand',None,x['name'].split()[0].title(),'Marke fehlt')
  if x['price_date'] and x['price_date']<'2026': add(x['name'],x['url'],'flag','price_status','alt',None,f"Preis vom {x['price_date']} – veraltet")
  if x['price_eur'] is None and x['protein_100'] is not None: add(x['name'],x['url'],'flag','price_eur',None,None,'kein Preis (nur OFF) – nicht in Preis-Rankings')
missing=[{'name':'Good Choice Lasagne Bolognese 1000 g','ean':'4099200163659','producer_id':'AT 41586 EG','reason':'in hofer_goodchoice.json (150 kcal/6,8 g P), fehlt in scored.json; belegt Hochreiter-Zuordnung'},
 {'name':'Primana Gulaschsuppe','ean':'4099200121567','reason':'in hofer_goodchoice.json (83 kcal/5,3 g P), fehlt in scored.json -> Nährwerte in "PRIMANA Gulasch Suppe 400g" mergen'},
 {'name':'Good Choice Lasagne Bolognese 400 g','ean':'4099200053707','reason':'in hofer_goodchoice.json (170/5,6) – prüfen ob = CUCINA NOBILE Lasagne 400g (gleiche Werte)'}]
logos=[{'file':'analysis/logos/hofer.svg','status':'replaced','old':'Aldi_Süd_2017_logo.svg','new':'https://commons.wikimedia.org/wiki/File:Hofer_Logo_2017.svg','reason':'Aldi-Süd-Logo statt HOFER; logos.json aktualisiert'},
 {'file':'analysis/logos/knorr.png','status':'replaced','old':'Knorr_logo_old.png','new':'Commons Knorr_Logo_2020.svg als PNG 300px','reason':'veraltetes Logo; logos.json aktualisiert'},
 {'file':'analysis/logos/frosta.svg','status':'ok_minor','reason':'Konzern-Wortmarke "FRoSTA AG"'},
 {'file':'analysis/logos/gms-gourmet.png','status':'low_quality','reason':'nur Kochmützen-Favicon'},
 {'file':'analysis/logos/graninger.png','status':'low_quality','reason':'Favicon "G", 1 KB'},
 {'file':'analysis/logos/hochreiter.png','status':'low_quality','reason':'winziges Favicon'},
 {'file':'analysis/logos/karnerta.png','status':'low_quality','reason':'abgeschnitten ("RNER")'},
 {'file':'analysis/logos/wiesbauer.png, wiesbauer-gourmet.png','status':'low_quality','reason':'718-B-Favicon "W", beide identisch'},
 {'file':'analysis/logos/rewe-*.svg','status':'ok_generic','reason':'REWE-Group-Konzernlogo'},
 {'file':'restliche 22','status':'ok','reason':'rendern, richtige Marke'}]
prod=[{'code':'AT 92584 EG','issue':'unaufgelöst (company null)'},
 {'code':'AT 92556 EG','issue':'Wiesbauer Wurstspezialitäten: 0 Produkte – Profil ohne Gericht'},
 {'code':'AT 40559 EG','issue':'Greisinger: Mini Berner Würstel/Putenknacker sind Wurst, keine Fertiggerichte'},
 {'code':'AT 41586 EG','issue':'Hochreiter↔Good Choice Lasagne 1 kg durch OFF emb_codes belegt; ok'},
 {'code':'AT 62028 EG','issue':'Landena: "Curry Madras - Pure Beef" Marke/Kette unklar, prüfen; Rest konsistent'},
 {'code':'AT 30733 EG','issue':'GMS↔Good Choice Gelbes Gemüsecurry konsistent in scored.json'},
 {'code':'FSC-C010395','issue':'falsch als producer_id (Kasnudeln) – entfernen'},
 {'code':'DE NW-20108 EG / DE NW 41110 EG','issue':'Hofer Pastasalat Feta + Tortelloni Käse von deutschen Betrieben – plausibel, im UI als Herkunft DE zeigen'},
 {'code':'alle AT-Codes','issue':'Präfix↔Bundesland für alle 15 AT-Codes konsistent'}]
out={'date':'2026-10-12','hofer_products_checked':len(H),'product_fixes':fx,'missing_in_scored':missing,'logo_fixes':logos,'producer_issues':prod,
'country_check':'Alle 35 OFF-EANs unter HOFER haben countries_tags inkl. Austria und stores=Hofer -> keine reinen DE/CH-Artikel. Bilder: 50/50 laden.',
'price_check':'wokostswas Good Choice Pinzgauer Käsespätzle 380 g = 3,06 € am 12.10.2026 bestätigt'}
json.dump(out,open('qa/hofer_logos_fixes.json','w'),ensure_ascii=False,indent=1)
print(len(H),len(fx),collections.Counter(f['action'] for f in fx))
for f in fx:
  if f['action']=='remove_duplicate': print(' DUP',f['name'],'->',f['reason'][:60])
