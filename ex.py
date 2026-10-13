import json,re,urllib.request,urllib.parse,time,concurrent.futures as cf
C=json.load(open('cand.json'));det=json.load(open('det.json'));det.update(json.load(open('det2.json')))
NM={'ENER-':'kcal','PRO-':'protein','FAT':'fat','FASAT':'satfat','CHOAVL':'carbs','SUGAR-':'sugar','FIBTG':'fiber','SALTEQ':'salt'}
NK=['kcal','protein','fat','satfat','carbs','sugar','fiber','salt']
KEYS=list(json.load(open('billa.json'))[0].keys())
def billa(c,p):
  txt=json.dumps(p,ensure_ascii=False)
  ai=(p.get('additionalInformation') or [{}])[-1]
  fi=ai.get('foodInformation',{}) or {}; pi=ai.get('productInformation',{}) or {}
  n={}
  for ni in fi.get('nutritionInfos',[]):
    if ni.get('relationValue')!=100: continue
    if n and ni.get('preparationGrade')!='Unzubereitet': continue
    for x in ni.get('nutrients',[]):
      k=NM.get(x['nutrientId'])
      if not k or (k=='kcal' and x['unit']['symbol']!='kcal'): continue
      n[k]=x['value']
  ids=sorted(set(re.findall(r'\bAT[ -]?\d{4,5}[ -]?(?:EG|EWG|EC)\b|\b(?:DE|IT|HU|PL|CZ|SK|SI)[ -][A-Z0-9-]{2,10}[ -](?:EG|EWG|EC)\b',txt)))
  b=p.get('badges') or []
  return dict(brand=(p.get('brand') or {}).get('name'),url='https://shop.billa.at/produkte/'+p['slug'],image_url=(p.get('images') or [None])[0],
    manufacturer=pi.get('manufacturersAddress') or (pi.get('contactDetails') or {}).get('name') or None,producer_id=', '.join(ids) or None,
    origin=p.get('countryOfOrigin') or None,veg='vegan' if 'pp-vegan' in b else 'vegetarisch' if 'pp-veget' in b else None,
    billa_category=p.get('category'),storage=p.get('storageType'),nut_source='BILLA shop API' if n else None,**{k+'_100':n.get(k) for k in NK})
W=lambda s:set(w for w in re.findall(r'[a-zäöüß]{3,}',(s or '').lower()) if w not in('mit','und','der','die','das','bio','von','nach','art','spar','billa'))
def off(c):
  q=c['name']
  for i in range(4):
    try:
      u='https://search.openfoodfacts.org/search?'+urllib.parse.urlencode(dict(q=q,page_size=10,fields='code,product_name,product_name_de,brands,nutriments,emb_codes,image_front_url,origins,nutriscore_grade'))
      d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'GrokBot-research/1.0'}),timeout=40));break
    except Exception: time.sleep(5*(i+1))
  else: return None
  nw=W(c['name']); first=c['name'].split()[0].lower()
  best=None
  for h in d.get('hits',[]):
    br=' '.join(h.get('brands') or []).lower() if isinstance(h.get('brands'),list) else (h.get('brands') or '').lower()
    pn=h.get('product_name_de') or h.get('product_name') or ''
    if first not in br and first not in pn.lower(): continue
    pw=W(pn)-W(br)
    if not pw: continue
    nw2=nw-W(br)
    sc=len(nw2&pw)/max(len(nw2|pw),1)
    if sc>=0.6 and (not best or sc>best[0]): best=(sc,h,pn)
  if not best: return None
  h=best[1];n=h.get('nutriments') or {}
  F={'kcal':'energy-kcal_100g','protein':'proteins_100g','fat':'fat_100g','satfat':'saturated-fat_100g','carbs':'carbohydrates_100g','sugar':'sugars_100g','fiber':'fiber_100g','salt':'salt_100g'}
  r={k+'_100':n.get(v) for k,v in F.items()}
  if all(v is None for v in r.values()): r={}
  em=h.get('emb_codes');em=', '.join(em) if isinstance(em,list) else em
  return dict(r,off_image=h.get('image_front_url'),off_emb=em or None,off_match=f"{h['code']} {best[2]} ({best[0]:.2f})",off_ns=(h.get('nutriscore_grade') or '').upper() if h.get('nutriscore_grade') in list('abcde') else None,off_origin=h.get('origins') or None)
