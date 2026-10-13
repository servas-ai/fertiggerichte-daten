import requests,re,json,time,os
from urllib.parse import urljoin
H={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36"}
NH={"User-Agent":"fertig-research/1.0 (martin-hausleitner.github.io)"}
P=json.load(open('../producers_resolved.json'))['producers']
if os.path.exists('../producers_v2.json'):
  try:
    v2=json.load(open('../producers_v2.json')); P+= (v2.get('producers',v2) if isinstance(v2,dict) else v2)
  except Exception as e: print('v2 err',e)
old=json.load(open('logos.json'))
def slug(s): 
  s=s.lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
  return re.sub(r'[^a-z0-9]+','-',s).strip('-')
# producer meta: slug, website, group (only verified facts)
PM={"GMS GOURMET GmbH":("gms-gourmet","https://www.gourmet.at/","GOURMET (GMS Gourmet GmbH)"),
"Rewe Austria Fleischwaren GmbH":("rewe-austria-fleischwaren","https://rewe-group.at/de/","REWE Group"),
"Wiesbauer Gourmet Gastro GmbH":("wiesbauer-gourmet","https://www.wiesbauer.at/","Wiesbauer"),
"Wilhelm Blasko CONVENIENCE-Fertiggerichte GmbH":("blasko","https://www.blasko.at/",None),
"KARNERTA GmbH":("karnerta","https://www.karnerta.at/",None),
"Landgenossenschaft Ennstal LANDENA KG":("landena","https://www.landena.at/de/","Landgenossenschaft Ennstal"),
"Hink GmbH":("hink","https://hink.wien/",None),
"Greisinger GmbH":("greisinger","https://www.greisinger.at/",None),
"Wiesbauer österreichische Wurstspezialitäten GmbH":("wiesbauer","https://www.wiesbauer.at/","Wiesbauer"),
"Rewe Austria Genussküche GmbH":("rewe-genusskueche","https://rewe-group.at/de/","REWE Group"),
"Hochreiter Quality Meat Factory GmbH":("hochreiter","https://www.hochreiter-gruppe.at/","Hochreiter Gruppe"),
"Hubers Landhendl GmbH":("hubers-landhendl","https://huberslandhendl.at/",None),
"Graninger Holding GmbH":("graninger","https://graninger-lebensmittel.at/","Graninger (unverified link: site is Graninger GmbH, Frastanz)"),
"Radatz - Feine Wiener Fleischwaren GmbH":("radatz","https://www.radatz.at/",None),
"Wech-Geflügel GmbH":("wech","https://www.wech.at/",None),
"Heiploeg International B.V.":("heiploeg","https://www.heiploeg.com/","Heiploeg Group")}
B=[("billa","Billa","chain","https://www.billa.at/","REWE Group"),("spar","Spar","chain","https://www.spar.at/","SPAR Österreich"),
("hofer","Hofer","chain","https://www.hofer.at/","ALDI Süd"),("lidl","Lidl","chain","https://www.lidl.at/","Schwarz Gruppe"),
("penny","Penny","chain","https://www.penny.at/","REWE Group"),("dm","dm","chain","https://www.dm.at/","dm-drogerie markt"),
("fit-to-go","Fit to Go","brand","https://fittogo.at/",None),("knorr","Knorr","brand","https://www.knorr.com/at","Unilever"),
("maggi","Maggi","brand","https://www.nestle.at/marken/alle-marken/maggi","Nestlé"),("inzersdorfer","Inzersdorfer","brand","https://www.inzersdorfer.at/",None),
("felix","Felix","brand","https://www.felix.at/",None),("iglo","Iglo","brand","https://www.iglo.at/","Nomad Foods"),
("planted","Planted","brand","https://eatplanted.com/","Planted Foods AG"),("vegavita","Vegavita","brand","https://www.spar.at/","SPAR (Eigenmarke)"),
("good-choice","Good Choice","brand","https://www.hofer.at/","Hofer (Eigenmarke)"),("clever","Clever","brand","https://www.billa.at/","Billa (Eigenmarke)"),
("s-budget","S-Budget","brand","https://www.spar.at/","SPAR (Eigenmarke)"),("ja-natuerlich","Ja! Natürlich","brand","https://www.janatuerlich.at/","REWE Group")]
def get_logo(sl,site):
  if sl in old and os.path.exists(old[sl]['file']): return old[sl]['file'],old[sl]['source']
  for f in os.listdir('logos'):
    if f.rsplit('.',1)[0]==sl: return 'logos/'+f,'existing'
  try:
    r=requests.get(site,headers=H,timeout=20); h=r.text
  except Exception: return None,None
  c=[urljoin(r.url,x) for x in re.findall(r'(?:src|href)=["\']([^"\'\s]*logo[^"\'\s]*\.(?:svg|png))',h,re.I) if 'white' not in x.lower() and 'footer' not in x.lower()]
  c+= [urljoin(r.url,x) for x in re.findall(r'<link[^>]+rel=["\'](?:apple-touch-icon|icon)[^"\']*["\'][^>]*href=["\']([^"\']+\.(?:svg|png)[^"\']*)',h,re.I)]
  c+= [urljoin(r.url,x) for x in re.findall(r'<meta[^>]+og:image["\'][^>]*content=["\']([^"\']+)',h,re.I)]
  for u in c:
    try:
      x=requests.get(u,headers=H,timeout=20)
      if x.status_code!=200 or len(x.content)<200: continue
      ct=x.headers.get('content-type','')
      ext='svg' if ('svg' in ct or x.content.lstrip()[:5] in (b'<?xml',b'<svg ')) else 'png' if 'png' in ct or x.content[:4]==b'\x89PNG' else None
      if not ext: continue
      p=f'logos/{sl}.{ext}'; open(p,'wb').write(x.content); return p,u
    except Exception: pass
  return None,None
GC={}
def geo(addr):
  if addr in GC: return GC[addr]
  time.sleep(1.1)
  try: j=requests.get('https://nominatim.openstreetmap.org/search',params={'q':addr,'format':'json','limit':1},headers=NH,timeout=20).json()
  except Exception: j=[]
  if not j and ',' in addr:
    time.sleep(1.1); j=requests.get('https://nominatim.openstreetmap.org/search',params={'q':addr.split(',',1)[1],'format':'json','limit':1},headers=NH,timeout=20).json()
    GC[addr]=(float(j[0]['lat']),float(j[0]['lon']),'town-level') if j else (None,None,None); return GC[addr]
  GC[addr]=(float(j[0]['lat']),float(j[0]['lon']),'address') if j else (None,None,None); return GC[addr]
out={}
for p in P:
  n=p.get('company')
  if not n: continue
  sl,web,grp=PM.get(n,(slug(n),None,None))
  addr=p.get('town'); 
  pa=[]
  if addr:
    q=addr+(', Austria' if p['state']!='Niederlande' else ', Netherlands')
    la,lo,prec=geo(q)
    town=re.sub(r'^\d{4}\s*','',addr.split(',')[-1].strip())
    pa.append(dict(address=addr,town=town,state=p.get('state'),lat=la,lon=lo,geocode_precision=prec,approval_code=p.get('code'),source=p.get('source')))
  if sl in out: out[sl]['plant_addresses']+=pa; continue
  out[sl]=dict(slug=sl,name=n,type='producer',website=web,logo_path=None,logo_source=None,plant_addresses=pa,group=grp,retail_brands=sorted(set(p.get('retail_brands') or [])))
for sl,n,t,w,g in B:
  out.setdefault(sl,dict(slug=sl,name=n,type=t,website=w,logo_path=None,logo_source=None,plant_addresses=[],group=g))
for o in out.values():
  if o['website']:
    lp,src=get_logo(o['slug'],o['website'])
    if lp: o['logo_path']='/workspace/fertig/analysis/'+lp; o['logo_source']=src
    print(o['slug'],lp,src)
json.dump(list(out.values()),open('companies.json','w'),indent=1,ensure_ascii=False)
