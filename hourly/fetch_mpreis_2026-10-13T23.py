# hourly T23: MPreis sitemap (robots-allowed product pages, JSON-LD offer + Nährwerte tab) — hand-picked heat-up meal slugs whose SKU is not yet in scored/connectors_new
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import mpreis_shop as M
SLUGS="""alnatura-bio-gemuesenudelsuppe-365204 alnatura-bio-tomaten-cremesuppe-365205 alnatura-bowl-nach-mediterraner-art-365944 alnatura-bowl-nach-mexikanischer-art-365790
iglo-crispy-chicken-rosmarin-meersalz-820540 costa-garnelenpfanne-knoblauch-815188 alnatura-huehner-nudel-suppe-366299 alnatura-kartoffel-lauch-suppe-366300
kaesespaetzle-899416 kaspress-knoedel-mit-kraut-899436 iglo-knusprige-ofengarnelen-813376 jeden-tag-lasagne-145786 iglo-lasagne-al-forno-804982 jeden-tag-lasagne-bolognese-611543
mini-huehnerschnitzel-gebacken-tk-846120 costa-ofenfisch-bordelaise-msc-813759 costa-ofenfrisch-tomate-spinat-alaska-msc-813754 omas-faschierte-laibchen-80120
inzersdorfer-rindsgulasch-226502 bens-original-express-risotto-296774 streetfood-thai-green-curry-133557 auinger-zwergerlsuppe-259423 auinger-klare-suppe-259421
dahlhoff-feinkost-garnelen-thai-curry-asc-233136 jeden-tag-chili-cheese-nuggets-812102 jeden-tag-chicken-wings-812011 11er-selection-chicken-fries-812124 stritzinger-chicken-frites-80186
fjordgold-alaska-seelachs-schnitzel-81219 pierre-baguette-gyros-baguette-770186 pierre-baguette-huehner-strips-scharf-770159 pierre-baguette-baguette-debrecen-baguette-770154
jeden-tag-schinken-baguette-6er-packung-809410 alnatura-pizza-minis-365847 alnatura-tortellini-gemuese-366198 bio-vom-berg-tiroler-jungrind-gulasch-733302 knorr-bitte-zu-tisch-huehnersuppe-278790
knorr-bitte-zu-tisch-nudelsuppe-277602 knorr-bitte-zu-tisch-fleischkloesschensuppe-278404 knorr-bitte-zu-tisch-griessnockerlsuppe-278700 jeden-tag-chicken-dip-812171""".split()
out=[]
for s in SLUGS:
    u='https://www.mpreis.at/shop/p/'+s
    try: p=M.product(u)
    except Exception as e: print('ERR',s,str(e)[:80],flush=True); continue
    time.sleep(0.5)
    if not p: print('NONE',s,flush=True); continue
    out.append(p.__dict__)
    print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:40].replace('\n',' '),'|',(p.extra or {}).get('availability'),flush=True)
json.dump(out,open('hourly/cand_mpreis_2026-10-13T23.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
