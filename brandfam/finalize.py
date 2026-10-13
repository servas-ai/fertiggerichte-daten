import json,os,collections
D=json.load(open('brand_families_def.json'))
VG=json.load(open('qa/vision_gate.json')) if os.path.exists('qa/vision_gate.json') else {'logos':{},'products':{}}
S=json.load(open('scored.json'))
by=collections.defaultdict(list)
for x in S:
    if x.get('sub_brand') and x.get('is_meal',True) and not x.get('dry'):
        img=x.get('image_url'); v=VG['products'].get(img) if img else None
        by[(x['brand_family'],x['sub_brand'])].append(dict(name=x['name'],store=x.get('store'),url=x.get('url'),source_url=x.get('source_url') or x.get('url'),
          img=img if (v and v.get('pass')) else None,vision=(v or {}).get('pass'),price=x.get('price_eur'),size_g=x.get('size_g'),price_status=x.get('price_status'),
          protein_100=x.get('protein_100'),kcal_100=x.get('kcal_100'),protein_per_euro=x.get('protein_per_euro'),health_score=x.get('health_score'),
          nutriscore=x.get('nutriscore'),packaging=x.get('packaging'),manufacturer=(x.get('manufacturer') or '').split('\n')[0] or None,producer_id=x.get('producer_id')))
fams=[];tot=0
for f in D['families']:
    f=dict(f);subs=[]
    for s in f['sub_brands']:
        s=dict(s);lv=VG['logos'].get(s['logo']) if s.get('logo') else None
        if s.get('logo') and not (lv and lv.get('pass')): s['logo_rejected']=s['logo'];s['logo']=None
        s['products']=sorted(by.get((f['chain'],s['name']),[]),key=lambda p:-(p['protein_per_euro'] or 0))
        s['count']=len(s['products']);subs.append(s)
    f['sub_brands']=subs;f['count']=sum(s['count'] for s in subs);tot+=f['count'];fams.append(f)
lv=VG['logos'].get
D2=dict(D,families=fams,total=tot,vision_gate=VG.get('summary'))
json.dump(D2,open('brand_families.json','w'),ensure_ascii=False,indent=1)
os.makedirs('/workspace/fertig-app/public',exist_ok=True)
json.dump(D2,open('/workspace/fertig-app/public/brand_families.json','w'),ensure_ascii=False)
for f in fams: print(f['name'],f['count'],{s['name']:s['count'] for s in f['sub_brands']})
