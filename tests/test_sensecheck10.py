"""Sensecheck 10: wet ready meals mis-labeled Trocken/Instant (Knorr Meisterkessel / Inzersdorfer / Hink);
family-size Lasagne 700 g and 4× Haddock 500 g split into 2 portions; vorspeise soups out of main top lists."""
import os,re,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,ROOT)
import score_v2 as V

def _classify():
    import re as _re
    src=open(os.path.join(ROOT,'score.py')).read()
    ns={'re':_re}
    # classify lives between def classify and NOVA=
    a=src.index('def classify(x):'); b=src.index('\nNOVA=',a)
    exec(compile(src[a:b],'score.py','exec'),ns)
    return ns['classify']

def test_meisterkessel_dose_not_trocken():
    C=_classify()
    assert C(dict(name='Knorr Meisterkessel Chili Con Carne',brand='Knorr',category='Dose',prep='Mikrowelle, Topf'))=='Dose/Konserve'
    assert C(dict(name='Knorr Meister Kessel Rindsgulasch',brand='Knorr',category='Dose',prep='Mikrowelle, Topf'))=='Dose/Konserve'
    assert C(dict(name='Knorr Meisterkessel Bohnen-Speck Suppe',brand='Knorr',category='Dose'))=='Dose/Konserve'

def test_inzersdorfer_hink_beutel_retort():
    C=_classify()
    assert C(dict(name='Inzersdorfer Rahmschnitzel mit Spiralen',brand='Inzersdorfer',category='Beutel',prep='Mikrowelle, Wasserbad'))=='Beutel ungekühlt (Retort-Pouch)'
    assert C(dict(name='Inzersdorfer Zwiebelrindsbraten',brand='Inzersdorfer',category='Beutel'))=='Beutel ungekühlt (Retort-Pouch)'
    assert C(dict(name='Hink Wien Wiener Rindersaftgulasch',brand='Hink Wien',category='Beutel'))=='Beutel ungekühlt (Retort-Pouch)'

def test_dry_knorr_maggi_still_trocken():
    C=_classify()
    assert C(dict(name='Knorr Fix Gulasch',brand='Knorr',category='Trocken'))=='Trocken/Instant'
    assert C(dict(name='Knorr Beutelsuppe Tomate',brand='Knorr',category='Beutel'))=='Trocken/Instant'
    assert C(dict(name='Maggi Magic Asia Gebratene Nudeln Ente',brand='Maggi',category='Beutel'))=='Trocken/Instant'
    assert C(dict(name='Knorr Kaiserteller Grießnockerlsuppe',brand='Knorr',category='Trocken'))=='Trocken/Instant'

def test_family_pack_portions():
    assert V.portion(dict(name='Iglo Lasagne al Forno (tiefgekühlt)',size_g=700,packaging='Tiefkühl (TK)',kcal_100=124),None)==(350,'family_pack')
    assert V.portion(dict(name='Marks & Spencer 4 Breaded Haddock Fillets (tiefgekühlt)',size_g=500,packaging='Tiefkühl (TK)',kcal_100=174),None)==(250,'family_pack')
    # single pack stays pack_single
    assert V.portion(dict(name='Iglo Lasagne al Forno',size_g=350,packaging='Tiefkühl (TK)',kcal_100=160),None)==(350,'pack_single')

def test_top_lists_skip_vorspeise():
    src=open(os.path.join(ROOT,'export_app.py')).read()
    assert "gang')!='vorspeise'" in src or 'gang")!=\'vorspeise\'' in src or "get('gang')!='vorspeise'" in src
    # all three main tops filter vorspeise
    assert src.count("get('gang')!='vorspeise'")>=3

def test_loewenanteil_glas_not_unklar():
    C=_classify()
    x=dict(name='Gelbes Thai Curry',brand='Löwenanteil',packaging='Glas',packaging_raw='Glas',storage='Ungekühlt (Glas, steril)',category='Online Meal-Prep',prep='Mikrowelle 2–3 Min.')
    assert C(x)=='Glas'
    # name contains Eintopf must not override explicit Glas packaging_raw/storage
    assert C(dict(name='Berglinseneintopf',brand='Löwenanteil',packaging='Glas',packaging_raw='Glas',storage='Ungekühlt (Glas, steril)',category='Online Meal-Prep'))=='Glas'
