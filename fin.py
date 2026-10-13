import json,re,collections
o=json.load(open('expand.json'))
J=re.compile(r'erdal|vandal|schuh|ameisen|fliege|insekt|gourmet gold|nassfutter|katze|hund|basis\b|basis für|\bfix\b|teigbl|lasagneblätter|lasagne.?blätter|risotto reis|reis lose|curry (mild|mittelscharf|powder|rot)|curry\s*$|currypulver|powder|spice|brotaufstrich|frischkäse|aufstrich|gulaschsaft|gewürz|würz|kotányi|good karma|ragout$|ragout (huhn|thunfisch|mit rind)|sauce|soße|samen|chips|snack|juice|saft',re.I)
BC={'Insektenschutz','Nassfutter','Schuhpflege','Gewürzgläser, Mühlen & Dosen','Basis- & Fixprodukte','Rundkorn'}
k=[x for x in o if not J.search(x['name']) and x['category'] not in BC]
for x in k:
  if x.get('off_match') and float(re.search(r'\(([\d.]+)\)',x['off_match']).group(1))<0.67:
    for f in ['kcal_100','protein_100','fat_100','satfat_100','carbs_100','sugar_100','fiber_100','salt_100','protein_pack','kcal_pack','nutriscore']: x[f]=None
    x['nut_source']=None; x['off_match']=None
json.dump(k,open('expand.json','w'),ensure_ascii=False,indent=1)
n=len(k);print(n,collections.Counter(x['store'] for x in k))
for f in ['kcal_100','protein_100','fat_100','satfat_100','carbs_100','sugar_100','fiber_100','salt_100','image_url','url','producer_id','manufacturer','packaging','price_eur']:
  c=sum(1 for x in k if x.get(f) is not None);print(f,c,f'{100*c/n:.0f}%')
print(collections.Counter(x['category'] for x in k).most_common(10))
print(collections.Counter((x['store'],x['protein_100'] is not None) for x in k))
