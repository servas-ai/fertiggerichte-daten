import json
def v(x):
    if x in (None,'None','','null'): return None
    try: return float(x)
    except: return x
out=[]
for x in json.load(open('spar_browser_meals.json')):
    sz=v(x.get('pack_weight_g'));p=v(x.get('price_eur'));pr=v(x.get('protein_g'));k=v(x.get('kcal_per_100g'))
    cat=x.get('category_note') or ''
    out.append(dict(name=x['name'],brand=x.get('brand'),store='INTERSPAR',price_eur=p,size_g=sz,price_per_kg=round(p/sz*1000,2) if p and sz else None,url=x.get('product_url'),image_url=x.get('image_url'),
      kcal_100=k,protein_100=pr,fat_100=v(x.get('fat_g')),satfat_100=v(x.get('sat_fat_g')),carbs_100=v(x.get('carbs_g')),sugar_100=v(x.get('sugar_g')),fiber_100=v(x.get('fiber_g')),salt_100=v(x.get('salt_g')),
      protein_pack=round(pr*sz/100,1) if pr is not None and sz else None,kcal_pack=round(k*sz/100) if k is not None and sz else None,
      manufacturer=v(x.get('inverkehrsbringer')),producer_id=v(x.get('identitaetskennzeichen')),packaging=cat or None,
      price_source='INTERSPAR Webshop (Browser) 2026-10-12',price_date='2026-10-12',nut_source='INTERSPAR Webshop'))
json.dump(out,open('spar_browser_norm.json','w'),ensure_ascii=False,indent=1)
# more_meals: 'None' strings -> null
m=[{k:v(val) if isinstance(val,str) and k not in('name','brand','store','url','image_url','manufacturer','category','price_source','price_date','nut_source','packaging','source_url','fertigstufe','producer_id','origin','prep','instantpot','nutriscore') else (None if val=='None' else val) for k,val in x.items()} for x in json.load(open('more_meals.json'))]
for x in m: x['bio']=x.get('bio') in (True,'True')
json.dump(m,open('more_meals_norm.json','w'),ensure_ascii=False,indent=1)
print(len(out),len(m))
