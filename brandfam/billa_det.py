import json,re,urllib.request,concurrent.futures as cf
R=json.load(open('billa_raw.json'))
MEALCAT=re.compile(r'Menüschalen|Fertiggerichte gekühlt > Suppen|Fertiggerichte ungekühlt > (Suppen|Gerichte)|Tiefkühlgerichte > Tiefkühlgerichte|Pizza & Co > Pizza|Schnell & Rein Pflanzlich > Fertiggerichte')
DISH=re.compile(r'eintopf|gulasch|suppentopf|chili|lasagne|ravioli|risotto|curry|paella|bolognese|linsen|bohnen|tortellini|gnocchi|knödel mit|nudeln mit|reis mit|ragout|geschnetzel|bowl|pfanne|menü',re.I)
def J(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))
sel=[]
for sb,L in R.items():
    for x in L:
        cat=' > '.join(c['name'] for c in (x.get('parentCategories') or [[]])[0][:3])
        if MEALCAT.search(cat) or ('Konserven' in cat and DISH.search(x['name'])): sel.append((sb,cat,x))
print(len(sel))
def nut(d):
    o={}
    try:
        for ni in d['additionalInformation'][0]['foodInformation']['nutritionInfos']:
            for n in ni['nutrients']:
                nm=n['name'].lower();v=n['value'];u=n['unit']['symbol']
                if nm.startswith('energie') and u=='kcal':o['kcal_100']=v
                elif nm=='eiweiß':o['protein_100']=v
                elif nm=='fett':o['fat_100']=v
                elif 'gesättigt' in nm:o['satfat_100']=v
                elif nm=='kohlenhydrate':o['carbs_100']=v
                elif 'zucker' in nm:o['sugar_100']=v
                elif 'ballast' in nm:o['fiber_100']=v
                elif nm=='salz':o['salt_100']=v
            break
    except Exception:pass
    return o
def f(t):
    sb,cat,x=t
    try:d=J("https://shop.billa.at/api/product-discovery/products/"+x['sku'])
    except Exception:d=x
    pi=((d.get('additionalInformation') or [{}])[0] or {}).get('productInformation') or {}
    pr=(x.get('price') or {}).get('regular') or {}
    sz=None
    for m in pi.get('measurements') or []:
        if m['type']=='Nettogehalt': sz=m['value']*(1000 if m['unit'] in('Kilogramm','Liter') else 1)
    p={'name':x['name'],'brand':x['brand']['name'],'store':'BILLA','price_eur':(pr.get('value') or 0)/100 or None,'size_g':sz,
       'price_per_kg':(pr.get('perStandardizedQuantity') or 0)/100 or None,'url':'https://shop.billa.at/produkte/'+x['slug'],
       'image_url':(x.get('images') or [None])[0],'manufacturer':pi.get('manufacturersAddress'),'producer_id':pi.get('mandatoryIndicator'),
       'category':cat,'price_source':'shop.billa.at API','price_date':'2026-10-13','nut_source':'shop.billa.at API',
       'brand_family':'BILLA','sub_brand':sb,'source_url':'https://shop.billa.at/api/product-discovery/products/'+x['sku']}
    p.update(nut(d))
    if p.get('protein_100') and sz: p['protein_pack']=round(p['protein_100']*sz/100,1)
    if p.get('kcal_100') and sz: p['kcal_pack']=round(p['kcal_100']*sz/100)
    return p
with cf.ThreadPoolExecutor(6) as ex: out=list(ex.map(f,sel))
json.dump(out,open('billa_family.json','w'),ensure_ascii=False,indent=1)
import collections;print(collections.Counter(p['sub_brand'] for p in out), sum(1 for p in out if p.get('protein_100') is not None))
