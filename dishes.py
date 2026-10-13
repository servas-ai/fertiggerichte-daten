import re
# (dish_key, label, regex) — order matters: specific first
DISHES=[
('wiener-suppentopf','Wiener Suppentopf',r'suppentopf'),
('gulaschsuppe','Gulaschsuppe',r'gulaschsuppe|gulasch-suppe|gulyas ?suppe'),
('erdaepfelgulasch','Erdäpfelgulasch',r'erd[äa]+pfel ?-?gulasch|kartoffel ?-?gulasch|würstel ?-?gulasch'),
('saftgulasch','Saftgulasch',r'saftgulasch|fiakergulasch|wiener saft'),
('hirschragout','Hirschragout/Wildgulasch',r'hirsch|wildragout|wildgulasch|reh ?ragout'),
('szegediner','Szegediner Gulasch',r'szegedin|krautgulasch|székely'),
('rindsgulasch','Rindsgulasch',r'rinds?gulasch|rindergulasch|gulasch'),
('chili-sin-carne','Chili sin carne',r'chili sin carne|chili vegan|veg\w* chili|chili.*(vegan|veggie|bohnen sin)'),
('chili-con-carne','Chili con carne',r'chili con carne|chili con|chili'),
('linseneintopf','Linseneintopf',r'linsen ?-?(eintopf|suppe|topf|curry)|linsen mit|linsengericht|\bdal\b|\bdhal\b|\bdaal\b'),
('erbsensuppe','Erbseneintopf/-suppe',r'erbsen ?-?(eintopf|suppe)'),
('bohneneintopf','Bohneneintopf',r'bohnen ?-?(eintopf|suppe|topf)|serbische bohnen|bohnengulasch|baked beans|bohnen mit speck'),
('cannelloni','Cannelloni',r'cannelloni'),
('lasagne','Lasagne',r'lasagne|lasagna'),
('ravioli','Ravioli',r'ravioli'),
('spaghetti-bolognese','Spaghetti/Pasta Bolognese',r'bolognese|bolognaise'),
('reisfleisch','Reisfleisch',r'reisfleisch'),
('butter-chicken','Butter Chicken',r'butter ?chicken|murgh makhani|tikka masala'),
('gemuesecurry','Gemüsecurry',r'(gemüse|veggie|kichererbsen|vegan\w*|tofu)\w* ?-?curry|curry.*(gemüse|kichererbsen|tofu)'),
('huhn-curry','Huhn Curry',r'(huhn|hühner|hähnchen|chicken|hendl|geflügel)\w*.{0,20}curry|curry.{0,20}(huhn|hühn|hähnchen|chicken|hendl)|curry ?huhn|chicken curry|thai ?curry|red curry|green curry'),
('curry','Curry (sonstige)',r'curry'),
('paprikahuhn','Paprikahuhn',r'paprika ?-?(huhn|hendl|hähnchen)|hühnerpaprika|paprikahendl'),
('geschnetzeltes','Geschnetzeltes',r'geschnetzelt|zürcher'),
('kaesespaetzle','Käsespätzle/Kasnocken',r'käse ?-?sp[äa]tzle|kässp[äa]tzle|kasnock|käsnock|kasspatz'),
('schinkenfleckerl','Schinkenfleckerl',r'schinkenfleckerl|schinken ?-?fleckerl'),
('krautfleckerl','Krautfleckerl',r'krautfleckerl'),
('faschierter-braten','Faschierter Braten/Fleischlaibchen mit Püree',r'faschierter braten|faschiertes laibchen.*pür|fleischlaib\w*.*(pür|püree)|hackbraten'),
('schweinsbraten','Schweinsbraten (mit Knödel)',r'schweinsbraten|schweinebraten|krustenbraten'),
('backhendl','Backhendl',r'backhendl|backhuhn|backhähnchen'),
('tafelspitz','Tafelspitz',r'tafelspitz'),
('rindsrouladen','Rindsrouladen',r'(rinds?|rinder)\w*roulade|roulade.*(rind|rahm|sauce)'),
('stroganoff','Boeuf Stroganoff',r'stroganoff'),
('rahmschwammerl','Schwammerlsauce/Rahmschwammerl',r'schwammerl ?-?(sauce|soße|gulasch)|rahmschwammerl|champignon ?-?rahm|pilz ?-?rahm'),
('kartoffelgratin','Gratin/Auflauf',r'gratin|auflauf'),
('cevapcici','Cevapcici/Djuvec',r'cevap|djuvec|đuveč'),
('nasi-goreng','Nasi/Bami Goreng',r'nasi goreng|bami goreng|mie goreng'),
('risotto','Risotto',r'risotto'),
('mac-and-cheese','Mac and Cheese/Käsemakkaroni',r'mac.{0,5}cheese|käsemakkaroni|makkaroni ?-?käse'),
('ripperl','Ripperl/Spare Ribs',r'ripperl|spare ?ribs'),
('eintopf','Sonstiger Eintopf',r'eintopf'),
]
_C=[(k,l,re.compile(r,re.I)) for k,l,r in DISHES]
LABEL={k:l for k,l,_ in DISHES}
EXCL=re.compile(r'\bbasis\b|fix für|seasoning|\bmix\b|hipp|alete|ab dem \d|ab \d+ (jahr|monat)|babym|bambini|gewürz|würzmischung|\bfix\b|fix für|sauce\b(?!.*(mit|reis))|soße|pulver|paste|ketchup|chips|cracker|snack|gewürzmühle|mühle|marinade|dressing|senf|bohnen ?gekocht|nudeln roh|teigwaren|lasagneblätter|lasagne ?blätter|lasagne ?platten|cannelloni ?röhren|tortilla|nachos|flips|schoten|chilischote|chiliflocken|chili ?öl|sweet chili|chili ?sauce|currysauce|curry ?pulver|curry ?ketchup|currywurst ?sauce|kokosmilch|katzen|hunde|tiernahrung|felix .*katze|whiskas|gourmet|sheba|pedigree',re.I)
def dish_key(name,brand=''):
    t=(name or '')
    if EXCL.search(t): return None
    for k,l,c in _C:
        if c.search(t): return k
    return None
