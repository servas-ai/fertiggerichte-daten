import json,urllib.request,urllib.parse,re,os,time
UA={'User-Agent':'fertig-vergleich/1.0 (martin; logo research)'}
def j(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
Q=[('mueller','Müller',['Müller'],'Müller dairy'),('alpro','Alpro',['Alpro','alpro'],'Alpro'),('danone','Danone',['Danone'],'Danone'),('picard','Picard',['PICARD','Picard'],'Picard'),('noem','NÖM',['Nöm','nöm PRO','nöm Cremix','NÖM'],'NÖM'),('darbo','Darbo',['Darbo'],'Adolf Darbo'),('andros','Andros',['Andros'],'Andros company'),('landliebe','Landliebe',['Landliebe'],'Landliebe brand')]
res=json.load(open('logos_new.json'))
for slug,name,brands,q in Q:
  try:
    s=j('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode({'action':'wbsearchentities','search':q,'language':'en','format':'json','limit':5}))
    f=None
    for e in s.get('search',[]):
      c=j(f"https://www.wikidata.org/wiki/Special:EntityData/{e['id']}.json")['entities'][e['id']]['claims']
      if 'P154' in c: f=c['P154'][0]['mainsnak']['datavalue']['value'];qid=e['id'];break
      time.sleep(0.5)
    if not f: print('none',name);continue
    ext=f.rsplit('.',1)[-1].lower(); fn=f'logos_new/{slug}.{ext}'
    u='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(f.replace(' ','_'))
    open(fn,'wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read())
    res[slug]=dict(slug=slug,name=name,brands=brands,logo_category='Marke',file=f'logos/{slug}.{ext}',source=u,wikidata=qid,size=ext,note='Wikidata P154 / Wikimedia Commons',hq=ext=='svg')
    print('ok',name,f,qid)
  except Exception as e: print('err',name,e)
  time.sleep(1)
json.dump(res,open('logos_new.json','w'),ensure_ascii=False,indent=1)
