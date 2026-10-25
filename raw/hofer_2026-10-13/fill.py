import json,re,unicodedata,datetime
def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',(s or '').lower()).encode('ascii','ignore').decode()).strip()
app=json.load(open('/workspace/fertig-app/public/data.json'))['rows'];H=[r for r in app if r['store']=='Hofer']
HA={norm(r['name']):r for r in json.load(open('rows.json'))}
OFF=json.load(open('off_hofer_all.json'));OE={p['code']:p for p in OFF};ON={}
for p in OFF: ON.setdefault(norm(p.get('product_name_de') or p.get('product_name')),p)
HP={}
for x in json.load(open('/home/box/.cache/food-connectors/heisse-preise.json')):
  if x.get('store')=='hofer': HP.setdefault(norm(x.get('name')),x)
def hp_find(name,brand):
  n=norm(name)
  c=[(k,v) for k,v in HP.items() if n and n in k and (not brand or norm(brand).split()[0] in k)]
  c.sort(key=lambda kv:len(kv[0]));return c[0][1] if c else None
cut=(datetime.date(2026,10,13)-datetime.timedelta(days=365)).isoformat()
fill=[];stat=dict(app_rows=len(H),hofer_at=0,off=0,heisse=0)
for a in H:
  f=dict(app_id=a['id'],app_name=a['name'],had_price=a.get('price') is not None,had_kcal=a.get('kcal') is not None,had_size=a.get('size') is not None)
  m=HA.get(norm(a['name']))
  if m:
    stat['hofer_at']+=1
    f.update(price_eur=m['price_eur'],size_g=m['size_g'],price_per_kg=m['price_per_kg'],ingredients=m['ingredients'],allergens=m['allergens'],image_url=m['image_url'],hofer_url=m['url'],price_source='hofer.at live 2026-10-13',price_date='2026-10-13')
  e=re.search(r'product/(\d{8,14})',str(a.get('url')));o=OE.get(e.group(1)) if e else None
  o=o or ON.get(norm(a['name']))
  if o:
    stat['off']+=1;nu=o.get('nutriments') or {}
    for k,ok in (('kcal_100','energy-kcal_100g'),('protein_100','proteins_100g'),('fat_100','fat_100g'),('satfat_100','saturated-fat_100g'),('carbs_100','carbohydrates_100g'),('sugar_100','sugars_100g'),('fiber_100','fiber_100g'),('salt_100','salt_100g')):
      if nu.get(ok) is not None: f[k]=nu[ok]
    if o.get('nutriscore_grade') in list('abcde'): f['nutriscore']=o['nutriscore_grade'].upper()
    if o.get('nova_group'): f['nova']=o['nova_group']
    f.setdefault('ingredients',o.get('ingredients_text_de') or o.get('ingredients_text'))
    if o.get('product_quantity') and not f.get('size_g'):
      try: f['size_g']=float(o['product_quantity'])
      except: pass
    f['ean']=o['code'];f.setdefault('image_url',o.get('image_front_url'))
  if not f.get('price_eur'):
    x=hp_find(a['name'],a.get('brand'))
    asz=a.get('size')
    if x and asz and x.get('quantity') and x.get('unit') in('g','ml') and abs(x['quantity']-asz)/asz>0.1: x=None
    if x and x.get('price'):
      stat['heisse']+=1;pd=(x.get('priceHistory') or [{}])[0].get('date')
      f.update(price_eur=x['price'],price_date=pd,price_old=bool(pd and pd<cut),price_source=f"heisse-preise.io Hofer {pd}"+(' Altpreis >12 Monate' if pd and pd<cut else ''))
      if not f.get('size_g') and x.get('unit') in('g','ml') and x.get('quantity'): f['size_g']=x['quantity']
  if f.get('price_eur') and f.get('size_g') and not f.get('price_per_kg'): f['price_per_kg']=round(f['price_eur']/f['size_g']*1000,2)
  fill.append(f)
json.dump(fill,open('/workspace/fertig/hofer_fill_2026-10-13.json','w'),ensure_ascii=False,indent=1)
after=lambda k,ak:sum(1 for a,f in zip(H,fill) if a.get(ak) is not None or f.get(k) is not None)
stat.update(price_after=after('price_eur','price'),kcal_after=after('kcal_100','kcal'),size_after=after('size_g','size'),
 price_before=sum(a.get('price') is not None for a in H),kcal_before=sum(a.get('kcal') is not None for a in H),size_before=sum(a.get('size') is not None for a in H),
 old_prices=sum(1 for f in fill if f.get('price_old')))
print(stat);json.dump(stat,open('fill_stats.json','w'))
