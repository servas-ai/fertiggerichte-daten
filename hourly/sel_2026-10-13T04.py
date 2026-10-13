import json,re,sys,concurrent.futures as cf
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import ADAPTERS
from food_connectors.schema import Product
K='Kühlregal (Menüschale/frisch)';T='TK (Tiefkühl)';SV='Sous-vide (vakuum)';D='Dose'
SEL=[ # (name regex, category, packaging)
 (r'^Pappudia Gebackener Käse','Komplettmahlzeit',K),(r'^Pappudia Rindfleisch in Paradeiser','Komplettmahlzeit',K),
 (r'^Meica Curry King','Komplettmahlzeit',K),(r'^Hühnerfilet in Pilzsauce mit Reis','Komplettmahlzeit',K),
 (r'^Radatz Salonbeuschl','Komplettmahlzeit',K),(r'^Gissinger Fledermaus','Komplettmahlzeit',K),(r'^Gissinger Gansl','Komplettmahlzeit',K),
 (r'^Wiener Virtshaus Linsen','Komplettmahlzeit',K),(r'^High Protein Pasta mit Hähnchen','Komplettmahlzeit',K),
 (r'^Paneer Makhani','Komplettmahlzeit',K),(r'^Hähnchencurry mit Grünen Bohnen','Komplettmahlzeit',K),(r'^Butter Chicken mit Naan','Komplettmahlzeit',K),
 (r'^Fleischbällchen in Tomatensauce mit Tarhonya','Komplettmahlzeit',K),(r'^Wiesbauer Mediterrane Schweinebacken','Komplettmahlzeit',SV),
 (r'^Freshery Tom Yum','Suppe/Eintopf',K),(r'^Freshery Pho','Suppe/Eintopf',K),
 (r'^Mochi Spicy Chicken Ramen','Suppe/Eintopf',K),(r'^Mochi Tonkotsu Ramen','Suppe/Eintopf',K),(r'^Mochi Mushroom Miso Ramen','Suppe/Eintopf',K),
 (r'^Pappudia Kuttelsuppe','Suppe/Eintopf',K),(r'^DimmidiSi Kürbis Karotten Cremesuppe','Suppe/Eintopf',K),(r'^La Cocina de Lola Gazpacho','Suppe/Eintopf',None),
 (r"^HOFMANNs Oma's Fleischpflanzerl",'Komplettmahlzeit',T),(r'^HOFMANNs Asia-Erdnuss-Nudeln','Komplettmahlzeit',T),
 (r'^Iglo 3 Riesen-Germknödel','Nachspeise',T),(r'^HOFMANNs Kaiserschmarren','Nachspeise',T),(r'^PICARD 2 Vanille Crème Brûlées','Nachspeise',T),
 (r'^Inzersdorfer Erdäpfelgulasch','Suppe/Eintopf',D),(r'^Inzersdorfer Rindsgulasch','Komplettmahlzeit',D),(r'^Felix Erdäpfelgulasch','Suppe/Eintopf',D),
 (r'^Bonduelle Linsen Curry','Komplettmahlzeit',D),(r'^Bonduelle Linseneintop','Suppe/Eintopf',D),(r'^Marks & Spencer Spaghetti Loops','Komplettmahlzeit',D),
]
P=json.load(open('/tmp/gk_new.json'))
G=ADAPTERS['gurkerl']
picked=[]
for rx,cat,pack in SEL:
  m=[p for p in P if re.search(rx,p['name'])]
  if not m: print('MISS',rx); continue
  picked.append((m[0],cat,pack))
def enr(t):
  p,cat,pack=t
  try:
    pr=Product(**{k:v for k,v in p.items() if k in Product.__dataclass_fields__})
    e=G.enrich(pr).to_dict()
  except Exception as ex: print('ERR',p['name'],ex); e=p
  return e,cat,pack
with cf.ThreadPoolExecutor(6) as ex: R=list(ex.map(enr,picked))
json.dump([dict(p=e,cat=c,pack=k) for e,c,k in R],open('hourly/cand_enriched_2026-10-13T04.json','w'),ensure_ascii=False,indent=1)
for e,c,k in R: n=e.get('nutrition_100g') or {}; print(e['name'][:50],'|',n.get('kcal'),n.get('protein'),n.get('salt'),'|',e.get('producer'),e.get('producer_id'),e.get('ean'))
