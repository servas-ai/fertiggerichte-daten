import json,re,collections
from dishes import dish_key
S=json.load(open('scored.json'))
txt=open('scored.json').read()+open('expand.json').read()
seen={s.lstrip('0') for s in re.findall(r'-00?(\d{5,7})"',txt)}
N=lambda s:re.sub(r'\s*\d+([.,]\d+)?\s?(g|kg|ml|l)\b.*$','',re.sub(r'[^a-z0-9 ]','',(s or '').lower())).replace(' ','')
names={N(p.get('name')) for p in S}
NOISE=re.compile(r'creme|lip|fuß|spray|katze|hund|nassfutter|baby|babymen|gläschen|aufstrich|thunfisch|sardin|hering|wurst|würst|schinken|salami|käse(?!sp)|chips|tyrolini|taler|schnecke|schote|salz|mühle|gewürz|masala|reis lose|risotto ?reis|collezione|auflaufform|backform|schüssel|form\b|öl\b|essig|sauce|sugo|pesto|tee|schokolade|kuchen|muffin|nüsse|nuss|kerne|bier|limo|eis\b|insekt|schuh|bohnen\b(?!.*(eintopf|suppe|speck|topf))|aufschnitt|leberkäse|riegel|cracker|stange|stick|gurke|oliven|pulver|würfel|brühe|fond\b|senf|mayo|dip\b|hummus|tofu natur|kokos|drink|smoothie|joghurt|gnocchi$|nudeln$|teig|blätter|platten|röhren|lunchbox|box set|teller',re.I)
STRICT={'chili-con-carne':r'chili con|chili mit|chili-?topf|chili \d',
 'curry':r'curry.*(reis|nudel|mit|\d{3} ?g)|(reis|nudel).*curry','huhn-curry':r'.','hirschragout':r'ragout|gulasch|braten','risotto':r'risotto (mit|al|ai|con)|pilz|steinpilz|risotto \w+ \d|gericht','ravioli':r'.','rindsgulasch':r'.'}
def ok(name,k):
  if NOISE.search(name): return False
  p=STRICT.get(k)
  return not p or re.search(p,name,re.I)
out=[]
A=json.load(open('hourly/billa_all.json'))
GOODP=re.compile(r'Fertiggericht|Tiefkühlgerichte|Feinkost|Suppen|Menü|Schnelle Küche > (Gerichte|Fertig)|Dose|Rein Pflanzlich > (Fertig|Reis, Pasta)|Tiefkühl > (Fisch & Fleisch|Gemüse & Käse|Pizza|Asia|Reis)',re.I)
for s,r in A.items():
  k=dish_key(r['name'])
  if not k or not ok(r['name'],k): continue
  path=' > '.join(x['name'] for x in (r.get('parentCategories') or [[]])[0])
  if not GOODP.search(path): continue
  if r['slug'].split('-')[-1].lstrip('0') in seen or N(r['name']) in names: continue
  out.append(dict(src='billa',sku=s,k=k,name=r['name'],path=path,price=r['price']['regular']['value']/100,amount=r.get('amount'),unit=r.get('volumeLabelShort')))
H=json.load(open('heisse_preise_raw.json'))
for h in H:
  if h['store'] not in('spar','hofer','dm') or h.get('unavailable')=='True': continue
  k=dish_key(h['name'])
  if not k or not ok(h['name'],k) or N(h['name']) in names: continue
  ph=h.get('priceHistory') or []; ph=eval(ph) if isinstance(ph,str) else ph
  last=max((p['date'] for p in ph),default=None)
  out.append(dict(src=h['store'],sku=h['id'],k=k,name=h['name'],price=float(h['price']),amount=h.get('quantity'),unit=h.get('unit'),url=h.get('url'),last=last,cat=h.get('category')))
# dedupe
u={};[u.setdefault((o['src'],N(o['name'])),o) for o in out];out=list(u.values())
json.dump(out,open('classics_cand.json','w'),ensure_ascii=False,indent=0)
print(len(out),collections.Counter(o['src'] for o in out))
for o in out: print(o['src'],o['k'],'|',o['name'],'|',o['price'],o.get('amount'),o.get('unit'),o.get('last'),o.get('path','')[-35:])
