import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P=json.load(open('/tmp/h12/billa_new.json'))
OK={'Pizza','Menüschalen','Gemüse & Käsegerichte','Asien','Gemüse','Mehlspeisen, Torten'}
SEL=re.compile(r'Pizza|Piccolinis|Suprema|Tradizionale|La Mia|Bowl|Krautfleckerl|K-Noodles Cup|Gemüse Pfanne Asia Curry|Apfel-Strudel',re.I)
NO=re.compile(r'Sauce|Paste|Marinade|Gewürz|Teig|Torte',re.I)
b=Billa(); out=[]
for d in P:
    if d.get('category') not in OK or not SEL.search(d['name']) or NO.search(d['name']): continue
    p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    b.enrich(p); time.sleep(0.4)
    out.append(p.__dict__); print(p.name,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:40],'|',p.producer_id)
json.dump(out,open('hourly/cand_billa_2026-10-13T12.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