def cat(name,bc,pk):
  n=name.lower()
  if re.search(r'reis|knödel|kartoffel|püree|rösti|spinat|gemüse|brokkoli|erbsen|fisolen|nockerl|spätzle|gnocchi|pommes|kroketten|polenta|couscous',n) and not re.search(r'suppe|gericht|mit (rind|hendl|huhn|schwein|speck|fleisch)|gulasch|curry|risotto|pfanne mit',n): return 'Beilage/Gemüse'
  if re.search(r'suppe|eintopf',n): return 'Suppe/Eintopf'
  if pk=='Tiefkühl': return 'Tiefkühlgericht'
  return bc or 'Fertiggericht'
def pack(name,bc,st):
  n=name.lower();b=(bc or '').lower();s=(st or '').lower()
  if 'sous' in n: return 'Sous-vide'
  if 'tief' in s or 'tk ' in n+' ' or 'tiefkühl' in b or 'gefror' in s: return 'Tiefkühl'
  if 'dose' in b or re.search(r'\bdose\b|konserve',n): return 'Dose'
  if re.search(r'kochbeutel|beutel|instant|5 minuten|minuten terrine|cup\b|express',n) or b in('beutel','asien'): return 'Instant/Beutel'
  if 'kühl' in s or 'menüschal' in b or 'gekühlt' in b: return 'Kühlschale'
  return None
def work(c):
  r={k:None for k in KEYS}
  r.update(name=c['name'],store='BILLA' if c['store']=='billa' else 'SPAR',price_eur=c['price_eur'],price_per_kg=c.get('price_per_kg'),bio=bool(c.get('bio')),
    size_g=c['qty'] if c.get('unit') in('g','ml') else None,price_source=c['price_source'],price_date=c.get('last_price_change'))
  ex={}
  if c['store']=='billa' and det.get(c['id']):
    ex=billa(c,det[c['id']])
    for k in KEYS:
      if k in ex and ex[k] is not None: r[k]=ex[k]
    r['category']=ex['billa_category']
  else:
    r['url']=f"https://www.interspar.at/p/{c['id']}" if c['store']=='spar' and not c['id'].startswith('2020') else None
  r['nut_source']=ex.get('nut_source')
  if r['protein_100'] is None and r['kcal_100'] is None:
    o=off(c)
    if o:
      for k in [x+'_100' for x in NK]: r[k]=o.get(k)
      if any(o.get(x+'_100') is not None for x in NK): r['nut_source']='Open Food Facts '+o['off_match']
      r['image_url']=r['image_url'] or o['off_image']; r['producer_id']=r['producer_id'] or o['off_emb']
      r['nutriscore']=o['off_ns'];r['origin']=r['origin'] or o['off_origin'];r['off_match']=o['off_match']
  if not r['brand']: r['brand']=None
  if r['size_g']:
    if r['protein_100'] is not None:r['protein_pack']=round(r['protein_100']*r['size_g']/100,1)
    if r['kcal_100'] is not None:r['kcal_pack']=round(r['kcal_100']*r['size_g']/100,1)
  r['packaging']=pack(c['name'],r['category'],ex.get('storage'))
  r['category']=cat(c['name'],r['category'],r['packaging'])
  return r
with cf.ThreadPoolExecutor(8) as e: out=list(e.map(work,C))
json.dump(out,open('expand.json','w'),ensure_ascii=False,indent=1)
n=len(out);print(n)
for k in ['kcal_100','protein_100','fat_100','satfat_100','carbs_100','sugar_100','fiber_100','salt_100','image_url','url','producer_id','manufacturer','packaging','brand']:
  print(k,sum(1 for o in out if o.get(k) is not None),round(100*sum(1 for o in out if o.get(k) is not None)/n))
import collections;print(collections.Counter(o['category'] for o in out).most_common(12));print(collections.Counter((o['store'],o['protein_100'] is not None) for o in out))
