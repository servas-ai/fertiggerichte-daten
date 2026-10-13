import json,urllib.request,urllib.parse,collections,concurrent.futures as cf
def J(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))
SUB={'Clever':'clever','Billa Immer Gut':'billa-immer-gut','Simply Good':'simply-good','Omis Schmankerl':'omis-schmankerl','Billa Bio':'billa-bio','Ja! Natürlich':'ja--natuerlich','Corso':'corso','Billa Genusswelt':'billa-genusswelt','Vegavita':'vegavita','Billa':'billa','Billa Plus':'billa-plus'}
def run(sb):
    out=[];p=0
    while p<15:
        try:d=J(f"https://shop.billa.at/api/product-discovery/products?brand={SUB[sb]}&page={p}&pageSize=100")
        except Exception as e: print(sb,e);break
        r=d.get('results',[]);out+=r
        if len(r)<100:break
        p+=1
    return sb,out
res={}
with cf.ThreadPoolExecutor(4) as ex:
    for sb,o in ex.map(run,SUB): res[sb]=o; print(sb,len(o))
json.dump(res,open('billa_raw.json','w'),ensure_ascii=False)
c=collections.Counter(' > '.join(c['name'] for c in (x.get('parentCategories') or [[]])[0][:3]) for v in res.values() for x in v)
for k,v in c.most_common(400): print(v,k)
