# hourly T01: fetch hand-picked MPreis heat-up meal slugs from sitemap gap
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
SLUGS="""iglo-backhendlstreifen-804935 iglo-backhendlstreifen-kuerbiskern-809027
toni-kaiser-wiener-kaiserschmarren-810166 leitschwendt-bio-chili-con-carne-606526
inzersdorfer-rindsgulasch-226502 dr-oetker-ristorante-hawaii-805014
wagner-steinofen-diavolo-pizza-803234 wagner-piccolinis-tomate-mozzarella-pizza-802223
streetfood-thai-green-curry-133557 frosta-cornflakes-staebchen-msc-814504
iglo-dorsch-paniert-msc-805610 iglo-dorsch-in-knusperbroesel-msc-815069
iglo-polardorsch-paniert-msc-805660 iglo-polardorsch-muellerin-msc-805284
iglo-polardorsch-mediterrane-art-msc-804923 iglo-polardorsch-serbische-art-msc-805269
iglo-scholle-paniert-msc-811848 iglo-scholle-muellerin-die-verfeinerte-811846
fjordgold-alaska-seelachs-schnitzel-81219 knorr-spaghetteria-carbonara-292078
knorr-spaghetteria-pomodoro-mozzarella-fertiggericht-292010 knorr-spaghetteria-spinaci-fertiggericht-292006
alnatura-bio-tomaten-cremesuppe-365205 alnatura-bio-gemuesenudelsuppe-365204
frank-juice-bio-karotten-suppe-367104 stoppato-risotto-funghi-porcini-845098
maggi-air-fryer-chicken-cheesy-275303 maggi-air-fryer-chicken-paprika-275305
maggi-air-fryer-mexican-style-fajita-275304 wagner-air-fryer-mozzarella-814507
heura-burger-pflanzlich-611572 allgroo-udon-nudeln-meeresfruechte-186411
allgroo-udon-nudeln-miso-186407 allgroo-udon-nudeln-tofu-und-pilze-186408
strauss-eierspaetzle-611160 henglein-eierspaetzle-knoepfle-811410
jeden-tag-chicken-wings-812011 jeden-tag-crispy-mozzarella-sticks-mit-red-pepp-812294
jeden-tag-pizza-margherita-3er-packung-803726 alnatura-pizza-minis-365847
alnatura-bio-dinkel-tortelloni-ricotta-spinat-365310 alnatura-bio-rote-linsen-burger-365715
alnatura-vollkorn-verganer-burger-365194""".split()
out=[]
for s in SLUGS:
    u='https://www.mpreis.at/shop/p/'+s
    try: p=M.product(u)
    except Exception as e: print('ERR',s,str(e)[:100],flush=True); continue
    time.sleep(0.4)
    if not p: print('NONE',s,flush=True); continue
    out.append(p.__dict__)
    n=p.nutrition_100g or {}
    print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',p.ean,'|',(p.extra or {}).get('availability'),flush=True)
json.dump(out,open('hourly/cand_mpreis_2026-10-14T01.json','w'),ensure_ascii=False,default=str,indent=0)
print('fetched',len(out))
