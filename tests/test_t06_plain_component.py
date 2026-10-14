import sys; sys.path.insert(0,'/workspace/fertig')
import score_v2 as V
def test_plain_sousvide_pieces_are_components():
    for n in ['Wiesbauer Gourmet Barbarie Entenbrust sous vide','Wiesbauer Gourmet Saftige Rinderbacken sous vide','BILLA Genusswelt Roastbeef Sous Vide','K&P Hendlhof halbes Gauloise Blanche Huhn sous vide','GREENFORCE Frische Köttbullar VEGAN']:
        assert V.plain_component(n), n
def test_sousvide_dishes_stay_meals():
    for n in ['BILLA Genusswelt Kalbsrahmgulasch Sous Vide','Hofstädter Rindsgulasch Sous Vide','Wiesbauer Asia Style Schwein leicht scharf sous vide','Köttbullar mit Kartoffelpüree','Entenbrust in Feigen-Schalotten-Soße dazu bunter Stampf']:
        assert not V.plain_component(n), n
