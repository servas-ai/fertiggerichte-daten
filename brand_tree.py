import json,re,collections,statistics as st
A=json.load(open('/workspace/fertig-app/public/data.json'));R=A['rows']
V=json.load(open('/workspace/fertig/producers_v2.json'))
comp={c['slug']:c for c in json.load(open('/workspace/fertig/analysis/companies.json'))}
v_by_url={p['url']:p for p in V['products'] if p.get('url')}
# 2026-10-13T02 additions (sources): Perutnina→MHP SE (mhp.com.ua press release 21.02.2019), bibigo→CJ CheilJedang (cj.co.kr/en/brands/bibigo),
#  Ben's Original→Mars Inc. (mars.com press release 08.07.2025), MAMA instant noodles→Thai President Foods (mama.co.th), Marks & Spencer→Marks and Spencer Group plc
# 2026-10-13T03: MPreis shop import — MPREIS/EMP, AIA/Veronesi, Youcook, Deflorian, Brajlovic, Alnatura, Meica, Planted, Riso Scotti, Bertagni, Delamaris
# 2026-10-13T04: Hofmann Menü-Manufaktur→Compass Group (de.wikipedia Hofmann-Menü_Holdings; northdata HRB 560522 Gesellschafter Compass Group Deutschland GmbH)
# 2026-10-13T09: GAON GmbH Wien FN 608356t (gaon-vienna.com); Hengstenberg Familienunternehmen (hengstenberg.com/company); Mochi GmbH Wien LEI 391200XRB8WKVGZ3DQ31; Wiener Virtshaus; Mahavira Kanswala (Gurkerl Hersteller)
# 2026-10-13T10: Ashoka→ADF Foods (adf-foods.com/brands/ashoka); Südtiroler Kochwerk→Südtiroler Kochwerk GmbH (suedtiroler-kochwerk.it); Morgentau Biogemüse GmbH Hofkirchen OÖ (morgentau.at); Samyang Foods (samyangfoods.com); Della Mamma→Ölz (tiramisu); Andros (andros.de); PICARD Surgelés (picard.fr); Kreyenhop & Kluge/Diamond; Golfera/Ben Fatto; Pappudia (Lidl brand via Gurkerl)
# 2026-10-13T11: Wagner→European Pizza Group (Nestlé/PAI JV, nestle.com PR 21.04.2023, EU case M.11147; label still names Nestlé Österreich as Inverkehrbringer);
#  Gustavo Gusto GmbH & Co. KG Geretsried HRA 110625 (gustavo-gusto.de/impressum, gründergeführt, keine externen Investoren bekannt); followfood GmbH Friedrichshafen HRB 631854 (Gründer Knoll/Butsch Mehrheit, de.wikipedia Followfood);
#  Dr. Oetker/Ristorante→Oetker-Gruppe (Dr. August Oetker KG, oetker-gruppe.de)
# 2026-10-13T13: Heura→Foods for Tomorrow S.L. (heurafoods.com; EIB project 20240549 FOODS FOR TOMORROW SLU; DE-GmbH 100% Tochter);
#  Nordsee LEH-Lizenzprodukte→HOMANN Feinkost / Unternehmensgruppe Theo Müller (muellergroup.com fish-deli brands; Lizenz seit 2015);
#  HOMANN→Unternehmensgruppe Theo Müller (seit 2011, de.wikipedia Homann_Feinkost; muellergroup.com);
#  Yopokki→Young Poong Co., Ltd. / YPFOODS (ypfoods.co.kr brand page);
#  VIFON→Vietnam Food Industries (Vifon) (vifon.com.vn; historisch JV Acecook, heute eigenständig);
#  Podravka→Podravka d.d. (podravka.com; börsennotiert HR);
#  Windisch→Stefan Windisch GmbH Wiener Neustadt (windisch-wurst.at Impressum/Produktseite);
#  Farniente→Farniente S.A. Seilles BE (farniente.be / food.be; unabhängiges Familienunternehmen seit 1991)
# 2026-10-13T12: Coppenrath & Wiese→Oetker-Gruppe seit 2015 (oetker.com/de/ueber-uns/wer-wir-sind/unternehmensstruktur, Geschäftsbericht 2025);
#  Freda→siu foods GmbH Passau (eatfreda.com/pages/faq, Herstellerangabe BILLA-Shop; Start-up gegr. 2022); Namdong K-Noodles→Unilever (Inverkehrbringer Unilever Austria laut BILLA-Shop)
# 2026-10-13T14: Schulzi's Knödel→BS Gastro & Event Services GmbH (BRoK Catering, Schwechat, FN 433660k; brok-catering.at/de/Impressum.html, brok.at/schulzisknoedel);
#  Berger Schinken→Fleischwaren Berger GmbH & Co KG, Familie Berger (Gesellschafter Mag. Rudolf Berger 100 % über Berger Schinken Beteiligungs GmbH FN 456320i; evi.gv.at/f/456320i, berger-schinken.at/ueber-uns);
#  Alpenhain→Alpenhain Käsespezialitäten-Werk GmbH & Co. KG, Familie Hain (alpenhain.de/ueber-uns/unsere-historie; HRB 17428 AG Traunstein);
#  Rebel Meat/Rebel Kids→concept cool Vertriebsgesellschaft mbH St. Pölten (Asset Deal Juni 2024, concept-cool.at Presseinformation 04.06.2024; Etikett nennt weiter Rebel Meat GmbH FN 516090g)
BRAND_KONZ=[(r"schulzi",'BS Gastro & Event Services GmbH (BRoK, Schwechat)','🇦🇹'),(r'\bberger\b','Fleischwaren Berger (Familie Berger)','🇦🇹'),(r'alpenhain','Alpenhain Käsespezialitäten (Familie Hain)','🇩🇪'),(r'rebel meat|rebel kids','concept cool Vertriebsgesellschaft mbH (Rebel Kids)','🇦🇹'),(r'\bheura\b','Foods for Tomorrow / Heura Foods','🇪🇸'),(r'\bnordsee\b','HOMANN Feinkost (Theo Müller, Nordsee-Lizenz)','🇩🇪'),(r'\bhomann\b','Unternehmensgruppe Theo Müller','🇱🇺'),(r'yopokki|yo ?pokki','Young Poong Co., Ltd. (YPFOODS)','🇰🇷'),(r'\bvifon\b','Vietnam Food Industries (Vifon)','🇻🇳'),(r'podravka','Podravka d.d.','🇭🇷'),(r'\bwindisch\b','Stefan Windisch GmbH','🇦🇹'),(r'farniente','Farniente S.A. (Seilles)','🇧🇪'),(r'coppenrath','Oetker-Gruppe (Dr. August Oetker KG)','🇩🇪'),(r'\bfreda\b','siu foods GmbH (Freda, Passau)','🇩🇪'),(r'namdong','Unilever','🇬🇧'),(r'\bwagner\b','European Pizza Group (Nestlé/PAI-JV)','🇩🇪'),(r'gustavo gusto','Gustavo Gusto GmbH & Co. KG','🇩🇪'),(r'followfood|followfish','followfood GmbH','🇩🇪'),(r'dr\.? ?oetker|ristorante','Oetker-Gruppe (Dr. August Oetker KG)','🇩🇪')]
KONZ=[(r'hofmann men','Compass Group plc (Hofmann-Menü-Gruppe)','🇬🇧'),(r'perutnina','MHP SE (Perutnina Ptuj)','🇺🇦'),(r'bibigo','CJ CheilJedang','🇰🇷'),(r"ben'?s original",'Mars Inc.','🇺🇸'),(r'\bmama instant','Thai President Foods','🇹🇭'),(r'marks ?& ?spencer','Marks and Spencer Group plc','🇬🇧'),(r'\bgaon\b','GAON GmbH (Wien)','🇦🇹'),(r'hengstenberg','Hengstenberg GmbH & Co. KG (Familie)','🇩🇪'),(r'\bmochi\b','Mochi GmbH (Wien)','🇦🇹'),(r'virtshaus|wiener virtshaus','Wiener Virtshaus','🇦🇹'),(r'mahavira|kanswala','Mahavira Kanswala','🇦🇹'),(r'\bashoka\b','ADF Foods (Ashoka)','🇮🇳'),(r'südtiroler kochwerk|suedtiroler kochwerk','Südtiroler Kochwerk GmbH','🇮🇹'),(r'\bmorgentau\b','MORGENTAU Biogemüse GmbH','🇦🇹'),(r'samyang|buldak','Samyang Foods','🇰🇷'),(r'della mamma','Ölz / Della Mamma','🇦🇹'),(r'\bandros\b','Andros','🇫🇷'),(r'\bpicard\b','Picard Surgelés','🇫🇷'),(r'kreyenhop|\bdiamond\b','Kreyenhop & Kluge (Diamond)','🇩🇪'),(r'golfera|ben fatto','Golfera / Ben Fatto','🇮🇹'),(r'pappudia','Pappudia','🇪🇺'),(r'prepmymeal|prep my meal','PrepMyMeal','🇦🇹'),
 (r'rewe|billa|genussk|ja! nat|merkur|penny','REWE Group','🇩🇪'),(r'gourmet|vivatis|inzersdorfer|maresi|hink|wojnar|karnerta','VIVATIS Holding (RLB OÖ)','🇦🇹'),
 (r'unilever|knorr','Unilever','🇬🇧'),(r'nestl|maggi','Nestlé','🇨🇭'),(r'iglo','Nomad Foods','🇬🇧'),(r'frosta','FRoSTA AG','🇩🇪'),(r'rana','Pastificio Rana','🇮🇹'),
 (r'landena','Landgenossenschaft Ennstal (Genossenschaft)','🇦🇹'),(r'blasko|marcher','Marcher Fleischwerke','🇦🇹'),(r'wiesbauer','Wiesbauer Gruppe','🇦🇹'),(r'felix','Felix Austria (Orkla)','🇳🇴'),(r'spar','SPAR Österreich','🇦🇹'),
 (r'hofer|aldi','ALDI Süd','🇩🇪'),(r'lidl','Schwarz Gruppe','🇩🇪'),(r'fit2go|fit to go','Fit2go GmbH','🇦🇹'),(r'mars','Mars Inc.','🇺🇸'),(r'radatz','Radatz','🇦🇹'),(r'hochreiter','Hochreiter Gruppe','🇦🇹'),
 (r'mpreis','MPREIS (EMP)','🇦🇹'),(r'\baia\b|gruppo veronesi','Gruppo Veronesi','🇮🇹'),(r'youcook','Youcook GmbH','🇩🇪'),(r'deflorian','Deflorian S.r.l.','🇮🇹'),(r'brajlovic','Brajlovic GmbH','🇦🇹'),(r'alnatura','Alnatura','🇩🇪'),(r'meica','Meica GmbH','🇩🇪'),(r'planted','Planted Foods AG','🇨🇭'),(r'riso scotti','Riso Scotti','🇮🇹'),(r'bertagni','Bertagni 1882','🇮🇹'),(r'delamaris','Delamaris','🇸🇮')]
