import sys,os; sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v2 as V
def row(**k): d=dict(name='X',size_g=400,packaging='Kühlregal (Menüschale/frisch)'); d.update(k); return d
def test_dry_pasta_flagged():
    r=V.score_v2(row(name='Clever Lasagne',kcal_100=355,fat_100=1.8,protein_100=12,packaging='Unklar (keine Lagerangabe)',size_g=500))
    assert r['nutrition_basis']=='dry' and r['health_score'] is None and r['meal_class']=='dry'
def test_dry_converted_with_prep_ratio():
    r=V.score_v2(row(name='Nudelsnack',kcal_100=380,fat_100=4,protein_100=10,salt_100=4,satfat_100=1,size_g=70,packaging='Trocken/Instant',prep='mit 250 ml heißem Wasser'))
    assert r['nutrition_basis']=='prepared' and r['health_score'] is not None
def test_tk_not_dry():
    assert V.nutrition_basis(row(kcal_100=320,fat_100=5,packaging='Tiefkühl (TK)'),None)[0]=='as_sold'
def test_sugar_penalty_protein_dessert():
    d=V.score_v2(row(name='Protein Pudding',kcal_100=80,protein_100=10,sugar_100=12,salt_100=0.2,satfat_100=1,size_g=200))
    m=V.score_v2(row(name='Chili',kcal_100=110,protein_100=8,sugar_100=2,salt_100=0.8,satfat_100=1,size_g=400))
    assert d['score_parts']['sugar']<=-6 and d['health_score']<55 and d['health_score']<m['health_score']+10
def test_sugar_points():
    assert V.sugar_points(3)==0 and V.sugar_points(12)==3 and V.sugar_points(60)==15
def test_veg_from_ingredients_not_name():
    assert V.veg_share(row(name='Gemüse Curry'),None)==(None,'unknown')
    p,s=V.veg_share(row(ingredients='Wasser, Karotten 20%, Linsen 15%, Rapsöl, Salz'),None); assert s=='ingredients_order' and p==35
def test_nova_sources():
    assert V.nova_of(row(),{'nova_group':3})==(3,'off')
    assert V.nova_of(row(ingredients='Huhn, Reis, Aroma, Maltodextrin'),None)==(4,'ingredients_markers')
    assert V.nova_of(row(packaging='Dose/Konserve'),None)==(None,'unknown')
def test_meal_check():
    assert V.meal_class(200)=='snack_side' and V.meal_class(280)=='light_meal' and V.meal_class(600)=='meal' and V.meal_class(1500)=='multi_portion'
    r=V.score_v2(row(name='Hühnersuppe',kcal_100=25,protein_100=2,salt_100=0.8,satfat_100=0.2,size_g=400)); assert r['meal_class']=='snack_side'
def test_portion_never_placeholder():
    assert V.portion(row(size_g=1200),None)==(None,'unknown')
    assert V.portion(row(name='Bowl (2 Portionen)',size_g=800),None)==(400,'name_portions')
    r=V.score_v2(row(kcal_100=150,protein_100=8,salt_100=1,satfat_100=2,size_g=400)); assert r['day_pct']['kcal']==30 and r['per_portion']['protein']==32
