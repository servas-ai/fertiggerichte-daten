import json,urllib.request,re,time
B={'LIDL':[('Chef Select','chef-select'),('Vemondo','vemondo'),('Deluxe','deluxe'),('Vitasia','vitasia'),('Kania','kania')],'PENNY':[('Chef Menü','chef-menu'),('Food for Future','food-for-future')],'HOFER':[('Good Choice','good-choice'),('Primana','primana'),("Leibspeis'",'leibspeis'),('Cucina','cucina'),('Asia Green Garden','asia-green-garden'),('Le Gusto','le-gusto'),("Nature's Gold",'nature-s-gold'),('Just Veg','just-veg')]}
MEAL=re.compile(r'eintopf|gulasch|suppe|chili|lasagne|ravioli|risotto|curry|paella|bolognese|carbonara|tortellini|gnocchi|knödel|mit (reis|nudeln|kartoffel|püree|spätzle)|ragout|geschnetzel|bowl|pfanne|menü|pizza|wrap|burrito|moussaka|cannelloni|spätzle|cevapcici|schnitzel|nasi|bami|frühlingsrolle|noodle|nudel|teller|meal|ready',re.I)
out=[]
for fam,L in B.items():
  for sb,tag in L:
    for page in (1,2,3,4):
      u=f"https://world.openfoodfacts.org/api/v2/search?brands_tags={tag}&countries_tags_en=austria&page_size=100&page={page}&fields=code,product_name,product_name_de,brands,quantity,image_front_url,nutriments,nutriscore_grade,manufacturing_places,emb_codes,stores"
      d=None
      for k in range(5):
        try:d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'fertig-research/1.0 (martin)'}),timeout=60));break
        except Exception as e: print(sb,e);time.sleep(20)
      if d is None: continue
      P=d.get('products',[])
      for p in P:
        nm=p.get('product_name_de') or p.get('product_name') or ''
        if not nm or not MEAL.search(nm): continue
        n=p.get('nutriments') or {}
        g=lambda k:n.get(k+'_100g')
        out.append(dict(name=nm,brand=p.get('brands'),store=fam,ean=p['code'],size_raw=p.get('quantity'),image_url=p.get('image_front_url'),
          kcal_100=g('energy-kcal'),protein_100=g('proteins'),fat_100=g('fat'),satfat_100=g('saturated-fat'),carbs_100=g('carbohydrates'),sugar_100=g('sugars'),fiber_100=g('fiber'),salt_100=g('salt'),
          nutriscore=p.get('nutriscore_grade'),producer_id=p.get('emb_codes') or None,origin=p.get('manufacturing_places') or None,
          url=f"https://world.openfoodfacts.org/product/{p['code']}",source_url=f"https://world.openfoodfacts.org/product/{p['code']}",nut_source='Open Food Facts',brand_family=fam,sub_brand=sb))
      print(fam,sb,page,len(P));
      if len(P)<25:break
      time.sleep(6)
      time.sleep(6)
json.dump(out,open('off_family.json','w'),ensure_ascii=False,indent=1)
import collections;print(len(out),collections.Counter(o['sub_brand'] for o in out))
