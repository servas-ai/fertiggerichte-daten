"""Daten-Squad 2026-10-13T11 logo merge: additive only (new keys + extra brand aliases) into fertig/analysis/logos.json.
Every new logo was visually checked on gate_final.png (correct brand, sharp, no placeholder, no product photo)."""
import json,shutil,os,datetime
CM=json.load(open('cm_meta.json'))
G='Vision gate 2026-10-13T11 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto)'
def cm(k): m=CM[k]; return m['page'], f"Wikimedia Commons ({m['license']})"
NEW=[
 # slug,name,category,brands,file,source,origin-note
 ('noem','NÖM','Markenhersteller',['NÖM','Nöm','nöm','nöm PRO','Nöm PRO','nöm Cremix','NÖM PRO'],'noem.png','https://www.noem.at/logo_512x512.png','offizielles Logo von noem.at (NÖM AG, Baden)'),
 ('zurueck-zum-ursprung','Zurück zum Ursprung','Eigenmarke',['Zurück zum Ursprung','ZURÜCK','ZURÜCK ZUM URSPRUNG'],'zurueck-zum-ursprung.svg','https://www.zurueckzumursprung.at/_assets/4b8eedeac75dabf6c5c55a34303952fc/Images/Logo-2026.svg','offizielles Header-Logo zurueckzumursprung.at (Hofer-Bio-Eigenmarke)'),
 ('danone','Danone','Markenhersteller',['Danone','Danone Belux nv'],'danone.png',*cm('danone')),
 ('bibigo','Bibigo','Markenhersteller',['Bibigo','bibigo'],'bibigo.svg','https://cdn.sanity.io/images/mf5qmsk4/production/7f117672123d4ebf0ddf23531397fc7129dac375-159x117.svg','offizielles Header-Logo bibigo.com (CJ CheilJedang)'),
 ('berger-schinken','Berger Schinken','Markenhersteller',['Berger Schinken'],'berger-schinken.svg','https://www.berger-schinken.at/wp-content/uploads/2021/08/bergerschinken-logo-2.svg','offizielles Header-Logo berger-schinken.at'),
 ('buerger','Bürger','Markenhersteller',['Bürger','BÜRGER'],'buerger.svg','https://www.buerger.de/buerger-logo.svg','offizielles Header-Logo buerger.de (Bürger GmbH, Crailsheim; GTIN-Präfix 4075600)'),
 ('delamaris','Delamaris','Markenhersteller',['Delamaris'],'delamaris.svg','https://www.delamaris.si/wp-content/uploads/2021/01/Group-161.svg','offizielles Header-Logo delamaris.si'),
 ('dimmidisi','DimmidiSì','Markenhersteller',['DimmidiSì','DimmidiSi','Dimmidisì'],'dimmidisi.png','https://www.dimmidisi.it/wp-content/uploads/2022/04/logo-dimmidisi.png','offizielles Logo dimmidisi.it'),
 ('eismann','eismann','Markenhersteller',['Eismann','eismann'],'eismann.svg',*cm('eismann')),
 ('golfera','Golfera','Markenhersteller',['Golfera','GOLFERA'],'golfera.png','https://golfera.com/wp-content/uploads/2025/08/LOGO-GOLFERA_2025-2.webp','offizielles Header-Logo golfera.com (Golfera in Lavezzola S.p.A.; Ben-Fatto-Gerichte bei Gurkerl)'),
 ('greenforce','GREENFORCE','Markenhersteller',['GREENFORCE','Greenforce'],'greenforce.png','https://cdn.shopify.com/s/files/1/0417/0242/4737/files/GREENFORCE_Logo.png?v=1732182654&width=300','offizielles Header-Logo greenforce.com'),
 ('gue','Gü','Markenhersteller',['GÜ','Gü','Gü Puds'],'gue.png','https://cdn.shopify.com/s/files/1/1025/1252/5644/files/SEO_c6330974-1949-4c1d-996c-e874295aa199.png?v=1769701720','Wortmarke ausgeschnitten aus offiziellem og:image (gupuds.com → gudesserts.us)'),
 ('heinz','Heinz','Markenhersteller',['Heinz','HEINZ'],'heinz.svg',*cm('heinz2')),
 ('hengstenberg','Hengstenberg','Markenhersteller',['Hengstenberg'],'hengstenberg.png',*cm('hengstenberg')),
 ('hilcona','Hilcona','Markenhersteller',['Hilcona'],'hilcona.svg',*cm('hilcona')),
 ('jeden-tag','Jeden Tag','Eigenmarke',['Jeden Tag'],'jeden-tag.svg','https://www.jeden-tag.de/_assets/e6bf15f02616d4b86dc74f33fda97e9c/Images/logo.svg','offizielles Header-Logo jeden-tag.de (ZEV-Markant-Handelsmarke, bei MPreis/Unimarkt)'),
 ('kotanyi','Kotányi','Markenhersteller',['Kotányi','KOTÁNYI','Kotanyi'],'kotanyi.svg',*cm('kotanyi')),
 ('meica','Meica','Markenhersteller',['Meica','MEICA'],'meica.png','https://www.meica.de/_assets/2463467ec568880360cfe0d0f1852732/Images/Logo.png','offizielles Header-Logo meica.de'),
 ('neni','NENI','Markenhersteller',['Neni','NENI'],'neni.png','https://nenifood.com/application/images/NENI_Logo_Familymade_RGB_Falafel.png','offizielles Logo nenifood.com (NENI-Handelsprodukte)'),
 ('nongshim','Nongshim','Markenhersteller',['Nongshim','NONGSHIM'],'nongshim.svg',*cm('nongshim')),
 ('perutnina','Perutnina Ptuj','Markenhersteller',['Perutnina','Perutnina Ptuj'],'perutnina.svg',*cm('perutnina')),
 ('riso-scotti','Riso Scotti','Markenhersteller',['Riso Scotti'],'riso-scotti.png',*cm('riso-scotti')),
 ('salzburgmilch','SalzburgMilch','Markenhersteller',['SalzburgMilch','Salzburg Milch'],'salzburgmilch.png',*cm('salzburgmilch')),
 ('stadtkueche','Stadtküche','Markenhersteller',['Stadtküche'],'stadtkueche.png','https://www.kasnudl.com/wp-content/uploads/2024/01/cropped-Design-ohne-Titel3.png','offizielles Header-Logo kasnudl.com (Kasnudl GmbH, Marke Stadtküche bei Billa)'),
 ('uncle-bens','Uncle Ben\'s','Markenhersteller',["Uncle Ben's",'Uncle Bens'],'uncle-bens.svg',*cm('uncle-bens')),
 ('weight-watchers','Weight Watchers','Markenhersteller',['Weight Watchers','weight watchers','Weight'],'weight-watchers.svg',*cm('weight-watchers')),
 ('wiegert','Wiegert','Markenhersteller',['Wiegert'],'wiegert.png','https://www.wiegert.at/wp-content/uploads/2022/01/cropped-WIE-logo-11-claim-1024x553.png','offizielles Header-Logo wiegert.at'),
 ('andechser-natur','Andechser Natur','Bio',['Andechser Natur','Andechser'],'andechser-natur.svg',*cm('andechser')),
 ('bauernland','Bauernland','Markenhersteller',['Bauernland'],'bauernland.png','https://www.weinbergmaier.at/images/Logo_BL.png','offizielles Logo weinbergmaier.at (Weinbergmaier GmbH, Marke Bauernland)'),
 ('brajlovic','Brajlović','Markenhersteller',['Brajlovic','Brajlović','BRAJLOVIC'],'brajlovic.png','https://www.brajlovic.at/','offizielles Site-Icon brajlovic.at (192 px, Wix-CDN)'),
]
ALIAS={'tress-brueder':['Tressbrüder'],'planted':['Planted.'],'maggi':['Maggi, Nestlé'],'hubers-landhendl':['Hubers Landhendl','Hubers'],
 'little-lunch':['Little'],'cucina':['Cucina, Girone & Sohn Nahrungsmittel'],'knorr':['Knorr, Kaiser Teller','Knorr Kaiser Teller'],
 'food-for-future':['Food for Future, Penny'],'fit-taste':['FitTaste'],'hut-und-stiel':['Hut & Stiel'],'vegavita':['VEGA VITA VON BILLA'],
 'billa-bio':['Billabio'],'spar-natur-pur':['Spar Natur Pur'],'dr-oetker':['DR.OETKER RISTORANTE']}
