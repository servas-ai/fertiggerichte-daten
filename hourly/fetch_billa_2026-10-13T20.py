# hourly T20 (2026-10-13T20): BILLA product-discovery search with new ready-meal stems; only items not yet in scored/connectors_new (url or name+store)
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if str(x.get('store') or '').upper()=='BILLA'}
Q=["tiefkühlgericht","tk gericht","tk menü","mikrowellengericht","nudelgericht","reisgericht","asia gericht","asia pfanne","indisches gericht","thai curry","green curry","red curry","massaman","katsu","donburi","sushi","wonton","bao","baozi","pakora","poke","hummus","bolognese","carbonara","alfredo","pesto pasta","cannelloni tk","gratin","auflauf","fleischstrudel","topfenstrudel","mohnnudeln","marillenknödel","topfenknödel","buchteln","kasnocken","schlutzkrapfen","erdäpfelgulasch","fiakergulasch","szegediner","hirschgulasch","bohnengulasch","fisolen","gemüseeintopf","hühnerfrikassee","königsberger","rouladen","pulled pork","spare ribs","chicken","hendl","schnitzel","fischlaibchen","lachs","garnelen","paella","risotto","gnocchi","tortelloni","agnolotti","suppentopf","ramen","pho","miso","gazpacho","borschtsch","gulaschsuppe","leberknödelsuppe","erdäpfelsuppe","schwammerlsuppe","cremesuppe","brokkolisuppe","karottensuppe","süßkartoffel","linsensuppe","bohnensuppe","erbsensuppe","hühnersuppe","rindsuppe","dessert","pudding","mousse","tiramisu","panna cotta","grießschmarrn","kaiserschmarrn","palatschinken","crepes","milchreis","pizza","pizza tk","pizza familie","pizza mini","pizzabaguette","pizzaschnecke","flammkuchen","quiche","tarte","pastete","pie","lasagne","moussaka","burger","wrap","toast","sandwich","panini","focaccia","börek","burek","pita","gyros","kebab","cevapcici","sarma","djuvec","gulasch","chili","curry","eintopf","suppe","knödel","strudel","nockerl","spätzle","nudeln mit","reis mit","kartoffel mit","erdäpfel mit","gemüse mit","huhn mit","rind mit","schwein mit","fisch mit","vegan","vegetarisch","veggie","protein","high protein","bio gericht","ja natürlich","clever","billa gericht","billa bio","billa corso","billa immer gut","rewe","wagner","dr. oetker","iglo","frosta","bürger","maggi","knorr","erasco","felix","inzersdorfer","hengstenberg","sonnen bassermann","natur aktiv","mama mancini","garden gourmet","like meat","rügenwalder","planted","beyond","vegini","gustavo gusto","ristorante","la mia","culinaria","steinofen","big pizza","piccolinis","speciale","deliciosu","youcook","dean david","freshfood","nanu","develey","greisinger","hütthaler","wiesbauer","handl","stastnik","senna","hofmann","gourmet","menü","kalbsrahm","geschnetzeltes","stroganoff","ragout","frikassee","beuschel","bruckfleisch","fleischlaibchen","faschiertes","hackbraten","schweinsbraten","stelze","ripperl","bratwurst","käsekrainer","leberkäse","blunzen","grammel","speck","schinkenfleckerl","krautfleckerl","eiernockerl","topfennockerl","käsespätzle","spinatspätzle","maultaschen","ravioli","tortellini","gnocchi"]
out=[]; seen=set(); b=Billa()
for q in Q:
    try: ps=b.search(q,100)
    except Exception as e: print('ERR',q,e); time.sleep(1); continue
    n=0
    for p in ps:
        if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
        seen.add(p.source_id); out.append(p.__dict__); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.3)
json.dump(out,open('/tmp/h20/billa_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
