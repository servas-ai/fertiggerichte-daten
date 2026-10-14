"""Hofer GOOD CHOICE GTIN fill (2026-10-14, sensecheck 6 §3 follow-up).

Fills nutrition for Hofer GOOD CHOICE rows that had none, ONLY from Open Food Facts products
looked up by EAN (API v2, https://world.openfoodfacts.org/api/v2/product/<ean>.json) where
brand = Good Choice and pack size match. For the two wraps and the Spaghettini OFF has no
brand/quantity *fields*, so brand + weight were verified on the OFF front photo and every value
on the OFF nutrition-panel photo (URLs in qa/hofer_gtin_off_2026-10-14.json). Values are
per 100 g as printed; *_pack = per-100 g value x size_g (same convention as 53d3b5f).
nutrition_source = 'GTIN-confirmed' (same label as 47f93a9 / fertig-app d59ae65).
Idempotent; only touches entries matched by exact (file, name, store HOFER, size_g).

Not filled (OFF has nothing usable): see SKIPPED below.
"""
import json
V={
 '4099200075556':dict(kcal_100=266,protein_100=11,fat_100=13,satfat_100=3.4,carbs_100=25,sugar_100=4.3,fiber_100=None,salt_100=1.6,nutriscore='d',size=170,
     image_url='https://images.openfoodfacts.org/images/products/409/920/007/5556/front_fr.3.400.jpg'),
 '4099200075570':dict(kcal_100=220,protein_100=5.4,fat_100=7.5,satfat_100=0.9,carbs_100=32,sugar_100=3.5,fiber_100=None,salt_100=1.5,nutriscore='c',size=170,
     image_url='https://images.openfoodfacts.org/images/products/409/920/007/5570/front_fr.3.400.jpg'),
 '4061463022950':dict(kcal_100=113,protein_100=3.3,fat_100=2.6,satfat_100=0.3,carbs_100=18,sugar_100=1.6,fiber_100=None,salt_100=0.84,nutriscore=None,size=400,
     image_url='https://images.openfoodfacts.org/images/products/406/146/302/2950/front_de.3.400.jpg'),
 '4061463023018':dict(kcal_100=119,protein_100=4.0,fat_100=5.4,satfat_100=1.8,carbs_100=13,sugar_100=0.9,fiber_100=None,salt_100=1.02,nutriscore=None,size=400,
     image_url='https://images.openfoodfacts.org/images/products/406/146/302/3018/front_de.7.400.jpg'),
}
T=[  # (file, indent, exact name, ean)
 ('brandfam_products.json',2,'GOOD CHOICE Wrap Caeser Chicken 170g','4099200075556'),
 ('brandfam_products.json',2,'GOOD CHOICE Wraps Thai Couscous 170g','4099200075570'),
 ('hofer_goodchoice.json',1,'Pasta Fertiggerichte Pecorelli in Tomatensauce','4061463022950'),
 ('hofer_goodchoice.json',1,'Pasta Fertiggerichte Lachs Spaghettini','4061463023018'),
 ('hofer_lidl.json',1,'GOOD CHOICE Pasta Fertiggerichte Pecorelli in Tomatensauce 400g','4061463022950'),
 ('hofer_lidl.json',1,'GOOD CHOICE Pasta Fertiggerichte Lachs Spaghettini 400g','4061463023018'),
]
SKIPPED={
 'GOOD CHOICE Schwammerlsauce mit Serviettenknödel 380g':'OFF 4099200146263 "Schwammerlsauce": no quantity, no photos -> size not verifiable',
 'Burger Chicken / Burger Cheese':'OFF 4099200051932 (HU, 300 g) / 4099200051949 (no quantity, no photos); snack, not filled',
 'GOOD CHOICE Risotto Pilz/Pilze 400g':'OFF only 4099200423159 Risotto Funghi 350 g (CH) -> size mismatch',
 'GOOD CHOICE Asia Curry Chicken Süß-Sauer 400g':'OFF only 4099200420783 350 g (CH-only) -> size mismatch',
 'GOOD CHOICE Pinzgauer Käsespätzle 380g':'OFF text search "käsespätzle good choice" = 0 hits (4061463822857 380 g is Cannelloni, not in our data)',
 'GOOD CHOICE Risotto Tomate 400g':'OFF 4061459374223 Risotto pomodoro 400 g is CH-only (countries switzerland) -> not used for AT',
 'Good Choice Hot Dog 280g':'OFF search rate-limited (HTTP 503), not checked',
}
def main():
    by={}
    for fn,ind,name,ean in T: by.setdefault((fn,ind),[]).append((name,ean))
    n=0
    for (fn,ind),items in by.items():
        D=json.load(open(fn,encoding='utf-8'))
        for name,ean in items:
            v=V[ean]; hit=[x for x in D if x.get('name')==name and str(x.get('store','')).upper()=='HOFER' and float(x.get('size_g') or 0)==v['size']]
            assert len(hit)==1,(fn,name,len(hit))
            x=hit[0]
            for k in ('kcal_100','protein_100','fat_100','satfat_100','carbs_100','sugar_100','fiber_100','salt_100'): x[k]=v[k]
            x['kcal_pack']=round(v['kcal_100']*v['size']/100)
            x['protein_pack']=round(v['protein_100']*v['size']/100,1)
            x['nutriscore']=v['nutriscore'] if v['nutriscore'] else x.get('nutriscore')
            x['ean']=ean
            if not x.get('image_url'): x['image_url']=v['image_url']
            x['nut_source']='GTIN-confirmed'; x['nutrition_source']='GTIN-confirmed'
            n+=1
        open(fn,'w',encoding='utf-8').write(json.dumps(D,ensure_ascii=False,indent=ind))
    print('hofer_gtin_fill: updated',n,'entries')
if __name__=='__main__': main()
