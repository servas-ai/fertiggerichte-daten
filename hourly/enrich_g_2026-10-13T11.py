import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.schema import Product
g=Gurkerl()
P=json.load(open('/tmp/h11/g_new.json'))
SEL=re.compile(r'Alnatura BIO Pizza|Big Sensation|Ristorante Pizza|Steinofen|Gustavo Gusto|Die Backfrische|Pietro Pizzi|Ofenfrische|Dinkel-Pizza Vegetariana|Margherita GLUTENFREI|Holy Slice|Erdäpfelgulasch|Rindsgulasch|Caesar Salad|Ceasar Salad|Fisch´n´Rösti|Schlemmerfilet BIO|Fledermaus|Schweinebacken|Instant Noodle Pot|Instant-Cup-Nudeln|Buldak  Ramen Cheese|Topokki Kimchi|Mezeteller|Tabouleh|Pizza Pockets|Gissinger Schinkenrollen|Macaroni Cheese',re.I)
out=[]
for d in P:
    if not SEL.search(d['name']) or not d['extra'].get('in_stock'): continue
    p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    g.enrich(p); time.sleep(0.3)
    out.append(p.__dict__)
    print(p.name,'|',p.nutrition_100g,'|',p.ean,'|',p.producer,'|',p.producer_id)
json.dump(out,open('/tmp/h11/g_enriched.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
