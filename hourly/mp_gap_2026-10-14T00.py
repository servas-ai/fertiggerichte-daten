# hourly T00 (2026-10-14T00): MPreis sitemap gap list — product slugs with heat-up-meal stems whose SKU is not yet in scored/connectors_new
import json,sys,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
have={m.group(1) for x in S if 'mpreis' in str(x.get('url')) for m in [re.search(r'-(\d+)$',x.get('url') or '')] if m}
rej=set()
import glob
for f in glob.glob('hourly/added_*.json'):
  try:
    for r in json.load(open(f)).get('rejected',[]): pass
  except Exception: pass
U=M.sitemap_urls(48)
STEM=re.compile(r'lasagne|gulasch|curry|risotto|eintopf|suppe|auflauf|gratin|knoedel|strudel|chili|paella|moussaka|cannelloni|tortelloni|ravioli|gnocchi|spaetzle|nockerl|schnitzel|nugget|cordon|backfisch|bowl|menue|ragout|geschnetzeltes|frikassee|bolognese|carbonara|schmarrn|palatschinken|flammkuchen|quiche|burrito|laibchen|cevapcici|boerek|tikka|masala|wok|bami|nasi|pad-thai|ramen|gyoza|dumpling|fruehlingsroll|kroketten|tarte|pie|stroganoff|ofenfisch|schlemmerfilet|fischstaebchen|wings|strips|frikadell|pfanne|eintopf|linsen|erbsen|bohnen|kaiserschmarrn|germknoedel|marillenknoedel|mohnnudeln|kaesespaetzle|tiroler-groestl|groestl|fleischlaibchen|krautfleckerl|schinkenfleckerl|wurstnudeln|pasta|nudeln-in|maultaschen|enchilada|fajita|kebab|gyros|falafel|hotdog|hot-dog|pizza',re.I)
BAD=re.compile(r'trockensuppe|suppenwuerfel|wuerfel|fond|bruehe-paste|gewuerz|mix-fuer|fix-fuer|sauce-fuer|teig|mehl|baby|hipp|alete|ab-dem|nudeln-roh|spaghetti-\d|pizzateig|pizzamehl|tomaten-pizza|pizzasauce|chips|cracker|snack',re.I)
out=[]
for u in U:
  m=re.search(r'/shop/p/([a-z0-9-]+)-(\d+)$',u)
  if not m or m.group(2) in have: continue
  s=m.group(1)
  if STEM.search(s) and not BAD.search(s): out.append(u)
json.dump(out,open('/tmp/h00/mp_gap.json','w'),indent=0)
print(len(U),'sitemap',len(have),'have',len(out),'gap')
for u in out: print(u.rsplit('/',1)[1])
