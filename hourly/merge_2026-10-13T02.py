import json,re,sys,os
sys.path.insert(0,'/workspace/food-connectors')
os.chdir('/workspace/fertig')
KEYS=list(json.load(open('more_meals_norm.json'))[0].keys())
C={str(p['source_id']):p for p in json.load(open('hourly/cand_gurkerl_cat_2026-10-13T02.json'))}
# curated: true heat-up meals only (id -> (category, packaging))
K='Kühlregal (Menüschale/frisch)';T='TK (Tiefkühl)';SV='Sous-vide (vakuum)';I='Trocken/Instant-Beutel'
SEL={
 '30504':('Komplettmahlzeit',K),'44184':('Komplettmahlzeit',K),'44173':('Komplettmahlzeit',K),'28395':('Komplettmahlzeit',K),'49086':('Komplettmahlzeit',K),
 '3654':('Komplettmahlzeit',SV),'44191':('Komplettmahlzeit',K),'39398':('Komplettmahlzeit',K),'28455':('Suppe/Eintopf',K),'28454':('Komplettmahlzeit',K),
 '28453':('Suppe/Eintopf',K),'46401':('Komplettmahlzeit',SV),'46400':('Komplettmahlzeit',SV),'44172':('Komplettmahlzeit',K),'40395':('Suppe/Eintopf',K),
 '40393':('Suppe/Eintopf',K),'44205':('Komplettmahlzeit',K),'44201':('Komplettmahlzeit',K),'38207':('Komplettmahlzeit',K),'38208':('Komplettmahlzeit',K),
 '38209':('Komplettmahlzeit',K),'32449':('Komplettmahlzeit',K),'32448':('Komplettmahlzeit',K),'32446':('Komplettmahlzeit',K),'39393':('Komplettmahlzeit',K),
 '47858':('Komplettmahlzeit',K),'37904':('Komplettmahlzeit',K),'4109':('Suppe/Eintopf',K),'13780':('Suppe/Eintopf',K),'13777':('Suppe/Eintopf',K),
 '13779':('Suppe/Eintopf',K),'42677':('Suppe/Eintopf',K),'41894':('Suppe/Eintopf',K),'6102':('Komplettmahlzeit',T),'49063':('Komplettmahlzeit',T),
 '6081':('Nachspeise',T),'36238':('Nachspeise',T),'5899':('Nachspeise',T),'5900':('Nachspeise',T),'5897':('Nachspeise',T),'13456':('Nachspeise',T),
 '13442':('Nachspeise',T),'49059':('Nachspeise',T),'10669':('Suppe/Eintopf',None),'10723':('Komplettmahlzeit','Dose'),'41437':('Komplettmahlzeit',I),
 '38498':('Komplettmahlzeit',None),'30601':('Komplettmahlzeit',I),'5096':('Komplettmahlzeit',I),'40534':('Komplettmahlzeit',I),'40544':('Komplettmahlzeit',I),
 '44153':('Komplettmahlzeit',I),'3454':('Nachspeise',None),'3455':('Nachspeise',None),'6904':('Suppe/Eintopf',None),'39867':('Suppe/Eintopf',None),
 '6905':('Suppe/Eintopf',None),'38809':('Suppe/Eintopf',None),'6908':('Suppe/Eintopf',None),'46174':('Komplettmahlzeit',None),'46180':('Komplettmahlzeit',None),
 '39930':('Komplettmahlzeit',I),'30581':('Komplettmahlzeit',I),
}
D='2026-10-13'
def rnd(v): return None if v is None else round(float(v),2)
mm=json.load(open('more_meals.json'));mn=json.load(open('more_meals_norm.json'))
have={(x['name'],x['store'],x.get('size_g')) for x in mm}; haveE={str(x.get('ean')) for x in mm if x.get('ean')}
new=[]
for sid,(cat,pack) in SEL.items():
  p=C[sid];n=p.get('nutrition_100g') or {}
  r={k:None for k in KEYS};r['ean']=None
  r.update(name=p['name'],brand=p.get('brand'),store='Gurkerl.at',price_eur=p['price_eur'],size_g=p['size_g'],
    price_per_kg=round(p['price_eur']/p['size_g']*1000,2) if p.get('size_g') else None,url=p['source_url'],image_url=p['image_url'],
    **{k+'_100':rnd(n.get(k)) for k in ['kcal','protein','fat','satfat','carbs','sugar','fiber','salt']},
    manufacturer=p.get('producer'),producer_id=p.get('producer_id'),origin=p.get('origin'),
    bio=bool(re.search(r'\bBIO\b',p['name'])),veg=True if re.search(r'vegan',p['name'],re.I) else None,
    category=cat,packaging=pack,fertigstufe='Eintopf/Suppe' if cat=='Suppe/Eintopf' else 'Komplettmahlzeit',
    price_source=f'food-connectors/gurkerl {D} (category API, inStock)',price_date=D,
    nut_source='Gurkerl.at API (composition)' if n else None,source_url=p['source_url'],ean=p.get('ean'))
  g=r['size_g']
  if g and r['protein_100'] is not None: r['protein_pack']=round(r['protein_100']*g/100,1)
  if g and r['kcal_100'] is not None: r['kcal_pack']=round(r['kcal_100']*g/100)
  r['protein_per_eur']=round(r['protein_pack']/r['price_eur'],1) if r.get('protein_pack') and r.get('price_eur') else None
  if (r['name'],r['store'],r['size_g']) in have or (r['ean'] and r['ean'] in haveE): continue
  new.append(r)
json.dump(new,open('hourly/added_2026-10-13T02.json','w'),ensure_ascii=False,indent=1)
print('candidates',len(new))
