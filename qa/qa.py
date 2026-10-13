import json,re,collections
src=json.load(open('billa_src.json'));img=json.load(open('billa_img.json'))
NM={'ENER-':'kcal','PRO-':'protein','FAT':'fat','FASAT':'satfat','CHOAVL':'carbs','SUGAR-':'sugar','FIBTG':'fiber','SALTEQ':'salt'}
KEYS=['kcal','protein','fat','satfat','carbs','sugar','fiber','salt']
DRYCAT={'Beutel','Asien','Suppengewürze','Rundkorn','Reis & Pasta'}
NOTMEAL={'Süßes & Desserts','Suppengewürze','Aufstriche','Kuchen, Muffins & Co verpackt','Eis am Stiel & Stanizl','Fruchtjoghurt','Eis-Snacks','Party & Geschenke','Rundkorn','Gartengemüse','Gemüse'}
def nut(p):
  ais=sorted([a for a in p.get('additionalInformation') or [] if a.get('validFrom','')<='2026-10-12'] or (p.get('additionalInformation') or []),key=lambda a:a.get('validFrom',''))
  for ai in reversed(ais):
    fi=ai.get('foodInformation') or {}; out={}
    for ni in fi.get('nutritionInfos',[]):
      if ni.get('relationValue')!=100: continue
      d={}
      for x in ni.get('nutrients',[]):
        k=NM.get(x['nutrientId'])
        if k and not(k=='kcal' and x['unit']['symbol']!='kcal'): d[k]=x['value']
      if d: out.setdefault(ni.get('preparationGrade'),d)
    if out: return out,ai
  return {},(ais[-1] if ais else {})
def size(p,ai):
  for m in (ai.get('productInformation') or {}).get('measurements',[]):
    if m['type']=='Nettogehalt' and m['unit'] in('Gramm','Milliliter'): return m['value']
  try:
    a=float(p['amount']); return a*1000 if p['volumeLabelShort'] in('kg','l') else a if p['volumeLabelShort'] in('g','ml') else None
  except: return None
def plaus(n,dry):
  r=[]
  if n.get('kcal') and None not in (n.get('carbs'),n.get('protein'),n.get('fat')):
    calc=4*n['carbs']+4*n['protein']+9*n['fat']+2*(n.get('fiber') or 0)
    if abs(calc-n['kcal'])>max(0.15*n['kcal'],10): r.append(f"kcal {n['kcal']} vs Makro-Rechnung {calc:.0f}")
  if (n.get('protein') or 0)>40 and not dry: r.append('Protein>40 g/100g bei nicht-trockenem Produkt')
  if (n.get('salt') or 0)>=5: r.append('Salz>=5 g/100g')
  if (n.get('satfat') or 0)>(n.get('fat') or 1e9): r.append('ges. Fett > Fett')
  if (n.get('sugar') or 0)>(n.get('carbs') or 1e9): r.append('Zucker > KH')
  return r
items=[(f,x) for f in ['scored.json','expand.json'] for x in json.load(open('../'+f)) if x.get('store')=='BILLA']
fixes=[];flags=[];seen=set();stats=collections.Counter()
def fx(u,fld,o,n,why,f):
  if isinstance(o,float) and isinstance(n,(int,float)) and abs(o-n)<0.051: return
  if o==n: return
  fixes.append(dict(id=u,file=f,field=fld,old=o,new=n,reason=why)); stats[fld]+=1
