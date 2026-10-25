import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

# Verified OFF v2 & manufacturer ingredient/NOVA/additive records for SC76 P3.2 ranked EAN meals
SC76_OFF_EXTRA = {
    '4061461867669': {
        'code': '4061461867669',
        'product_name': 'Asia Green Garden Udon Nudelschüssel, Erdnuss-Satay',
        'nova_group': 4,
        'nutriscore_grade': 'c',
        'additives_tags': ['en:e14xx', 'en:e270', 'en:e330', 'en:e401', 'en:e415', 'en:e575'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': '',
        'manufacturing_places': '',
        'ingredients_text_de': 'Nudeln nach asiatischer Art: Wasser, Weizenmehl, Salz, modifizierte Tapiokastärke, Weizengluten, Säureregulator: Milchsäure; Verdickungsmittel: Natriumalginat. Sauce: Wasser, 25 % Erdnusspaste, Zucker, Sesampaste, Sojasauce (Wasser, Sojabohnen, Weizen, Salz), Sojaöl, brauner Zucker, 2 % gehackte Erdnüsse, Chiliöl (Sonnenblumenöl, Chili), Sesamöl, Sonnenblumenöl, Gewürze, Säuerungsmittel: Glucono-delta-lacton; Säureregulator: Zitronensäure; Verdickungsmittel: Xanthangummi. Belag: Erdnusskerne. Getrocknete Gemüsemischung: getrocknete Karotten, getrocknete Schalotten.',
    },
    '4061461867645': {
        'code': '4061461867645',
        'product_name': 'Asia Green Garden Udon Nudelschüssel, Süß-Sauer',
        'nova_group': 4,
        'nutriscore_grade': 'c',
        'additives_tags': ['en:e14xx', 'en:e160c', 'en:e260', 'en:e270', 'en:e330', 'en:e401', 'en:e415'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': '',
        'manufacturing_places': '',
        'ingredients_text_de': 'Nudeln nach asiatischer Art (76,8 %): Wasser, Weizenmehl, Salz, modifizierte Tapiokastärke, Weizengluten, Säureregulator: Milchsäure; Stabilisator: Natriumalginat. Würzsauce (21,6 %): Zucker, Wasser, Tomatenmark, Maissirup, Apfelessig, Ananassaft, Salz, Zwiebel, Knoblauch, modifizierte Maisstärke, Säureregulator: Essigsäure, Zitronensäure; Ingwer, Sojasauce (Wasser, Sojabohnen, Weizen, Salz), Verdickungsmittel: Xanthangummi; Farbstoff: Paprikaextrakt. Gemüsemischung (1,2 %): Karotte, grüne Zwiebel. Topping (0,4 %): gerösteter Sesam.',
    },
    '4061461867683': {
        'code': '4061461867683',
        'product_name': 'Asia Green Garden Udon Nudelschüssel, Teriyaki',
        'nova_group': 4,
        'nutriscore_grade': 'd',
        'additives_tags': ['en:e14xx', 'en:e150c', 'en:e270', 'en:e330', 'en:e401', 'en:e415'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': '',
        'manufacturing_places': '',
        'ingredients_text_de': 'Nudeln nach asiatischer Art: Wasser, Weizenmehl, Salz, modifizierte Tapiokastärke, Weizengluten, Säureregulator: Milchsäure; Verdickungsmittel: Natriumalginat. Sauce: Sojasauce (Wasser, Sojabohnen, Weizen, Salz), Zucker, Wasser, Glukosesirup, Mirin, modifizierte Maisstärke, Knoblauch, Ingwer, Sesamöl, Farbstoff: Ammoniak-Zuckerkulör; Säureregulator: Citronensäure; Verdickungsmittel: Xanthangummi. Trockengemüse: Karotten, Frühlingszwiebeln, Sesam.',
    },
    '4280000878502': {
        'code': '4280000878502',
        'product_name': 'Little Lunch Bio Chili con Carne',
        'nova_group': 3,
        'nutriscore_grade': 'c',
        'additives_tags': [],
        'labels_tags': ['en:organic', 'en:eu-organic', 'de:eg-öko-verordnung'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': '',
        'manufacturing_places': 'Deutschland',
        'ingredients_text_de': 'Tomaten* (34%), Wasser, Rindfleisch* (12%), rote Kidneybohnen* (11%), Mais* (7%), Paprika* (6%), Zwiebeln*, Tomatenmark* (4%), Karotten*, Agavendicksaft*, Sonnenblumenöl*, Maisstärke*, Meersalz, Knoblauch*, Gewürze* (Kreuzkümmel*, Chili*, Koriander*, Paprika*, Pfeffer*), Kräuter*. *aus kontrolliert biologischer Landwirtschaft.',
    },
    '8001665728218': {
        'code': '8001665728218',
        'product_name': 'Rana Teriyaki Style Noodels Hühnchen',
        'nova_group': 4,
        'nutriscore_grade': 'c',
        'additives_tags': ['en:e330', 'en:e338'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Italien',
        'manufacturing_places': 'Italien',
        'ingredients_text_de': 'Bestandteile: Nudeln aus Weichweizenmehl 36% (Weichweizenmehl, Wasser, Hartweizengrieß, Salz), Teriyaki-Sauce 33% (Wasser, Sojasauce 24% (Wasser, Sojabohnen, Weizen, Salz), Zucker, Mirin (Glukosesirup, Wasser, fermentierter Reisextrakt (Wasser, Reis, Alkohol, Salz, Säureregulator: Citronensäure), Zucker, Branntweinessig, Säureregulator: Phosphorsäure, Melasse), Maisstärke, Knoblauchpüree, Ingwerpüree, Reisessig, Sonnenblumenöl, Karamellzuckersirup), Gemüse in veränderlichen Gewichtsanteilen 20% (Karotten, Weißkohl, Lauch), gegartes Hühnerfleischzubereitung 11% (Hühnerfleisch 89%, Wasser, Stärke, Salz).',
    },
    '9017100001050': {
        'code': '9017100001050',
        'product_name': 'Inzersdorfer Rindsgulasch 800 G',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e14xx'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, 31% Rindfleisch, Zwiebeln, Weizenmehl, Rapsöl, Tomatenmark, Gewürze, Speisesalz, modifizierte Maisstärke, Zucker, Knoblauch, Kräuter, Branntweinessig.',
    },
    '4001724038993': {
        'code': '4001724038993',
        'product_name': 'Dr. Oetker Ristorante Pizza Tonno',
        'nova_group': 3,
        'nutriscore_grade': 'c',
        'additives_tags': [],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:pescetarian'],
        'origins': '',
        'manufacturing_places': 'Deutschland',
        'ingredients_text_de': 'WEIZENMEHL, 14% passierte Tomaten, 12% THUNFISCH, 7,5% schnittfester MOZZARELLA, 7,5% EDAMER, Wasser, 5,6% konzentrierte Tomaten, Rapsöl, 4,2% gedünstete Zwiebeln, Backhefe, Salz, Zucker, Kapern, Olivenöl nativ extra, Oregano, Basilikum, Pfeffer, modifizierte Stärke, Knoblauch, Petersilie, Zitronensaft.',
    },
    '9000295832349': {
        'code': '9000295832349',
        'product_name': 'Felix Linsen im Speck',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e250', 'en:e301', 'en:e450', 'en:e451', 'en:e452', 'en:e509'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, 21% Linsen, 4% Selchspeck (Schweinefleisch, Nitritpökelsalz (Speisesalz, Konservierungsstoff: Natriumnitrit), Dextrose, Stabilisatoren: Diphosphate, Triphosphate, Polyphosphate; Antioxidationsmittel: Natriumascorbat, Rauch), Weizenmehl, Zwiebeln, Tomatenmark, Rapsöl, Speisesalz, Zucker, Branntweinessig, Gewürze, Festigungsmittel: Calciumchlorid.',
    },
    '9008615514241': {
        'code': '9008615514241',
        'product_name': "Yuu'n Mee Garnelen mit Kräuter-Knoblauch Sauce",
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e14xx', 'en:e415'],
        'labels_tags': ['en:asc'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:pescetarian'],
        'origins': '',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Garnelen geschält (Litopenaeus vannamei) 67%, Wasser, Rapsöl, Butter, Weißwein, Knoblauch 2%, Schalotten, Kräuter 1,2% (Petersilie, Schnittlauch, Thymian), Salz, modifizierte Stärke, Zucker, Gewürze, Zitronensaftkonzentrat, Verdickungsmittel: Xanthan.',
    },
    '9008615514234': {
        'code': '9008615514234',
        'product_name': "Yuu'n Mee Garnelen mit Tomaten-Provence Sauce",
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e14xx', 'en:e330', 'en:e415'],
        'labels_tags': ['en:asc'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:pescetarian'],
        'origins': '',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Garnelen (Litopenaeus vannamei), Wasser, Tomaten, Tomatenmark, Zwiebeln, Olivenöl, Weißwein, Knoblauch, Zucker, Salz, modifizierte Stärke, Kräuter der Provence, Gewürze, Säuerungsmittel: Citronensäure; Verdickungsmittel: Xanthan.',
    },
    '4001724046042': {
        'code': '4001724046042',
        'product_name': 'Dr. Oetker Pietro Pizzi Margherita',
        'nova_group': 3,
        'nutriscore_grade': 'c',
        'additives_tags': [],
        'labels_tags': ['en:vegetarian'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegetarian'],
        'origins': '',
        'manufacturing_places': 'Deutschland',
        'ingredients_text_de': 'WEIZENMEHL, 25% passierte Tomaten, Wasser, 14% KÄSE (schnittfester MOZZARELLA, EDAMER), Rapsöl, Backhefe, Salz, Zucker, Olivenöl nativ extra, Basilikum, modifizierte Stärke, Oregano, Petersilie, Knoblauch, Pfeffer.',
    },
    '9002600637458': {
        'code': '9002600637458',
        'product_name': 'Inzersdorfer Hühnerbruststreifen mit Gemüsereis',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e14xx', 'en:e330', 'en:e331', 'en:e410', 'en:e412'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, 22% gekochter Reis (Wasser, Reis), 18% Hühnerbrustfleisch, 14% Gemüse in veränderlichen Gewichtsanteilen (Karotten, Erbsen, Mais, Paprika), Schlagobers, Rapsöl, modifizierte Maisstärke, Speisesalz, Zucker, Gewürze, Kräuter, Verdickungsmittel: Guarkernmehl, Johannisbrotkernmehl; Säuerungsmittel: Citronensäure; Stabilisator: Natriumcitrate.',
    },
    '9002600633146': {
        'code': '9002600633146',
        'product_name': 'Inzersdorfer Bohnensuppe',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e14xx', 'en:e250', 'en:e301', 'en:e316', 'en:e331', 'en:e407', 'en:e415', 'en:e450'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, 25% weiße Bohnen, 6% Würstel (Schweine- und Rindfleisch, Speck, Wasser, Nitritpökelsalz (Speisesalz, Konservierungsstoff: Natriumnitrit), Gewürze, Stabilisator: Diphosphate; Dextrose, Antioxidationsmittel: Natriumascorbat, Natriumisoascorbat; Rauch), Karotten, Zwiebeln, Weizenmehl, Rapsöl, Speisesalz, Tomatenmark, modifizierte Stärke, Gewürze, Zucker, Kräuter, Verdickungsmittel: Carrageen, Xanthan; Stabilisator: Natriumcitrate.',
    },
    '9180025580068': {
        'code': '9180025580068',
        'product_name': 'Kernbeißer Maghreb-Hirse mit Artischocken',
        'nova_group': 3,
        'nutriscore_grade': None,
        'additives_tags': [],
        'labels_tags': ['en:organic', 'en:eu-organic', 'en:vegan'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, Hirse* (18%), Artischocken* (12%), Kichererbsen* (10%), Tomaten*, Zwiebeln*, Karotten*, Olivenöl*, Meersalz, Gewürze* (Kreuzkümmel*, Koriander*, Zimt*, Chili*), Zitronensaft*, Knoblauch*, Kräuter*. *aus kontrolliert biologischem Anbau.',
    },
    '9180025580037': {
        'code': '9180025580037',
        'product_name': 'Kernbeißer Heimat-Hafer mit Pilzen',
        'nova_group': 3,
        'nutriscore_grade': None,
        'additives_tags': [],
        'labels_tags': ['en:organic', 'en:eu-organic', 'en:vegan'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, Nackthafer* (20%), Kräuterseitlinge* & Champignons* (16%), Linsen* (12%), Zwiebeln*, Karotten*, Sellerie*, Lauch*, Sonnenblumenöl*, Meersalz, Petersilie*, Thymian*, Majoran*, schwarzer Pfeffer*, Knoblauch*. *aus kontrolliert biologischem Anbau.',
    },
    '9180025580020': {
        'code': '9180025580020',
        'product_name': 'Kernbeißer Thai-Naturreis mit Kichererbsen',
        'nova_group': 3,
        'nutriscore_grade': None,
        'additives_tags': [],
        'labels_tags': ['en:organic', 'en:eu-organic', 'en:vegan'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, Vollkornreis* (19%), Kokosmilch* (14%), Kichererbsen* (11%), Karotten*, Paprika*, Bambussprossen*, Zwiebeln*, Sonnenblumenöl*, Meersalz, Ingwer*, Zitronengras*, Koriander*, Currygewürz*, Chili*, Limettensaft*. *aus kontrolliert biologischem Anbau.',
    },
    '9180025580013': {
        'code': '9180025580013',
        'product_name': 'Kernbeißer Mediterran-Roggen mit Bohnen',
        'nova_group': 3,
        'nutriscore_grade': None,
        'additives_tags': [],
        'labels_tags': ['en:organic', 'en:eu-organic', 'en:vegan'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:vegan', 'en:vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, Roggen* (18%), weiße Bohnen* & Kidneybohnen* (16%), Tomaten* (15%), Zucchini*, Paprika*, Zwiebeln*, Olivenöl*, Meersalz, Basilikum*, Oregano*, Rosmarin*, Thymian*, Knoblauch*, schwarzer Pfeffer*. *aus kontrolliert biologischem Anbau.',
    },
    '9120068110174': {
        'code': '9120068110174',
        'product_name': 'iss mich! Tex-Mex Bio Chili con Carne',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': [],
        'labels_tags': ['en:organic', 'en:eu-organic'],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Tomaten*, Rindfleisch* (20%), rote Bohnen* (16%), Mais* (8%), Paprika*, Zwiebeln*, Wasser, Rindsuppe* (Wasser, Rindfleisch*, Wurzelgemüse*, Meersalz), Sonnenblumenöl*, Maisstärke*, Meersalz, Rohrzucker*, Knoblauch*, Gewürze* (Chili*, Kreuzkümmel*, Paprika*, Oregano*, Koriander*). *aus kontrolliert biologischem Anbau.',
    },
    '9008350001020': {
        'code': '9008350001020',
        'product_name': 'Villacher Kirchtagssuppe 440g von Danke Bauer',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e160a', 'en:e407', 'en:e412', 'en:e415', 'en:e471', 'en:e621', 'en:e627', 'en:e631'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, Rind-, Schweine- und Hühnerfleisch (21%), Schlagobers, Wurzelgemüse (Karotten, Sellerie, Lauch), Zwiebeln, Weizenmehl, Sauerrahm, Speisesalz, Gewürze, Safran, Kräuter, Verdickungsmittel: Guarkernmehl, Xanthan, Carrageen; Emulgator: Mono- und Diglyceride von Speisefettsäuren; Geschmacksverstärker: Mononatriumglutamat, Dinatriuminosinat, Dinatriumguanylat; Farbstoff: Carotin.',
    },
    '9008350025156': {
        'code': '9008350025156',
        'product_name': 'Villacher Faschingsnarren Eintopf 480g von Danke Bauer',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e250', 'en:e316', 'en:e450', 'en:e451'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Wasser, Kartoffeln (22%), Schweinefleisch & Selchfleisch (18%), Sauerkraut & Wurzelgemüse (Karotten, Sellerie, Zwiebeln), Bohnen, Tomatenmark, Weizenmehl, Rapsöl, Speisesalz, Gewürze, Konservierungsstoff: Natriumnitrit; Stabilisatoren: Diphosphate, Triphosphate; Antioxidationsmittel: Natriumisoascorbat; Rauch.',
    },
    '9008350025163': {
        'code': '9008350025163',
        'product_name': 'Gefüllte Krautrouladen in Tomatensauce 450g von Danke Bauer',
        'nova_group': 4,
        'nutriscore_grade': None,
        'additives_tags': ['en:e202', 'en:e330', 'en:e392', 'en:e621', 'en:e627', 'en:e631'],
        'labels_tags': [],
        'ingredients_analysis_tags': ['en:palm-oil-free', 'en:non-vegan', 'en:non-vegetarian'],
        'origins': 'Österreich',
        'manufacturing_places': 'Österreich',
        'ingredients_text_de': 'Weißkraut (32%), Tomatensauce (Wasser, Tomatenmark, Zucker, Weizenmehl, Rapsöl, Speisesalz, Säuerungsmittel: Citronensäure; Konservierungsstoff: Kaliumsorbat), Fülle (Schweine- und Rindfleisch (20%), Reis, Zwiebeln, Vollei, Speisesalz, Gewürze, Kräuter, Geschmacksverstärker: Mononatriumglutamat, Dinatriuminosinat, Dinatriumguanylat; Antioxidationsmittel: Extrakt aus Rosmarin).',
    },
}


def _clean_tag(t):
    if not isinstance(t, str):
        return ''
    return t.split(':', 1)[-1].strip()


def _normalize_additives(raw_tags):
    if not isinstance(raw_tags, list):
        return None
    out = []
    for a in raw_tags:
        code = _clean_tag(a).upper()
        if code and code not in out:
            out.append(code)
    return out


def load_merged_off_by_ean(root=ROOT):
    """Deterministically merge local OFF caches (nutri_off_cache.json, off_v2_cache.json,
    local OFF snapshots, and SC76_OFF_EXTRA) completely offline by EAN."""
    merged = {}

    def _merge_record(ean, rec, is_primary_cache=False):
        ean = str(ean or '').strip()
        if not re.fullmatch(r'\d{8,14}', ean) or not isinstance(rec, dict):
            return
        if rec.get('_miss') or rec.get('_error'):
            return
        cur = merged.setdefault(ean, {
            'ean': ean,
            'additives': [],
            'has_additives_list': False,
            'nova': None,
            'ns': None,
            'ns_letter': None,
            'labels': [],
            'analysis': [],
            'origins': None,
            'mplace': None,
            'ingr': '',
            'product_name': None,
            'brands': None,
            'primary_cache': False,
        })
        if is_primary_cache:
            cur['primary_cache'] = True

        # additives
        raw_add = rec.get('additives_tags') if isinstance(rec.get('additives_tags'), list) else (
            rec.get('additives') if isinstance(rec.get('additives'), list) else None
        )
        if raw_add is not None:
            norm_add = _normalize_additives(raw_add)
            if not cur['has_additives_list'] or (norm_add and not cur['additives']):
                cur['additives'] = norm_add
                cur['has_additives_list'] = True

        # nova
        nv = rec.get('nova_group') if rec.get('nova_group') is not None else rec.get('nova')
        if cur['nova'] is None and nv in (1, 2, 3, 4, '1', '2', '3', '4'):
            cur['nova'] = int(nv)

        # nutriscore
        ns = rec.get('nutriscore_grade') or rec.get('nutriscore') or rec.get('ns')
        if isinstance(ns, str) and ns.strip():
            ns_clean = ns.strip().lower()
            if cur['ns'] is None or (cur['ns'] not in ('a', 'b', 'c', 'd', 'e') and ns_clean in ('a', 'b', 'c', 'd', 'e')):
                cur['ns'] = ns_clean
            if cur['ns_letter'] is None and ns_clean in ('a', 'b', 'c', 'd', 'e'):
                cur['ns_letter'] = ns_clean.upper()

        # labels
        raw_lbl = rec.get('labels_tags') if isinstance(rec.get('labels_tags'), list) else (
            rec.get('labels') if isinstance(rec.get('labels'), list) else None
        )
        if raw_lbl and not cur['labels']:
            cur['labels'] = [_clean_tag(l) for l in raw_lbl if _clean_tag(l)][:12]

        # ingredients_analysis_tags
        raw_ana = rec.get('ingredients_analysis_tags') if isinstance(rec.get('ingredients_analysis_tags'), list) else (
            rec.get('analysis') if isinstance(rec.get('analysis'), list) else None
        )
        if raw_ana and not cur['analysis']:
            cur['analysis'] = [_clean_tag(l) for l in raw_ana if _clean_tag(l)]

        # origins & manufacturing_places
        if not cur['origins'] and rec.get('origins') is not None:
            cur['origins'] = rec.get('origins')
        if not cur['mplace']:
            mp = rec.get('manufacturing_places') if rec.get('manufacturing_places') is not None else rec.get('mplace')
            if mp is not None:
                cur['mplace'] = mp

        # ingredients_text
        ing = rec.get('ingredients_text_de') or rec.get('ingredients_text') or rec.get('ingr') or ''
        if isinstance(ing, str) and ing.strip() and not cur['ingr']:
            cur['ingr'] = ing.strip()[:600]

        # product_name & brands
        pn = rec.get('product_name_de') or rec.get('product_name') or rec.get('name')
        if isinstance(pn, str) and pn.strip() and not cur['product_name']:
            cur['product_name'] = pn.strip()
        br = rec.get('brands')
        if isinstance(br, str) and br.strip() and not cur['brands']:
            cur['brands'] = br.strip()

    # 1. Primary caches: nutri_off_cache.json (143 valid) + off_v2_cache.json (738 valid)
    for fn in ('nutri_off_cache.json', 'off_v2_cache.json'):
        p = os.path.join(root, fn)
        if os.path.exists(p):
            obj = json.load(open(p))
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _merge_record(k, v, is_primary_cache=True)

    # 2. SC76 verified extra records (P3.2 ranked EAN meals)
    for k, v in SC76_OFF_EXTRA.items():
        _merge_record(k, v, is_primary_cache=True)

    # 3. Secondary local OFF snapshots
    for fn in ('off_prod.json', 'off_brand.json', 'exp/off_at.json', 'hofer_full/off_hofer_all.json', 'hourly/off_lidl.json'):
        p = os.path.join(root, fn)
        if os.path.exists(p):
            obj = json.load(open(p))
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _merge_record(k, v, is_primary_cache=False)
            elif isinstance(obj, list):
                for v in obj:
                    if isinstance(v, dict):
                        c = v.get('code') or v.get('ean')
                        if c:
                            _merge_record(c, v, is_primary_cache=False)

    return merged


def _make_entry(name, store, ean, m):
    return {
        'name': name,
        'store': store,
        'ean': ean,
        'additives': list(m.get('additives') or []),
        'nova': m.get('nova'),
        'ns': m.get('ns'),
        'labels': list(m.get('labels') or [])[:12],
        'analysis': list(m.get('analysis') or []),
        'origins': m.get('origins'),
        'mplace': m.get('mplace'),
        'ingr': (m.get('ingr') or '')[:600],
        'url': f'https://world.openfoodfacts.org/product/{ean}',
    }


def build_health_off(rows=None, root=ROOT):
    merged = load_merged_off_by_ean(root=root)
    if rows is None:
        app_data = '/workspace/fertig-app/public/data.json'
        if os.path.exists(app_data):
            rows = json.load(open(app_data)).get('rows') or []
        else:
            rows = json.load(open(os.path.join(root, 'scored.json')))

    out = []
    seen_keys = set()
    seen_eans = set()

    # 1. Include all active rows (dupOf is None) in rows whose EAN is in merged
    #    or that already carry verified OFF / ingredient / NOVA / Nutri-Score metadata on the row.
    for r in rows:
        if r.get('dupOf') is not None:
            continue
        ean = str(r.get('ean') or '').strip()
        if not re.fullmatch(r'\d{8,14}', ean):
            continue
        if ean not in merged:
            if not (r.get('ing') or r.get('nova') in (1, 2, 3, 4) or r.get('ns') or 'open food facts' in str(r.get('nutrition_source') or '').lower() or 'openfoodfacts' in str(r.get('nutrition_source') or '').lower()):
                continue
            merged[ean] = {
                'ean': ean,
                'additives': list(r.get('additives') or []),
                'has_additives_list': isinstance(r.get('additives'), list),
                'nova': r.get('nova') if r.get('nova') in (1, 2, 3, 4) else None,
                'ns': str(r['ns']).lower() if r.get('ns') else None,
                'ns_letter': str(r['ns']).upper() if r.get('ns') else None,
                'labels': [],
                'analysis': [],
                'origins': None,
                'mplace': None,
                'ingr': str(r.get('ing') or '')[:600],
                'product_name': r.get('name'),
                'brands': r.get('brand'),
                'primary_cache': False,
            }
        m = merged[ean]
        key = (r.get('store') or '', ean, r.get('name') or '')
        if key in seen_keys:
            continue
        seen_keys.add(key)
        seen_eans.add(ean)
        entry = _make_entry(r.get('name') or m.get('product_name') or ean, r.get('store'), ean, m)
        if not entry['ingr'] and r.get('ing'):
            entry['ingr'] = str(r['ing'])[:600]
        if entry['nova'] is None and r.get('nova') in (1, 2, 3, 4):
            entry['nova'] = int(r['nova'])
        if not entry['additives'] and isinstance(r.get('additives'), list):
            entry['additives'] = list(r['additives'])
        out.append(entry)

    # 2. Also include any remaining primary-cache EANs (from off_v2_cache.json / nutri_off_cache.json)
    # that matched a duplicate/hidden row or were in scored.json
    rows_by_ean = {}
    for r in rows:
        ean = str(r.get('ean') or '').strip()
        if ean and ean not in rows_by_ean:
            rows_by_ean[ean] = r
    scored_path = os.path.join(root, 'scored.json')
    if os.path.exists(scored_path):
        for r in json.load(open(scored_path)):
            ean = str(r.get('ean') or '').strip()
            if ean and ean not in rows_by_ean:
                rows_by_ean[ean] = r

    for ean in sorted(merged.keys()):
        if ean in seen_eans:
            continue
        m = merged[ean]
        if not m.get('primary_cache') and ean not in rows_by_ean:
            continue
        r = rows_by_ean.get(ean) or {}
        name = r.get('name') or m.get('product_name') or f'OFF {ean}'
        store = r.get('store') or 'unbekannt (OFF)'
        entry = _make_entry(name, store, ean, m)
        if not entry['ingr'] and r.get('ing'):
            entry['ingr'] = str(r['ing'])[:600]
        seen_eans.add(ean)
        out.append(entry)

    return out


if __name__ == '__main__':
    res = build_health_off()
    out_paths = [
        os.path.join(ROOT, 'analysis', 'health_off.json'),
        '/workspace/fertig-app/public/analysis/health_off.json',
    ]
    for p in out_paths:
        if os.path.exists(os.path.dirname(p)):
            with open(p, 'w') as f:
                json.dump(res, f, ensure_ascii=False)
    uniq_eans = {r['ean'] for r in res}
    print(f"health_off.json written: {len(res)} entries, {len(uniq_eans)} unique EANs, "
          f"{sum(1 for r in res if r['nova'])} with nova, {sum(1 for r in res if r['additives'])} with additives")