# NOTE: VIVATIS ownership of Landena/Inzersdorfer/Maresi/Hink/Wojnar/Greisinger per producer_profiles & vivatis.at portfolio; Karnerta excluded below if not confirmed
def konzern(h,brand=''):
  for rx,k,f in BRAND_KONZ:
    if re.search(rx,brand or '',re.I): return k,f
  for rx,k,f in KONZ:
    if re.search(rx,h,re.I): return k,f
  return 'Unabhängig / unbekannt','🏳️'
# code-resolved producers from app data
code_prod={}
for p in A['producers']:
  for i in p.get('ids',[]): code_prod[i]=(p['name'],p.get('slug'),(p.get('plants') or [{}])[0])
for s in A['same']:
  for i in s['ids']: code_prod.setdefault(i,(s['herst'],None,{'approval_code':s['code'],'address':s['ort']}))
def norm(h):
  h=h.split('\n')[0].split(',')[0].strip()
  h=re.sub(r'\s+',' ',h); 
  if re.fullmatch(r'(?i)billa ag',h): return 'BILLA AG'
  if re.match(r'(?i)iglo',h): return 'Iglo Austria'
  return h
RET={'BILLA AG','SPAR Österreichische Warenhandels-AG','HOFER KG','Lidl Österreich GmbH','Ja! Natürlich Naturprodukte Gesellschaft m.b.H.'}
items=[]
for r in R:
  if r.get('nonfood') or r['stage'] not in('meal','stew','prot','side','veg'): continue
  v=v_by_url.get(r['url']) or {}
  if r['id'] in code_prod:
    n,slug,pl=code_prod[r['id']];conf='confirmed-code';src='https://vis.statistik.at/fileadmin/ovis/pdf/index.html'
    code=pl.get('approval_code');plant=pl.get('address') or pl.get('town')
  elif v.get('confidence')=='confirmed-code' and v.get('producer_company'):
    n=v['producer_company'];slug=None;conf='confirmed-code';src=v.get('evidence_url');code=v.get('plant_code');plant=v.get('plant_town')
  elif r['herst']:
    n=norm(r['herst']);slug=None;code=None;plant=r.get('ort') or None
    conf='recall/press' if 'Fit2go' in n else 'label-address';src=r['url']
  else: continue
  role='Inverkehrbringer (Handel) – Werk unbekannt' if (n in RET or re.match(r'(?i)(billa|spar|hofer|lidl)\b',n)) and conf!='confirmed-code' else 'Hersteller'
  k,f=konzern(n,r.get('brandN') or r.get('brand') or '')
  items.append(dict(id=r['id'],name=r['name'],brand=r['brandN'] or r['brand'],store=r['store'],dishKey=r['dishKey'],dish=r['dish'],price=r['price'],p100g=r.get('p100g'),pPor=r.get('pPor'),img=r['img'],producer=n,role=role,konzern=k,flag=f,code=code,plant=plant,confidence=conf,source=src,slug=slug))
