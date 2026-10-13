import json,urllib.request,urllib.parse,re,concurrent.futures as cf
H={'User-Agent':'Mozilla/5.0'}
def J(u):return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
cats='15395 15390 15391 15232 15233 13842 13969 15401 15403 15405 15474 15492 15394 15400 15129 15494 15497 15231 15496'.split()
terms="menüschale;fertiggericht;gulasch;chili con carne;chili sin carne;curry;lasagne;eintopf;risotto;meisterkessel;inzersdorfer;iglo;frosta;gefüllte paprika;krautfleckerl;geschnetzeltes;moussaka;tikka masala;butter chicken;nasi goreng;bami goreng;linseneintopf;erbseneintopf;bohneneintopf;gulaschsuppe;fleischknödel;szegediner;hühnerfrikassee;stroganoff;käsespätzle;schinkenfleckerl;spinatknödel;cannelloni;tortellini gericht;ravioli;penne;spaghetti bolognese;knödel mit ei;rindsgulasch;kalbsgulasch;fiakergulasch;saftgulasch;wildgulasch;beuschel;letscho;paella;bowl;wrap;burrito;quiche;pfanne;auflauf;gratin;omis;billa genusswelt;wiesbauer;hütthaler;greisinger;sonnen bassermann;erasco;maggi;knorr".split(';')
cand={}
def C(c):
  out=[]
  for p in range(8):
    try:d=J(f"https://shop.billa.at/api/product-discovery/categories/{c}/products?page={p}&pageSize=100&storeId=00-10")
    except Exception as e:print('cat',c,e);break
    rs=d.get('results',[]);[r.setdefault('_cat',c) for r in rs];out+=rs
    if len(rs)<100:break
  return out
def S(t):
  out=[]
  for p in range(3):
    try:d=J("https://shop.billa.at/api/product-discovery/products?"+urllib.parse.urlencode({'searchTerm':t,'page':p,'pageSize':50,'storeId':'00-10'}))
    except Exception as e:print('s',t,e);break
    rs=d.get('results',[]);[r.setdefault('_q',t) for r in rs];out+=rs
    if len(rs)<50:break
  return out
with cf.ThreadPoolExecutor(8) as ex:
  for rs in ex.map(C,cats):
    for r in rs:cand.setdefault(r['sku'],r)
  for rs in ex.map(S,terms):
    for r in rs:cand.setdefault(r['sku'],r)
print('cand',len(cand))
json.dump(cand,open('hourly/b_cand.json','w'),ensure_ascii=False)
