import json,re
h=json.load(open('../heisse_preise_raw.json'))
FAM={'hofer':[('Good Choice',r'good choice'),('Primana',r'primana'),("Leibspeis'",r'leibspeis'),('Cucina',r'cucina'),('Asia Green Garden',r'asia green'),('Gourmet',r'gourmet'),('Le Gusto',r'le gusto'),("Nature's Gold",r"nature.?s gold"),('Zurück zum Ursprung',r'zurück zum'),('Just Veg',r'just veg'),('Enjoy Free',r'enjoy free')],
 'spar':[('S-Budget',r's-budget'),('Spar Feine Küche',r'feine küche'),('Spar Premium',r'spar premium'),('Spar Natur*pur',r'natur\*?pur'),('Spar Veggie',r'spar veggie'),('Spar enjoy',r'spar enjoy'),('Spar Vital',r'spar vital')],
 'billa':[('Chef Menü',r'chef men'),('Food for Future',r'food for future')]}
MEAL=re.compile(r'eintopf|gulasch|suppe\b|suppentopf|chili con|lasagne|ravioli|risotto|curry|paella|bolognese|carbonara|tortellini|gnocchi|knödel mit|mit (reis|nudeln|kartoffel|püree|spätzle|knödel)|ragout|geschnetzel|bowl|pfanne|menü|pizza|wrap|burrito|moussaka|cannelloni|spätzle|kaiserschmarrn|fleischlaberl|cevapcici|schnitzel|rahmsuppe|risi|nasi|bami|frühlingsrolle|teller|salatbox',re.I)
NO=re.compile(r'würze|würfel|gewürz|\bfix\b|soße|sauce$|pesto|tiernahrung|katze|hund|suppengrün|suppenwürfel|suppenhuhn|einlage|nudeln \d|grieß',re.I)
out=[]
for x in h:
    st=x['store']
    if st not in FAM: continue
    n=x['name'].strip()
    for sb,p in FAM[st]:
        if re.search(p,n,re.I) and MEAL.search(n) and not NO.search(n) and (st=='hofer' or not x.get('unavailable')):
            out.append(dict(store=st,sub_brand=sb,name=n,price=x['price'],qty=x.get('quantity'),unit=x.get('unit'),url=x.get('url'),id=x['id'],last=(x.get('priceHistory') or [{}])[0].get('date'),bio=x.get('bio'),unavailable=x.get('unavailable'),raw_url=x.get('url')));break
json.dump(out,open('hp_family.json','w'),ensure_ascii=False,indent=1)
import collections;print(len(out),collections.Counter((o['store'],o['sub_brand']) for o in out))
print([o['url'] for o in out[:2]])