for f,x in items:
  u=x.get('url')
  if not u:
    key=(f,x['name'])
    if key in seen: continue
    seen.add(key); flags.append(dict(id=x['name'],name=x['name'],issue='keine BILLA-Shop-URL – nicht verifizierbar (nur heisse-preise.io)'))
    fx(x['name'],'is_meal',x.get('is_meal'),False,'süße Knödel/Rohreis – kein herzhaftes Fertiggericht',f); continue
  p=src[u];key=(f,u)
  if key in seen: continue
  seen.add(key)
  name=p['name'];brand=(p.get('brand') or {}).get('name')
  fx(u,'name',x['name'],name,'Name laut BILLA-Shop-API',f)
  if brand: fx(u,'brand',x['brand'],brand,'Marke laut BILLA-Shop-API',f)
  pr=p['price']['regular'];price=pr['value']/100
  if x.get('price_eur')!=price: fx(u,'price_eur',x.get('price_eur'),price,'Regalpreis laut BILLA-Shop-API 2026-10-12 (vorher: %s)'%(x.get('price_source') or '?'),f)
  if x.get('price_date') and x.get('price_date')<'2026-10-12': fx(u,'price_date',x['price_date'],'2026-10-12','Preis live verifiziert',f); fx(u,'price_status',x.get('price_status'),'aktuell','Preis live verifiziert',f)
  if p.get('inPromotion'): flags.append(dict(id=u,name=name,issue='aktuell in Aktion; Regalpreis verwendet'))
  ppk=pr.get('perStandardizedQuantity'); ppk=ppk/100 if ppk else None
  if ppk: fx(u,'price_per_kg',x.get('price_per_kg'),ppk,'Grundpreis laut API',f)
  ns,ai=nut(p); sz=size(p,ai)
  bu=p['price'].get('baseUnitShort')
  if ppk and bu in('kg','l'):
    implied=price/ppk*1000; cands=[c for c in [sz] if c]
    try:
      a=float(p['amount']); cands.append(a*1000 if p['volumeLabelShort'] in('kg','l') else a if p['volumeLabelShort'] in('g','ml') else None)
    except: pass
    cands=[c for c in cands if c]
    if cands:
      best=min(cands,key=lambda c:abs(c-implied))
      if sz and best and (best/sz>5 or sz/best>5): flags.append(dict(id=u,name=name,issue=f'API-Daten inkonsistent: Nettogehalt {sz} g vs. Menge {best} (Grundpreis basiert vermutlich auf Tippfehler) – Nettogehalt behalten'))
      else: sz=best
    if sz and abs(sz-implied)>0.06*implied: flags.append(dict(id=u,name=name,issue=f'Packungsgröße {sz} passt nicht zum Grundpreis ({price}€ / {ppk}€/{bu}, impliziert {implied:.0f})'))
  if sz: fx(u,'size_g',x.get('size_g'),sz,'Nettogehalt laut API',f)
  sz=sz or x.get('size_g')
  im=(p.get('images') or [None])[0]
  if im and x.get('image_url')!=im: fx(u,'image_url',x.get('image_url'),im,'Bild-URL laut API (aktuelles Produktbild)',f)
  elif not im: flags.append(dict(id=u,name=name,issue='kein Bild in API'))
  sku=u.rsplit('-',1)[1]
  if im and sku not in im.replace('-',''): flags.append(dict(id=u,name=name,issue='Bild-Dateiname enthält SKU nicht'))
  if x.get('image_url') in img and img[x['image_url']][0]!=200: flags.append(dict(id=u,name=name,issue='Bild lädt nicht'))
  cat=p['category']
  nl=name.lower()
  unz=ns.get('Unzubereitet');zub=ns.get('Zubereitet');other=ns.get('Nicht spezifiziert - Unbekannt, nicht anwendbar')
  dryish=cat in DRYCAT or any(w in nl for w in ['trocken','instant','cup','fix','pulver','suppenwürfel'])
  dry=bool(unz and zub and (unz.get('kcal') or 0)>200 and (zub.get('kcal') or 0)<0.6*(unz.get('kcal') or 1)) or (bool(unz) and (unz.get('kcal') or 0)>300 and dryish and not zub)
  c0=(unz or zub or other or {})
  if not dry and (c0.get('salt') or 0)>=5 and (unz and not zub) and (dryish or cat in('Beutel','Fertiggerichte Ungekühlt')):
    dry=True; flags.append(dict(id=u,name=name,issue='nur Trockenwerte (Pulver) in Quelle, keine Werte für zubereitetes Gericht – /100g nicht vergleichbar, aus Ranking nehmen'))
  if dry and zub: chosen,basis=zub,'zubereitet'
  else: chosen,basis=(unz or zub or other or {}),('unzubereitet' if unz else 'zubereitet' if zub else 'n/a')
  if x.get('dry') is not None or dry: fx(u,'dry',x.get('dry'),dry,'trocken/Pulver: Rohwerte weichen stark von Zubereitet ab' if dry else 'Werte gelten für verzehrfertiges Produkt',f)
  if chosen and chosen.get('kcal') and None not in (chosen.get('carbs'),chosen.get('protein'),chosen.get('fat')):
    calc=4*chosen['carbs']+4*chosen['protein']+9*chosen['fat']+2*(chosen.get('fiber') or 0)
    if abs(calc-chosen['kcal'])>0.15*chosen['kcal'] and abs(calc-chosen['kcal']/4.184)<=0.15*calc:
      chosen=dict(chosen,kcal=round(chosen['kcal']/4.184)); flags.append(dict(id=u,name=name,issue='Quelle hat kJ im kcal-Feld; umgerechnet'))
  if chosen:
    stats['has_nut']+=1
    for k in KEYS:
      if k in chosen: fx(u,k+'_100',x.get(k+'_100'),chosen[k],f'Nährwert/100g ({basis}) laut API',f)
    if sz and not dry:
      for k in ('protein','kcal'):
        if chosen.get(k) is not None: fx(u,k+'_pack',x.get(k+'_pack'),round(chosen[k]*sz/100,1),'= /100g × Packungsgröße',f)
    elif dry and x.get('protein_pack') and chosen.get('protein') is not None:
      flags.append(dict(id=u,name=name,issue='Trockenprodukt: protein_pack basiert auf Trockengewicht – Portionswert unsicher' ))
    for r in plaus(chosen,dry): flags.append(dict(id=u,name=name,issue='Nährwert unplausibel: '+r))
  else:
    stats['no_nut']+=1
    if x.get('protein_100') is not None: flags.append(dict(id=u,name=name,issue=f"keine Nährwerte in API; App-Wert aus {x.get('nut_source')} beibehalten"))
  if cat in NOTMEAL or re.search(r'\b(dessert|pudding|eis|dressing|gewürz|suppenwürze|risottoreis|suppengemüse|suppenterrine|suppenterinne|klare suppe|bouillon|goldaugen|suppentasse)\b|eisknödel|donut|\bfix\b|basis für|kräuterlinge|kraftbouillon|^knorr basis',nl):
    fx(u,'is_meal',x.get('is_meal'),False,f'kein Fertiggericht (Kategorie {cat})',f)
  if x.get('category') not in (cat,) and x.get('category') in NOTMEAL|DRYCAT|{'Menüschalen','Dose'}: fx(u,'category',x.get('category'),cat,'Kategorie laut API',f)
  if 'thunfisch' in nl and 'salat' not in nl and 'gericht' not in nl: flags.append(dict(id=u,name=name,issue='Thunfisch-Konserve – eher Zutat als Fertiggericht'))
# dedupe flags
fl=[];s=set()
for g in flags:
  k=(g['id'],g['issue'])
  if k not in s: s.add(k); fl.append(g)
json.dump(fixes,open('billa_fixes.json','w'),ensure_ascii=False,indent=1)
json.dump(fl,open('billa_flags.json','w'),ensure_ascii=False,indent=1)
print(len(items),len(fixes),len(fl),stats.most_common())
print(collections.Counter(g['issue'].split(':')[0][:50] for g in fl).most_common())
