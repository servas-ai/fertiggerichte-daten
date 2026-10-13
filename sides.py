import json,urllib.request,urllib.parse,concurrent.futures as cf,re
H={'User-Agent':'Mozilla/5.0'}
CATS={'gemuese-15482':'veg','salate-verpackt-13763':'salad','reis-15086':'side','knoedel-und-suppeneinlagen-15493':'side','knoedel-und-pueree-15092':'side'}
res={}
for c,role in CATS.items():
    d=json.load(urllib.request.urlopen(urllib.request.Request(f"https://shop.billa.at/api/product-discovery/categories/{c}/products?page=0&pageSize=100",headers=H),timeout=30))
    for r in d.get('results',[]):
        nm=r['name'].lower()
        if role=='side' and re.search(r'erdbeer|marillen|topfen|nougat|zwetschk|mohn|grieß|fix|nockerl|frittaten|backerbsen|schöberl',nm): continue
        if role=='salad' and re.search(r'beeren|sprossen|kräuter',nm): continue
        r['_term']=role; res.setdefault(r['sku'],r)
print(len(res))
def g(s):
    try: return s,json.load(urllib.request.urlopen(urllib.request.Request("https://shop.billa.at/api/product-discovery/products/"+s,headers=H),timeout=30))
    except: return s,None
with cf.ThreadPoolExecutor(8) as ex: det=dict(ex.map(g,list(res)))
NM={'ENER-':'kcal','PRO-':'protein','FAT':'fat','FASAT':'satfat','CHOAVL':'carbs','SUGAR-':'sugar','FIBTG':'fiber','SALTEQ':'salt'}
out=[]
for s,p in det.items():
    if not p: continue
    ai=(p.get('additionalInformation') or [{}])[-1]; fi=ai.get('foodInformation',{}) or {}; pi=ai.get('productInformation',{}) or {}
    n={}
    for ni in fi.get('nutritionInfos',[]):
        if ni.get('relationValue')!=100: continue
        if n and ni.get('preparationGrade')!='Unzubereitet': continue
        for x in ni.get('nutrients',[]):
            k=NM.get(x['nutrientId'])
            if k and not(k=='kcal' and x['unit']['symbol']!='kcal'): n[k]=x['value']
    if 'kcal' not in n: continue
    size=None
    for m in pi.get('measurements',[]):
        if m['type']=='Nettogehalt' and m['unit'] in('Gramm','Milliliter'): size=m['value']
    pr=p['price']['regular']
    t=res[s]['_term']; nm=p['name']
    role=t;_='veg' if re.search(r'gemüse|brokkoli|fisolen|erbsen|spinat|karfiol|kohlsprossen|wok|rotkraut|sauerkraut|bohnen|kichererbsen|linsen',t) else 'salad' if 'salat' in t else 'side'
    ids=sorted(set(re.findall(r'\bAT[ -]?\d{4,5}[ -]?(?:EG|EWG|EC)\b',json.dumps(p))))
    out.append(dict(name=nm,brand=(p.get('brand') or {}).get('name'),store='BILLA',price_eur=pr['value']/100,size_g=size,
      price_per_kg=round(pr['perStandardizedQuantity']/100,2) if pr.get('perStandardizedQuantity') else None,
      url='https://shop.billa.at/produkte/'+p['slug'],image_url=(p.get('images') or [None])[0],
      kcal_100=n.get('kcal'),protein_100=n.get('protein'),fat_100=n.get('fat'),satfat_100=n.get('satfat'),carbs_100=n.get('carbs'),sugar_100=n.get('sugar'),fiber_100=n.get('fiber'),salt_100=n.get('salt'),
      protein_pack=round(n['protein']*size/100,1) if size and n.get('protein') is not None else None,kcal_pack=round(n['kcal']*size/100) if size else None,
      manufacturer=pi.get('manufacturersAddress'),producer_id=', '.join(ids) or None,bio='bio' in nm.lower(),veg=None,category=p.get('category'),
      side_role=role,portion_g={'veg':200,'salad':100}.get(role, 75 if re.search(r'reis',nm.lower()) else 150),search_term=t,price_source='shop.billa.at live 2026-10-12',
      instantpot={'veg':'TK-Gemüse: Steam High 0–2 Min. (Richtwert), Quick Release','salad':'kalt servieren','side':('Reis: Pressure Cook High 4–6 Min. (Basmati 1:1,25 Wasser), 10 Min. Natural Release (Richtwert)' if 'reis' in nm.lower() else 'Knödel/Püree: Steam High 6–10 Min. (Richtwert)')}[role]))
json.dump(out,open('sides_billa.json','w'),ensure_ascii=False,indent=1)
import collections;print(len(out),collections.Counter(o['side_role'] for o in out))
for o in out[:15]: print(o['name'],o['category'],o['price_eur'],o['size_g'],o['kcal_100'],o['protein_100'])
