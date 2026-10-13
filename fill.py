import json,re,time,urllib.request,urllib.parse
L=json.load(open('spar.json'))
bad=re.compile(r'Teig|Nudeln$|Spaghetti$|Penne|Fusilli|Suppenwürze|Würfel|Rindsuppe klar|Brühe|Fond|Croutons|Einlage|Knödel$|Gnocchi$|Basis|Fix|Sauce$|Soße',re.I)
L=[x for x in L if not bad.search(x['name'])]
pri=lambda x:(0 if re.search('Fertiggericht|Hausmannskost|Eintopf|Suppe',x['prep'] or '') else 1, 0 if x['brand'].upper().startswith(('SPAR','S-B','DESPAR')) else 1)
L.sort(key=pri); L=L[:100]
def g(u):
  r=urllib.request.Request(u,headers={'User-Agent':'GrokBot-research/1.0'});return json.load(urllib.request.urlopen(r,timeout=30))
def words(s):return set(w for w in re.findall(r'\w{4,}',s.lower()))
for x in L:
  q=f"{x['brand']} {x['name']}"
  try:d=g('https://world.openfoodfacts.org/cgi/search.pl?'+urllib.parse.urlencode(dict(search_terms=q,search_simple=1,action='process',json=1,page_size=5,fields='code,product_name,brands,nutriments,nutriscore_grade,emb_codes,manufacturing_places,origins,countries')))
  except Exception as e: print('err',e);time.sleep(10);continue
  best=None
  for p in d.get('products',[]):
    pb=(p.get('brands') or '').lower()
    if not any(w in pb for w in x['brand'].lower().replace('*',' ').split() if len(w)>2): continue
    ov=len(words(x['name'])&words(p.get('product_name') or ''))
    if ov>=max(1,len(words(x['name']))//2) and (not best or ov>best[0]): best=(ov,p)
  if best:
    p=best[1];n=p.get('nutriments',{})
    for k,f in [('kcal_100','energy-kcal_100g'),('protein_100','proteins_100g'),('fat_100','fat_100g'),('satfat_100','saturated-fat_100g'),('carbs_100','carbohydrates_100g'),('sugar_100','sugars_100g'),('fiber_100','fiber_100g'),('salt_100','salt_100g')]:
      x[k]=n.get(f)
    if x['size_g']:
      if x['protein_100'] is not None:x['protein_pack']=round(x['protein_100']*x['size_g']/100,1)
      if x['kcal_100'] is not None:x['kcal_pack']=round(x['kcal_100']*x['size_g']/100)
    x['nutriscore']=(p.get('nutriscore_grade') or '').upper() if p.get('nutriscore_grade') in list('abcde') else None
    x['producer_id']=p.get('emb_codes') or None;x['origin']=p.get('origins') or None
    x['manufacturer']=p.get('manufacturing_places') or None;x['off_match']=f"{p.get('code')} {p.get('product_name')}"
    print('OK',x['name'],'->',x['off_match'])
  time.sleep(6.5)
json.dump(L,open('spar.json','w'),ensure_ascii=False,indent=1)
