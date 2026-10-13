import json
L='logos/'
def sb(name,pat,logo=None,typ=None,src=None):return dict(name=name,pattern=pat,logo=logo,logo_type=typ,logo_source=src)
OFF='offiziell (Markenseite)';PK='aus Packung'
F=[
 dict(id='hofer',name='HOFER',chain='HOFER',logo=L+'hofer.svg',sub_brands=[
  sb('Good Choice',r'good choice'),sb('Primana',r'primana',L+'primana.png',PK,'hofer.at Produktfoto Primana Frühstücksfleisch'),
  sb("Leibspeis'",r'leibspeis'),sb('Cucina',r'cucina',L+'cucina.png',OFF,'hofer.at/marken/cucina'),
  sb('Asia Green Garden',r'asia green garden',L+'asia-green-garden.png',PK,'hofer.at Produktfoto Asia Green Garden Pilztopf'),
  sb('Gourmet',r'^gourmet|gourmet finest',L+'hofer-gourmet.png',OFF,'hofer.at Markenlogo GOURMET'),
  sb('Le Gusto',r'le gusto',L+'le-gusto.png',OFF,'hofer.at Markenlogo'),sb("Nature's Gold",r"nature.?s gold"),
  sb('Zurück zum Ursprung',r'zurück zum ursprung',L+'zurueck-zum-ursprung.png',PK,'hofer.at Produktfoto ZZU Käferbohnen'),
  sb('Just Veg',r'just veg'),sb('Enjoy Free',r'enjoy free')]),
 dict(id='billa',name='BILLA (REWE)',chain='BILLA',logo=L+'billa.svg',sub_brands=[
  sb('Clever',r'^clever',L+'clever.png',OFF,'billa.at Eigenmarken'),sb('Billa Immer Gut',r'immer gut',L+'immer-gut.png',OFF,'billa.at Eigenmarken'),
  sb('Simply Good',r'simply good',L+'simply-good.png',OFF,'billa.at Eigenmarken'),sb('Omis Schmankerl',r'omis',L+'omis-schmankerl.png',OFF,'billa.at Eigenmarken'),
  sb('Billa Bio',r'billa bio',L+'billa-bio.png',OFF,'billa.at Eigenmarken'),sb('Ja! Natürlich',r'ja!? ?nat',L+'ja-natuerlich.svg',OFF,'Wikimedia/ja-natuerlich.at'),
  sb('Billa Genusswelt',r'genusswelt',L+'billa-genusswelt.png',OFF,'billa.at Eigenmarken'),sb('Vegavita',r'vegavita',L+'vegavita.png',OFF,'billa.at Eigenmarken'),
  sb('Corso',r'^corso')]),
 dict(id='spar',name='SPAR',chain='SPAR',logo=L+'spar.svg',sub_brands=[
  sb('S-Budget',r's-budget',L+'s-budget.png',OFF,'spar.at Eigenmarken'),sb('Spar Feine Küche',r'feine küche',L+'spar-feine-kueche.png',OFF,'spar.at Eigenmarken'),
  sb('Spar Premium',r'spar premium',L+'spar-premium.png',OFF,'spar.at Eigenmarken'),sb('Spar Natur*pur',r'natur\*?pur',L+'spar-natur-pur.png',OFF,'spar.at Eigenmarken'),
  sb('Spar Veggie',r'spar veggie',L+'spar-veggie.png',OFF,'spar.at Eigenmarken'),sb('Spar enjoy',r'spar enjoy'),sb('Spar Vital',r'spar vital',L+'spar-vital.png',OFF,'spar.at Eigenmarken'),
  sb('Despar',r'despar',L+'despar.png',OFF,'spar.at')]),
 dict(id='lidl',name='LIDL',chain='LIDL',logo=L+'lidl.svg',sub_brands=[sb('Chef Select',r'chef select'),sb('Vemondo',r'vemondo'),sb('Deluxe',r'deluxe'),sb('Vitasia',r'vitasia'),sb('Kania',r'kania')]),
 dict(id='penny',name='PENNY (REWE)',chain='PENNY',logo=L+'penny.svg',sub_brands=[sb('Chef Menü',r'chef men'),sb('Food for Future',r'food for future',L+'food-for-future.svg',OFF,'penny.at')]),
]
json.dump(dict(version='2026-10-13',note='Markenfamilien: Kette -> Eigen-/Untermarken. Logos nur nach Vision Gate (qa/vision_gate.json). logo_type: offiziell oder aus Packung.',families=F),open('brand_families_def.json','w'),ensure_ascii=False,indent=1)
