cd /workspace/food-connectors
python3 -m food_connectors.cli fetch --category ready-meals --store gurkerl --enrich -o /workspace/fertig/exp/gk_fetch.json
for t in suppentopf eintopf gulasch lasagne risotto curry chili "fertiggericht" "fertigmenü" knödel spätzle schupfnudeln gnocchi tortellini ravioli moussaka bowl "nasi goreng" "bami goreng" "pad thai" ramen tikka dal "linsen" "gemüsepfanne" kaiserschmarrn germknödel marillenknödel topfenknödel milchreis grießkoch pudding tiramisu "panna cotta" "mousse" suppe bolognese carbonara wrap couscous falafel frikassee ragout geschnetzeltes rouladen auflauf gratin strudel palatschinken quiche gnocchi "chili sin carne" "gefüllte paprika" "schweinsbraten" "backhendl" "schnitzel" "fleischlaberl" "krautfleckerl" "schinkenfleckerl" "kasnocken" "erdäpfelgulasch" "gemüsecurry" "salat bowl" "sushi" "dessert" "cheesecake" "kuchen dessert" "polenta" "paella" "cannelloni" "burrito" "enchilada" "hummus bowl" "frühlingsrolle" "dim sum" "gyoza" "teriyaki"; do
 python3 -m food_connectors.cli search "$t" --store gurkerl --enrich > "/workspace/fertig/exp/gk_$(echo $t|tr ' ' _).json" 2>/dev/null; sleep 1
done
echo DONE
