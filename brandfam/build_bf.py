import json,re,os,urllib.parse
B=json.load(open('billa_family.json'))
H=json.load(open('hp_family.json'))
O=json.load(open('off_family.json')) if os.path.exists('off_family.json') else []
R=json.load(open('hofer_raw.json'))
out=[]
for p in B: out.append(p)
def num(s):
    m=re.search(r'([\d.,]+)\s*(kg|g|ml|l)\b',s or '',re.I)
    if not m:return None
    v=float(m.group(1).replace(',','.'));u=m.group(2).lower()
    return v*1000 if u in('kg','l') else v
for x in H:
    if x['store']=='hofer' and (x.get('last') or '')<'2025-01-01': continue
    sz=x['qty'] if x.get('unit') in('g','ml') else (x['qty']*1000 if x.get('unit') in('kg','l') and x.get('qty') else None)
    st='HOFER' if x['store']=='hofer' else 'SPAR'
    q=urllib.parse.quote(x['name'])
    out.append(dict(name=x['name'],brand=x['sub_brand'],store=st,price_eur=x['price'],size_g=sz,price_per_kg=round(x['price']/sz*1000,2) if sz else None,
      url=('https://www.hofer.at/suchergebnisse?q='+q) if st=='HOFER' else ('https://www.interspar.at/shop/lebensmittel/search/?q='+q),
      image_url=None,bio=bool(x.get('bio')),price_source='heisse-preise.io latest-canonical'+(' (Altpreis, evtl. ausgelistet)' if x.get('unavailable') else ''),
      price_date=x.get('last'),brand_family=st,sub_brand=x['sub_brand'],source_url=f"https://heisse-preise.io/ ({x['store']} id {x['id']})"))
for x in O:
    sz=num(x.get('size_raw'))
    x=dict(x);x['size_g']=sz;x.pop('size_raw',None);x.pop('ean',None)
    if x['store']=='PENNY': x['store']='PENNY'
    if x.get('protein_100') is not None and sz: x['protein_pack']=round(x['protein_100']*sz/100,1)
    out.append(x)
LIVE={'good-choice-hot-dog':('Good Choice','Hot Dog'),'asia-green-garden-pilztopf':('Asia Green Garden','Pilztopf'),'asia-green-garden-udon-nudelschuessel':('Asia Green Garden',None)}
for k,v in R.items():
    for w,(sb,_) in LIVE.items():
        if w in k:
            t=v['txt'];sz=num(' '.join(t));pr=float(v['price'].replace('€','').replace(',','.').strip())
            out.append(dict(name=f"{t[2].title()} {t[3]}",brand=sb,store='HOFER',price_eur=pr,size_g=sz,price_per_kg=round(pr/sz*1000,2) if sz else None,
              url='https://www.hofer.at'+k,image_url=(v['img'] or '').replace('scaleWidth/232','scaleWidth/600'),price_source='hofer.at Suche live',price_date='2026-10-13',
              brand_family='HOFER',sub_brand=sb,source_url='https://www.hofer.at'+k))
json.dump(out,open('../brandfam_products.json','w'),ensure_ascii=False,indent=1)
import collections;print(len(out),collections.Counter((p['brand_family'],p['sub_brand']) for p in out))
