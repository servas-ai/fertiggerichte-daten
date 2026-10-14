# hourly T02 (2026-10-14T02): MPreis sitemap gap — heat-up meal stems whose SKU not yet in scored/connectors_new
import json,sys,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
have={m.group(1) for x in S if 'mpreis' in str(x.get('url')) for m in [re.search(r'-(\d+)$',x.get('url') or '')] if m}
U=M.sitemap_urls(48)
STEM=re.compile(r'lasagne|gulasch|curry|risotto|eintopf|suppe|auflauf|gratin|knoedel|strudel|chili|paella|moussaka|cannelloni|tortelloni|ravioli|gnocchi|spaetzle|nockerl|schnitzel|nugget|cordon|backfisch|bowl|menue|ragout|geschnetzeltes|frikassee|bolognese|carbonara|schmarrn|palatschinken|flammkuchen|quiche|burrito|laibchen|cevapcici|boerek|tikka|masala|wok|bami|nasi|pad-thai|ramen|gyoza|dumpling|fruehlingsroll|kroketten|tarte|pie|stroganoff|ofenfisch|schlemmerfilet|fischstaebchen|wings|strips|frikadell|pfanne|linsen|erbsen|bohnen|kaiserschmarrn|germknoedel|marillenknoedel|mohnnudeln|kaesespaetzle|tiroler-groestl|groestl|fleischlaibchen|krautfleckerl|schinkenfleckerl|wurstnudeln|pasta|nudeln-in|maultaschen|enchilada|fajita|kebab|gyros|falafel|pizza|backhendl|hendl|huhn|chicken|fisch|garnelen|shrimp|pelmeni|pierogi|ravioli|spätzle|spaetzle|tortilla|wrap-menue|fertiggericht|dosen|inzersdorfer|felix|iglo|frosta|wagner|ristorante|jeden-tag|clever|alma|naturapur|s-budget|good-choice|primana|le-gusto|cucina|dr-oetker|pietro|gustavo|toni-kaiser|allgroo|yum|bamboo|natsu|garden-gourmet|planted|heura|rebel|hubers|vega|followfood|costa|apetito|stastnik|hink|spitz|sonnen-bassermann|erasco|little-lunch|suppenliebe|knorr|maggi|miettes|backofen|ofen|panier|sticks|nuggets|burger|hot-dog|hotdog|paprika-gefuellt|kohlroulade|sarma|boulette|frikadelle|hackbraten|braten|schweinebraten|tafelspitz|beuschel|fiaker|szegedin|rindfleisch|pute|truthahn|ente|lachs|seelachs|kabeljau|forelle|thunfisch|makrele|sardine|pizza|pinsa|calzone|stromboli|quesadilla|taco|enchilada|burrito|chili|ratatouille|cassoulet|bouillabaisse|minestrone|pho|tom-yum|tom-kha|laksa|massaman|green-curry|red-curry|yellow-curry|korma|biryani|jambalaya|paella|risotto|arroz|couscous|bulgur|quinoa|dal|dahl|hummus-bowl|buddha|poke|sashimi-bowl|pokebowl',re.I)
BAD=re.compile(r'trockensuppe|suppenwuerfel|wuerfel|fond|bruehe-paste|gewuerz|mix-fuer|fix-fuer|sauce-fuer|teig$|mehl|baby|hipp|alete|ab-dem|nudeln-roh|spaghetti-\d|pizzateig|pizzamehl|tomaten-pizza|pizzasauce|chips|cracker|snack|joghurt|quark|milch$|sahne|butter$|kaese$|wurst$|schinken$|speck$|salami|aufschnitt|brot$|semmel|toast|bagel|croissant|muffin|kuchen-mix|backmischung|reis-natur|reis-basmati|reis-jasmin|nudeln-\d00g$|spaghetti-500|penne-500|fusilli|reis-500|kartoffel$|zwiebel|knoblauch|tomate-passiert|passata|ketchup|senf|mayo|oel$|essig|salz$|pfeffer|zucker$|honig$|marmelade|konfituere|schokolade-tafel|praline|gummi|bonbon|kaugummi|wasser$|saft$|limonade|cola|bier|wein|kaffee|tee$',re.I)
out=[]
for u in U:
  m=re.search(r'/shop/p/([a-z0-9-]+)-(\d+)$',u)
  if not m or m.group(2) in have: continue
  s=m.group(1)
  if STEM.search(s) and not BAD.search(s): out.append(u)
json.dump(out,open('/tmp/h02/mp_gap.json','w'),indent=0)
print(len(U),'sitemap',len(have),'have',len(out),'gap')
for u in out[:120]: print(u.rsplit('/',1)[1])
if len(out)>120: print('... +',len(out)-120,'more')
