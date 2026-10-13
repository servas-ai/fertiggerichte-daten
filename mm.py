import json,urllib.request,urllib.parse,glob,re,concurrent.futures as cf
exec(open('ex.py').read().split('W=lambda')[0].split("C=json")[0])
NM={'ENER-':'kcal','PRO-':'protein','FAT':'fat','FASAT':'satfat','CHOAVL':'carbs','SUGAR-':'sugar','FIBTG':'fiber','SALTEQ':'salt'}
NK=['kcal','protein','fat','satfat','carbs','sugar','fiber','salt']
src=open('ex.py').read();exec(src[src.index('def billa'):src.index('W=lambda')])
H={'User-Agent':'Mozilla/5.0'}
def J(u):return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
# existing
seen=set();names=set()
for f in glob.glob('*.json')+glob.glob('hg/*.json'):
  try:t=open(f).read()
  except:continue
  seen|=set(re.findall(r'00-\d{6}',t))|set(re.findall(r'-00(\d{6})"',t) and ['00-'+x for x in re.findall(r'-00(\d{6})"',t)])
for x in json.load(open('expand.json')): names.add(x['name'].lower())
terms="menüschale;fertiggericht hühner;hendl curry;geschnetzeltes;gulasch fertig;chili con carne;rindsgulasch;schweinsbraten fertig;ripperl;cevapcici fertig;lasagne;moussaka;kaiserschmarrn;bowl;protein;high protein;linseneintopf;bohneneintopf;chili sin carne;hühnerreis;nasi goreng;bami goreng;butter chicken;tikka masala;chicken;pulled pork;rinderroulade;sauerbraten;kartoffelgratin;tiefkühl gericht;iglo;frosta;mikrowelle;gefüllte paprika;krautfleckerl;fleischlaibchen;cordon bleu fertig;schnitzel fertig;gyros;kebab;pad thai;ramen;dal;falafel bowl;tortellini;gnocchi pfanne;spätzle pfanne;käsespätzle;hühnerfrikassee;stroganoff;bolognese fertig;ofenkartoffel;sous vide;billa genusswelt;spar natur pur fertig;ja natürlich fertiggericht;wiesbauer gourmet;greisinger;hütthaler;eto;inzersdorfer;felix;knorr;maggi;hipp".split(';')
cand={}
def S(t):
  out=[]
  for p in range(2):
    try:d=J("https://shop.billa.at/api/product-discovery/products?"+urllib.parse.urlencode({'searchTerm':t,'page':p,'pageSize':50,'storeId':'00-10'}))
    except:break
    out+=d.get('results',[])
    if len(d.get('results',[]))<50:break
  return out
with cf.ThreadPoolExecutor(6) as ex:
  for rs in ex.map(S,terms):
    for r in rs: cand[r['sku']]=r
for c in ['15395','15390','15391','15232','15233','13842','13969']:
  for p in range(5):
    try:d=J(f"https://shop.billa.at/api/product-discovery/categories/{c}/products?page={p}&pageSize=100")
    except:break
    for r in d.get('results',[]):cand[r['sku']]=r
    if len(d.get('results',[]))<100:break
print('cand',len(cand))
json.dump(cand,open('mm_cand.json','w'),ensure_ascii=False)