P='/workspace/fertig/analysis/logos.json'
d=json.load(open(P)); added=[];aliased=[]
for slug,name,cat,brands,fn,src,orig in NEW:
  if slug in d: print('skip existing',slug); continue
  shutil.copy('final/'+fn,'/workspace/fertig/analysis/logos/'+fn)
  d[slug]=dict(slug=slug,name=name,brands=brands,logo_category=cat,file='logos/'+fn,source=src,size='svg' if fn.endswith('.svg') else 'png',note=f'{G} · {orig}',hq=True)
  added.append(slug)
for k,al in ALIAS.items():
  v=d[k]; assert v.get('file') and os.path.exists('/workspace/fertig/analysis/'+v['file']),k
  b=v.get('brands') or []; new=[a for a in al if a not in b]
  if new: v['brands']=b+new; aliased.append((k,new))
tmp=P+'.tmp'; json.dump(d,open(tmp,'w'),ensure_ascii=False,indent=1); os.replace(tmp,P)
json.dump({'run':'2026-10-13T11 Daten-Squad','added':[{k:d[k][k2] for k2 in ('name','brands','file','source','note')} for k in added],'aliases':aliased,
  'rejected':{'Findus (findus.it favicon = shape only)':'no wordmark','La Fermière (white svg / pot icon only)':'not usable on light bg','Miil (miil.at = gransy, other company)':'wrong entity','Oyakata (oyakata.de unrelated)':'wrong entity','Basenbox (favicon B+lemon only)':'no confirmed wordmark','Riso Gallo (Commons = photo of a sign)':'not a clean logo','Esterhazy (Commons = Esterhazy Betriebe, product link unverified)':'entity unverified','Thai President Foods (producer of Mama, not the Mama brand logo)':'brand != producer','alias to file-less rows (Good Choice, Chef Menü, Nature\'s Gold, Trattoria Alfredo, Vemondo, Wonnemeyer, Greisinger, Natur Aktiv, Kania, Schwaben Krone)':'no logo file exists -> no alias added'},
  'checked_unresolved':['Pappudia','dmBio','GAON','The Green Garden','Deflorian','Strauss','Mochi','M (MPreis Eigenmarke)','Milsani','AIA','Andros','Hammermühle','Della Mamma','Landtmann\'s','Elsässer','Rians','Deli Dip','Danke Bauer'],
  'generated':datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')},open('evidence.json','w'),ensure_ascii=False,indent=1)
print('added',len(added),'aliased',len(aliased),'total',len(d))
