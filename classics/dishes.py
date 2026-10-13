import re
D=[('wiener-suppentopf','Wiener Suppentopf',r'suppentopf'),
('saftgulasch','Saftgulasch',r'saft\s?gulasch'),
('erdaepfelgulasch','Erdäpfelgulasch',r'(erdäpfel|kartoffel)\s?gulasch'),
('gulaschsuppe','Gulaschsuppe',r'gulasch\s?-?suppe|gulaschcreme'),
('szegediner','Szegediner Gulasch',r'szegediner'),
('rindsgulasch','Rindsgulasch',r'(rinds?|rinder|fiaker|wiener)\s?-?gulasch|^gulasch|gulasch\s(mit|vom)|\bgulasch\b'),
('chili-sin-carne','Chili sin carne',r'chili\s?sin|veg\w*\s?chili|chili\s?veg'),
('chili-con-carne','Chili con carne',r'chili\s?con|chili\s?carne'),
('linseneintopf','Linseneintopf',r'linsen\s?-?(eintopf|suppe|gericht|curry)|linseneintopf'),
('bohneneintopf','Bohneneintopf',r'bohnen\s?-?(eintopf|suppe|topf)|serbische\s?bohn'),
('erbsensuppe','Erbsensuppe/-eintopf',r'erbsen\s?-?(suppe|eintopf)'),
('kartoffelsuppe','Kartoffelsuppe',r'(kartoffel|erdäpfel)\s?-?(suppe|eintopf|rahmsuppe)'),
('nudeleintopf','Nudeleintopf',r'nudel\s?-?eintopf'),
('lasagne','Lasagne',r'lasagne'),
('cannelloni','Cannelloni',r'cannelloni'),
('ravioli','Ravioli',r'ravioli'),
('reisfleisch','Reisfleisch',r'reisfleisch'),
('butter-chicken','Butter Chicken',r'butter\s?chicken'),
('gemuesecurry','Gemüsecurry',r'(gemüse|veg\w*|kichererbsen|thai)\s?-?curry'),
('huhn-curry','Huhn Curry',r'(huhn|hühner|hähnchen|chicken|geflügel|pute)\w*\s?-?curry|curry\s?-?(huhn|hühn|chicken|hähnchen)|tikka|korma'),
('dal','Dal',r'\bdal\b|\bdhal\b'),
('geschnetzeltes','Geschnetzeltes',r'geschnetzelt'),
('spaghetti-bolognese','Spaghetti Bolognese',r'bolognese'),
('kaesespaetzle','Käsespätzle',r'käse\s?-?spätzle|kasnocken|kässpätzle|käsknöpfle'),
('schinkenfleckerl','Schinkenfleckerl',r'schinkenfleckerl|schinken\s?fleckerl'),
('krautfleckerl','Krautfleckerl',r'krautfleckerl'),
('faschierter-braten','Faschierter Braten',r'faschierter\s?braten|hackbraten|faschierte\s?laibchen|fleischlaibchen|frikadell|fleischbällchen|köttbullar'),
('schweinsbraten','Schweinsbraten',r'schweins\s?braten|schweinebraten|krustenbraten'),
('paprikahuhn','Paprikahuhn',r'paprika\s?-?(huhn|hendl|hähnchen)'),
('tafelspitz','Tafelspitz',r'tafelspitz'),
('rindsrouladen','Rindsrouladen',r'roulade'),
('stroganoff','Stroganoff',r'stroganoff'),
('chili-andere','Chili (andere)',r'^xx'),
('kasnocken','Kärntner Kasnudeln',r'kasnudel|schlutzkrapfen'),
('stelze','Stelze/Ripperl',r'stelze|ripperl|spareribs'),
('beuschel','Beuschel',r'beuschel'),
('fleischknoedel','Fleisch-/Grammelknödel',r'(fleisch|grammel|speck|selch|haschee)\s?-?knödel'),
('tortellini','Tortellini',r'tortellini|tortelloni'),
('risotto','Risotto',r'risotto'),
('gnocchi-gericht','Gnocchi-Gericht',r'gnocchi\s.*(sauce|soße|tomat|käse|pesto)'),
('kohlroulade','Krautroulade/Gefüllte Paprika',r'krautroulade|kohlroulade|gefüllte\s?paprika|sarma'),
('eintopf-sonstige','Eintopf (sonstige)',r'eintopf'),
]
NO=r'gewürz|würzmischung|fix\b|fix für|\bfix |sauce\b(?!.*(mit|und))|soße|sauce$|basis|chips|snack|nuss|tofu natur|bohnen\s?(natur|weiß|rot)|kernig|cracker|ketchup|mayonnaise|dressing|chilischote|chilisauce|chiliflocken|pulver|paste|salami|wurst(?!.*(gulasch))|käse\s?(scheiben|block)|katze|hund|tiernahrung|felix\s?(sensations|party|katzen)|whiskas|sheba|gourmet|dip|aufstrich|brot|toast|pizza(?!.*lasagne)|schmelzkäse|pfeffer|öl\b|gläser|zigarett|teigblätter|lasagneblätter|lasagneplatten|lasagnette|platten|nudeln\s?(roh|getrocknet)|cannelloni\s?\d|^barilla|^de cecco|^la molisana|spätzle\s?\d|teigwaren|eierteig|hartweizen|fleckerl\s?\d|gnocchi\s?\d|suppenwürze|suppengrün|bouillon|würfel|knorr fix|maggi fix|kochbeutel|reis\s?\d|basmati'
def dish(name):
    n=(name or '').lower()
    if re.search(NO,n): 
        # allow ready sauces? no
        return None
    for k,lab,p in D:
        if re.search(p,n): return k
    return None
LABEL={k:l for k,l,_ in D}
