import json,urllib.request,urllib.parse,time,itertools
F='code,product_name,product_name_de,generic_name_de,brands,countries_tags,categories_tags,nutriments,image_front_url,emb_codes,quantity,product_quantity,nutriscore_grade,origins,manufacturing_places,last_modified_t,stores,labels_tags,nova_group'
def Q(q,page=1):
  u='https://search.openfoodfacts.org/search?'+urllib.parse.urlencode(dict(q=q,page_size=100,page=page,fields=F))
  for i in range(4):
    try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'FertigCompare/1.0'}),timeout=60))
    except Exception as e:print('err',e);time.sleep(4*(i+1))
  return {}
res={}
for br in ['chef select','vemondo','combino','deluxe','mcennedy','select&go','vitasia','lidl','baresa','ocean sea','next level','meine metzgerei','chef select & you']:
  for cat in ['en:meals','en:soups','en:stews']:
    for c in ['en:austria','en:germany']:
      q=f'brands:"{br}" categories_tags:"{cat}" countries_tags:"{c}"'
      for p in (1,2,3):
        d=Q(q,p);h=d.get('hits',[])
        for x in h:x.setdefault('_c',c);res.setdefault(x['code'],x)
        if len(h)<100:break
      print(br,cat,c,d.get('count'),len(res))
json.dump(res,open('hourly/off_lidl.json','w'),ensure_ascii=False)
