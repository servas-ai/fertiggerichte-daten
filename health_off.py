import json,urllib.request,concurrent.futures as cf
S=json.load(open('/workspace/fertig/scored.json'))
it=[x for x in S if x.get('ean')]
def get(x):
    e=str(x['ean']).strip()
    try:
        u=f'https://world.openfoodfacts.org/api/v2/product/{e}.json?fields=additives_tags,nova_group,nutriscore_grade,labels_tags,ingredients_analysis_tags,origins,manufacturing_places,ingredients_text_de,ingredients_text'
        j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'fertiggerichte-vergleich/1.0'}),timeout=20))
        p=j.get('product') or {}
        if not p: return None
        return {'name':x['name'],'store':x.get('store'),'ean':e,'additives':[a.split(':')[1].upper() for a in p.get('additives_tags',[])],'nova':p.get('nova_group'),'ns':p.get('nutriscore_grade'),'labels':[l.split(':')[1] for l in p.get('labels_tags',[])][:12],'analysis':[l.split(':')[1] for l in p.get('ingredients_analysis_tags',[])],'origins':p.get('origins'),'mplace':p.get('manufacturing_places'),'ingr':(p.get('ingredients_text_de') or p.get('ingredients_text') or '')[:600],'url':f'https://world.openfoodfacts.org/product/{e}'}
    except Exception as ex: return None
with cf.ThreadPoolExecutor(8) as ex: res=[r for r in ex.map(get,it) if r]
json.dump(res,open('/workspace/fertig/analysis/health_off.json','w'),ensure_ascii=False)
print(len(it),len(res),sum(1 for r in res if r['nova']),sum(1 for r in res if r['additives']))
