import json,subprocess,urllib.parse,concurrent.futures as cf
qs="fertiggericht;chef select;vemondo;combino;kania;eintopf;gulasch;curry;lasagne;chili;risotto;suppe;bowl;menü;nudelauflauf;knödel;ravioli;tortelloni;gnocchi;paella;burrito;wrap;tikka;nasi;bami;moussaka;cannelloni;eintöpfe;fertigmenü;mikrowelle;dose;tiefkühl;pizza;linsen;spätzle;schnitzel;cordon;geschnetzeltes;frikassee;pasta;asia;nudeln;salat;sushi;deluxe;mcennedy;vitasia;baresa;gourmet;veggie".split(';')
def G(q):
  u='https://www.lidl.at/q/api/search?'+urllib.parse.urlencode(dict(assortment='AT',locale='de_AT',version='v2.0.0',q=q,fetchsize=100))
  r=subprocess.run(['curl','-s','-m','40','-A','Mozilla/5.0',u],capture_output=True).stdout
  try:return q,json.loads(r)
  except:return q,None
res={}
with cf.ThreadPoolExecutor(6) as ex:
  for q,d in ex.map(G,qs):
    its=(d or {}).get('items',[]);print(q,len(its))
    for it in its:
      g=it.get('gridbox',{}).get('data',{})
      if g.get('category')!='Food':continue
      it['_q']=q;res[it['code']]=it
print('lidl food',len(res))
json.dump(res,open('hourly/lidl_live.json','w'),ensure_ascii=False)
for k,it in res.items():
  g=it['gridbox']['data'];print(k,g.get('fullTitle'),(g.get('price') or {}).get('price'),(g.get('price') or {}).get('packaging',{}).get('text') if isinstance((g.get('price') or {}).get('packaging'),dict) else '')
