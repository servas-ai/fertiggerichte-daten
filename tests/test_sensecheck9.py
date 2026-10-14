"""Sensecheck 9: per-portion values honour bofrost*'s published portion count; an OFF serving larger than a
ready-to-eat pack is ignored; top lists collapse cross-store twins even when only one store row has the GTIN."""
import os,re,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,ROOT)
import score_v2 as V

def row(**k):
    d=dict(name='X',size_g=500,packaging='Tiefkühl (TK)',kcal_100=171,protein_100=18,salt_100=1,satfat_100=2); d.update(k); return d

def test_bofrost_provider_portions():
    x=row(name='Tafelspitz in Krensauce',store='Online: bofrost*',portions=2.0)
    assert V.portion(x,None)==(250,'provider_portions')
    r=V.score_v2(x); assert r['portion_g']==250 and r['kcal_meal']==428
    assert V.meal_check(x,r)['portion']==250
    # soup insert sold as 10 portions is not a 500 g meal
    assert V.portion(row(name='Leberspätzle',store='Online: bofrost*',portions=10.0),None)==(50,'provider_portions')

def test_provider_portions_only_bofrost_and_gt1():
    assert V.portion(row(store='Online: Juit',portions=2),None)==(500,'pack_single')
    assert V.portion(row(store='Online: bofrost*',portions=1.0),None)==(500,'pack_single')
    assert V.portion(row(store='Online: bofrost*',portions=None,size_g=1000),None)==(None,'unknown')

def test_name_portions_still_win():
    assert V.portion(row(name='Bowl (XL, 2 Portionen)',store='Online: bofrost*',portions=4,size_g=1000),None)==(500,'name_portions')

def test_off_serving_bigger_than_ready_pack_ignored():
    x=row(name='followfood BIO Dinkel-Pizza Verdura',size_g=300,kcal_100=173)
    assert V.portion(x,{'serving_quantity':339,'serving_size':'339 g'})==(300,'pack_single')
    # normal OFF serving inside the pack is kept
    assert V.portion(row(size_g=700),{'serving_quantity':350,'serving_size':'350 g'})==(350,'off_serving')

def test_off_serving_kept_for_instant():
    # instant cup: serving = prepared weight (with water) > dry pack weight → keep the OFF serving
    assert V.portion(row(size_g=70,kcal_100=440,packaging='Unklar (keine Lagerangabe)'),{'serving_quantity':375,'serving_size':'375 g'})==(375,'off_serving')
    assert V.portion(row(size_g=70,kcal_100=90,packaging='Trocken/Instant'),{'serving_quantity':375,'serving_size':'375 g'})==(375,'off_serving')

def _collapse_ns():
    src=open(os.path.join(ROOT,'export_app.py')).read()
    a=src.index('_NOISE=re.compile'); b=src.index('_n_baby=0',a)
    c=src.index('def _prod_key'); d=src.index('def _exact_key',c)
    e=src.index('_TWIN_NOISE=re.compile'); f=src.index('topPLI,_c_pli',e)
    ns={'re':re}; exec(src[a:b]+src[c:d]+src[e:f],ns); return ns

def test_top_list_collapses_cross_store_twins():
    ns=_collapse_ns()
    R=[dict(id=1,store='MPreis',name='Iglo Polardorsch Serbische Art MSC',brandN='iglo',size=300.0,ean='9000143315925',s=60),
       dict(id=2,store='Billa',name='Iglo Polar-Dorsch Serbische Art',brandN='iglo',size=300.0,ean=None,s=59),
       dict(id=3,store='Spar',name='Iglo MSC Pazifischer Polar-Dorsch Serbische Art 4 Stück',brandN='iglo',size=300.0,ean=None,s=58),
       dict(id=4,store='MPreis',name='Dr. Oetker Ristorante Tonno',brandN='Dr. Oetker',size=355.0,ean='4001724038993',s=50),
       dict(id=5,store='Billa',name='Dr. Oetker Ristorante Pizza Tonno',brandN='Dr. Oetker',size=355.0,ean=None,s=49),
       dict(id=6,store='Billa',name='Iglo Polar-Dorsch Mediterrane Art',brandN='iglo',size=300.0,ean=None,s=48),
       dict(id=7,store='Billa',name='Iglo Lasagne al Forno',brandN='iglo',size=350.0,ean=None,s=47),
       dict(id=8,store='Gurkerl',name='Iglo Lasagne al Forno (tiefgekühlt)',brandN='iglo',size=700.0,ean=None,s=46)]
    kept,col=ns['_collapse'](R,lambda r:r['s'])
    assert [r['id'] for r in kept]==[1,4,6,7,8], [r['id'] for r in kept]  # different size (350 vs 700 g) stays separate
    assert col==3 and kept[0]['alsoAt']==['Billa','Spar'] and kept[1]['alsoAt']==['Billa']