# tree
tree=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(list)))
for it in items: tree[it['konzern']][it['producer']][it['brand']].append(it['id'])
logo_of={c['name']:c.get('logo_path','').replace('/workspace/fertig/','') for c in comp.values() if c.get('logo_path')}
T=[]
for k,ps in sorted(tree.items(),key=lambda x:-sum(len(i) for p in x[1].values() for i in p.values())):
  kn={'konzern':k,'flag':next(i['flag'] for i in items if i['konzern']==k),'producers':[]}
  for p,bs in sorted(ps.items(),key=lambda x:-sum(map(len,x[1].values()))):
    its=[i for i in items if i['producer']==p]
    kn['producers'].append({'name':p,'role':its[0]['role'],'logo':logo_of.get(p),'codes':sorted({i['code'] for i in its if i['code']}),'plants':sorted({i['plant'] for i in its if i['plant']}),
      'confidence':collections.Counter(i['confidence'] for i in its).most_common(1)[0][0],'stores':sorted({i['store'] for i in its}),
      'brands':[{'brand':b,'stores':sorted({i['store'] for i in its if i['brand']==b}),'ids':ids} for b,ids in sorted(bs.items(),key=lambda x:-len(x[1]))]})
  kn['n']=sum(len(b['ids']) for p in kn['producers'] for b in p['brands']);T.append(kn)
