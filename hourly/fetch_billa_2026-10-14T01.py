# hourly T01: BILLA search with stems less used in T00 / focus on heat-up meals not yet present
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if str(x.get('store') or '').upper()=='BILLA'}
Q=["backhendlstreifen","kaiserschmarrn","kaiserschmarren","germknödel","mohnnudeln","spaghetteria","ristorante hawaii","steinofen pizza","piccolinis mozzarella","seelachs schnitzel","dorsch paniert","scholle paniert","polardorsch","cornflakesstäbchen","leitschwendt","streetfood curry","air fryer chicken","heura burger","udon nudeln","eierspätzle","mozzarella sticks","linsenburger","dinkel tortelloni","pizza minis","chili con carne bio","rindsgulasch dose","karottensuppe","gemüsenudelsuppe","tomatencremesuppe","risotto funghi","wagner diavolo","frosta fisch","iglo scholle","iglo dorsch","jeden tag wings","jeden tag mozzarella","followfood","rebel meat","hubers landhendl","vegavita","beda ford","bedford","die pflanzerei","yuu n mee","dozz","apetito","costa prawns","schlemmerfilet","ofengarnelen","backteig","knusperfilet","fischfrikadellen","thunfisch pasta","lachs pasta","putengeschnetzeltes","schweinebraten","tafelspitz fertig","beuschel","fiaker gulasch","szegediner","kohlrouladen","gefüllte paprika","spinatknödel","käsespätzle","tiroler gröstl","krautfleckerl","wurstnudeln","pelmeni","pierogi","wareniki","gyoza vegetarisch","frühlingsrollen","dim sum","nasi goreng","bami goreng","pad thai fertig","butter chicken fertig","tikka masala fertig","massaman","tom kha","pho bo","ramen fertig","laksa","jambalaya","paella fertig","moussaka fertig","cannelloni fertig","quesadilla","enchilada fertig","burrito bowl","chili sin carne","ratatouille fertig","cassoulet","bouillabaisse","minestrone dose","hühnersuppe dose","gulaschsuppe dose","erbsensuppe dose","linseneintopf","kartoffelsuppe","kürbiscremesuppe","broccolicremesuppe"]
b=Billa(); out=[]; seen=set()
for q in Q:
    try: ps=b.search(q,80)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.25)
json.dump([p.__dict__ for p in out],open('/tmp/h01/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('TOTAL',len(out))
for p in out: print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category)