# same product different label: same producer (role Hersteller) + dishKey, >=2 brands or stores
same=[]
g=collections.defaultdict(list)
for it in items:
  if it['dishKey'] and it['role']=='Hersteller': g[(it['producer'],it['dishKey'])].append(it)
for (p,dk),its in g.items():
  labels={(i['brand'],i['store']) for i in its}
  if len(labels)<2: continue
  pr=[i['p100g'] for i in its if i['p100g']]
  spread=round((max(pr)/min(pr)-1)*100) if len(pr)>=2 else None
  same.append({'producer':p,'konzern':its[0]['konzern'],'dishKey':dk,'dish':its[0]['dish'],'kind':'andere Marke/Eigenmarke' if len({i['brand'] for i in its})>1 else 'gleiche Marke, andere Kette','labels':[{'brand':b,'store':s} for b,s in sorted(labels)],'ids':[i['id'] for i in its],
    'cheapest':min(its,key=lambda i:i['p100g'] or 1e9)['id'],'price_spread_pct':spread,'confidence':collections.Counter(i['confidence'] for i in its).most_common(1)[0][0]})
same.sort(key=lambda x:(x['kind']!='andere Marke/Eigenmarke',-(x['price_spread_pct'] or 0)))
# dish overview: which dishes are offered under many labels and how many distinct producers known
dish=[]
for dk,its in collections.defaultdict(list,{}).items(): pass
dd=collections.defaultdict(list)
for r in R:
  if r['dishKey'] and r['stage'] in('meal','stew') and not r.get('nonfood'): dd[r['dishKey']].append(r)
pmap={i['id']:i for i in items}
for dk,rs in dd.items():
  if len(rs)<5: continue
  pr=[r['p100g'] for r in rs if r.get('p100g')]
  dish.append({'dishKey':dk,'dish':rs[0]['dish'],'n':len(rs),'brands':len({r['brandN'] for r in rs}),'stores':sorted({r['store'] for r in rs}),
   'producers_known':sorted({pmap[r['id']]['producer'] for r in rs if r['id'] in pmap and pmap[r['id']]['role']=='Hersteller'}),
   'unknown_share':round(100*sum(1 for r in rs if r['id'] not in pmap or pmap[r['id']]['role']!='Hersteller')/len(rs)),
   'p100g_min':min(pr) if pr else None,'p100g_max':max(pr) if pr else None})
dish.sort(key=lambda x:-x['n'])
out={'generated':'2026-10-13','method':['Identitätskennzeichen → amtliche ÖVIS-Liste (vis.statistik.at)','Etikett-Herstelleradresse (BILLA-Shop Pflichtangaben)','producers_v2.json / producer_profiles.json / companies.json (Firmenbuch-/Website-Fakten)','Konzernzuordnung nach Eigentümer-Angaben in producer_profiles'],
 'confidence_legend':V['confidence_legend'],'coverage':{'products_with_producer':len(items),'confirmed_code':sum(i['confidence']=='confirmed-code' for i in items),'retailer_only':sum(i['role']!='Hersteller' for i in items)},
 'tree':T,'same_product':same,'dishes':dish,'items':items}
json.dump(out,open('/workspace/fertig/analysis/brand_tree.json','w'),ensure_ascii=False)
print(out['coverage'],len(T),len(same),len(dish))
for s in same[:12]: print(s['producer'],s['dish'],s['labels'],s['price_spread_pct'])
for d in dish[:8]: print(d['dish'],d['n'],d['brands'],d['producers_known'],d['unknown_share'])
