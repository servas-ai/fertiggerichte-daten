import json,re,os,io,requests,shutil,subprocess,urllib3
from urllib.parse import quote
from PIL import Image
urllib3.disable_warnings()
U={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/129 Safari/537.36"}
WH={"User-Agent":"fertig-research/1.0 (logo research)"}
P2=json.load(open('l3_pw2.json')); P1=json.load(open('l3_pw1.json'))
def find(job,sub,src=P2):
  for k,v in src.items():
    if k.split('|')[0]==job and 'c' in v:
      for c in v['c']:
        if c['t']=='img' and sub.lower() in c['src'].lower(): return c['src']
  return None
def inline_svg(job,sub):
  for k,v in P2.items():
    if k.split('|')[0]==job and 'c' in v:
      for c in v['c']:
        if c['t']=='svg' and c['svg'] and sub in c['svg'][:400]: return c['svg']
def spar_orig(u):  # strip AEM rendition -> original asset
  return u.split('/jcr:content')[0] if u else None
def wm(fn):
  j=requests.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',titles='File:'+fn,prop='imageinfo',iiprop='url',format='json'),headers=WH,timeout=20).json()
  return list(j['query']['pages'].values())[0]['imageinfo'][0]['url']
SC='https://dm.emea.cms.aldi.cx/is/image/aldiprodeu/'
K='https://assets-eu-01.kc-usercontent.com:443/d5bbd8c1-f776-012f-71ae-f309933a3006/'
EXIST='/workspace/fertig/analysis/logos/'
# brand -> (slug, category, source spec, note)
S={}
def a(names,slug,cat,src,note=None,site=None):
  for n in ([names] if isinstance(names,str) else names): S[n]=dict(slug=slug,cat=cat,src=src,note=note,site=site)
# chains
a('Billa','billa','Handelskette',('file','billa.svg')); a('Spar','spar','Handelskette',('file','spar.svg')); a('SPAR','spar','Handelskette',('file','spar.svg'))
a('Hofer','hofer','Handelskette',('wm','Hofer Logo 2017.svg')); a('Lidl','lidl','Handelskette',('file','lidl.svg'))
a('Penny','penny','Handelskette',('file','penny.svg')); a('dm','dm','Handelskette',('file','dm.svg'))
# Billa
a('BILLA Immer Gut','immer-gut','Eigenmarke',('file','immer-gut.png')); a('BILLA Genusswelt','billa-genusswelt','Eigenmarke',('file','billa-genusswelt.png'))
a('Omis Schmankerl','omis-schmankerl','Eigenmarke',('file','omis-schmankerl.png')); a('Simply Good','simply-good','Eigenmarke',('file','simply-good.png'))
a('Vegavita','vegavita','Eigenmarke',('url',K+'b961241e-7b3d-4e9f-b155-5217795a7bc4/Vegavita_Logo.svg','extract'))
a('CLEVER','clever','Budget',('file','clever.png')); a('BILLA Bio','billa-bio','Bio',('url',K+'5e4de8a9-d343-4cf3-96c9-dcb63e21fb96/Billa_Bio_Logo.svg','extract'))
a('Ja! Natürlich','ja-natuerlich','Bio',('file','ja-natuerlich.svg'))
# Spar
a('S-BUDGET','s-budget','Budget',('url',spar_orig(find('spar:s-budget','s-budget-logo')),None))
a('SPAR PREMIUM','spar-premium','Eigenmarke',('url',spar_orig(find('spar:spar-premium','spar-premium-logo')),None))
a('SPAR Feine Küche','spar-feine-kueche','Eigenmarke',('url',spar_orig(find('spar:spar-feine-kueche','feine-kueche-spar-logo')),None))
a('SPAR Veggie','spar-veggie','Eigenmarke',('url',spar_orig(find('spar:spar-veggie','spar-veggie-logo')),None))
a('SPAR Vital','spar-vital','Eigenmarke',('url',spar_orig(find('spar:spar-vital','vital-logo-web')),None))
a('SPAR Natur*pur','spar-natur-pur','Bio',('url',spar_orig(find('spar:spar-natur-pur','logo-color-pantone')),None))
a('DESPAR','despar','Eigenmarke',('url',spar_orig(find('spar:despar','DESPAR-Logo')),None))
a('SPAR enjoy','spar-enjoy','Eigenmarke',None,'only white-on-transparent logo on spar.at; not used')
# Hofer
a('Le Gusto','le-gusto','Eigenmarke',('url',SC+'2026_MA_Brandpage-Logo_Le-Gusto:1-1?wid=800&fit=constrain',None))
a(['Cucina','Cucina Nobile'],'cucina','Eigenmarke',('url',SC+'2026_MA_Brandpage-Logo_Cucina:1-1?wid=800&fit=constrain',None),'Hofer brand page /marken/cucina (Cucina Nobile merged into Cucina)')
a('Almare','almare','Eigenmarke',('url',SC+'2026_MA_Brandpage-Logo_ALMARE:1-1?wid=800&fit=constrain',None))
a('GOURMET FINEST CUISINE','hofer-gourmet','Eigenmarke',('url',SC+'2026_MA_Brandpage-Logo_GOURMET:1-1?wid=800&fit=constrain',None),'Hofer GOURMET brand logo')
a('SONNHOF','sonnhof','Eigenmarke',('url',SC+'Brandpage-Logo_Sonnhof_386x386px:1-1?wid=800&fit=constrain',None))
a('FairHOF','fairhof','Eigenmarke',('url',SC+'2026_MA_Brandpage-Logo_Fairhof:1-1?wid=800&fit=constrain',None))
for n in ['Good Choice','Primana','Asia','Green Garden',"Nature's Gold","PIZZ'AH","Leibspeis'",'Natur Aktiv','Rettenswert','Wonnemeyer']:
  a(n,re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-'),'Bio' if n=='Natur Aktiv' else 'Eigenmarke',None,'Hofer private label: no logo published on hofer.at brand pages')
# Lidl/Penny
for n in ['Chef Select','Vemondo','Deluxe','Vitasia','MCENNEDY','Schwaben Krone','SELECT&GO','Trattoria Alfredo','Kania']:
  a(n,re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-'),'Eigenmarke',None,'Lidl private label: no official logo asset found')
a('Food for Future','food-for-future','Eigenmarke',('url','https://assets-eu-01.kc-usercontent.com:443/1d32d597-5ed5-0129-acbb-0e3925686fcc/2f2e48b1-b6da-4c09-a80f-623b2c5ce926/Food_for_Future_Logo_4c.svg',None))
a(['Delikatessa','Chef Menü'],None,'Eigenmarke',None,'no logo found')
# Markenhersteller
a('Knorr','knorr','Markenhersteller',('wm','Knorr Logo 2020.svg')); a('Maggi','maggi','Markenhersteller',('wm','Maggi logo.svg'))
a('iglo','iglo','Markenhersteller',('file','iglo.png')); a('Felix','felix','Markenhersteller',('file','felix.svg'))
a('Inzersdorfer','inzersdorfer','Markenhersteller',('file','inzersdorfer.png')); a('Rana','rana','Markenhersteller',('file','rana.png'))
a('Fit to Go','fit-to-go','Markenhersteller',('file','fit-to-go.png')); a('Planted','planted','Markenhersteller',('file','planted.svg'))
a('Barilla','barilla','Markenhersteller',('file','barilla.svg')); a('Frosta','frosta','Markenhersteller',('file','frosta.svg'))
a("Ben's Original",'ben-s-original','Markenhersteller',('file','ben-s-original.svg')); a('Hipp','hipp','Bio',('file','hipp.svg'))
a('Alnatura','alnatura','Bio',('file','alnatura.svg')); a('Kikkoman','kikkoman','Markenhersteller',('wm','Kikkoman-Logo.svg'))
a('Recheis','recheis','Markenhersteller',('wm','Recheis Logo.svg')); a('Mowi','mowi','Markenhersteller',('wm','Mowi ASA logo.svg'))
a('Schär','schaer','Markenhersteller',('url','https://www.schaer.com/themes/custom/schaer_radix/logo.svg',None))
a('Toni Kaiser','toni-kaiser','Markenhersteller',('url','https://www.tonikaiser.at/images/Logo_TK.svg',None))
a('Reis-Fit','reis-fit','Markenhersteller',('url','https://www.reis-fit.de/wp-content/uploads/2025/11/Logo.svg',None))
a('Little Lunch','little-lunch','Bio',('url','https://littlelunch.com/wp-content/uploads/2025/10/LL_Logo_2024_web_rand.svg',None))
a('Gavrilovic','gavrilovic','Markenhersteller',('url','https://www.gavrilovic.com/wp-content/uploads/2026/02/gavrilovic-logo-gdpr.png',None))
a('Nabio','nabio','Bio',('url','https://nabio.de/wp-content/uploads/2022/03/L_Nabio_b.svg',None))
a('Aumaerk','aumaerk','Markenhersteller',('url','https://aumaerk.com/cdn/shop/files/logo_1.svg',None))
a('BioVegan','biovegan','Bio',('url','https://www.biovegan.de/cdn/shop/files/Logo_BIOVEGAN_GmbH.png?width=1180',None))
a('Fratelli Barbaro','fratelli-barbaro','Markenhersteller',('url','https://www.barbaro-shop.com/cdn/shop/files/logo-barbaro.png?width=1100',None),'barbaro-shop.com (Barbaro family shop selling Fratelli Barbaro)')
a('Vier Diamanten','vier-diamanten','Markenhersteller',('url','https://vierdiamanten.com/wp-content/uploads/sites/23/2023/03/logo-neu.png',None))
a('Steirerkraft','steirerkraft','Markenhersteller',('url','https://www.steirerkraft.com/wp-content/uploads/2026/08/logo-steirerkraft-2026.svg',None))
a('Fit Taste','fit-taste','Markenhersteller',('url',(find('ext:Fit Taste','Fittaste_Logo') or '').replace('_100x.png','_600x.png'),None))
a('Natur Compagnie','natur-compagnie','Bio',('url','https://www.natur-compagnie.com/de/assets/static-images/logo.png',None))
a('Knödelwerkstatt','knoedelwerkstatt','Markenhersteller',('url',find('ext:Knödelwerkstatt','KnoedelwerkstattLogo'),None))
a('Efko','efko','Markenhersteller',('url','https://www.efko.at/wp-content/uploads/2025/03/efko-logo.png',None))
a("Limoni's",'limonis','Bio',('url','https://limonis.at/wp-content/uploads/2021/08/Limonis-Logo-180x73.png',None))
a('Goldblatt','goldblatt','Bio',('url','https://goldblatt.at/cdn/shop/files/goldblatt-logo-2026_fuer-Shop.svg?v=1790321040',None))
a('Hut&Stiel','hut-und-stiel','Markenhersteller',('url','https://www.hutundstiel.at/cdn/shop/files/H_S_logo_font_1.png',None))
a('Tress Brüder','tress-brueder','Bio',('url','https://www.tressbrueder.de/tressbrueder-logo.svg',None))
a('Iss mich!','iss-mich','Bio',('url','https://www.issmich.at/media/6a/g0/4e/1706898229/logo_issich_132x132_nobg.png',None))
a('Revo','revo','Markenhersteller',('url','https://revo-foods.com/wp-content/themes/FoundationPress/dist/assets/images/logo-black.svg',None),'assumed Revo Foods (Vienna)')
a('Eden','eden','Bio',('url','https://www.eden.de/wp-content/uploads/2023/11/EDEN-Logo_2023-Kopie-2.gif',None))
a('Holle','holle','Bio',('url','https://www.holle.ch/wp-content/uploads/2022/07/HOLLE-Logo-DE.svg',None))
a('Ströck','stroeck','Markenhersteller',('url','https://stroeck.at/wp-content/themes/stroeck/gfx/strock.svg',None))
a(['Hofstädter','Die Grillerei'],'hofstaedter','Markenhersteller',('url',find('billa-eigen','Hofst',P1),None),'logo tile from billa.at Eigenmarken page (Die Grillerei is a Hofstädter line)')
# producers
a('Radatz','radatz','Produzent/Werk',('file','radatz.png')); a('Hink Wien','hink','Produzent/Werk',('file','hink.svg'))
a('GMS Gourmet','gms-gourmet','Produzent/Werk',('file','gms-gourmet.png')); a('Greisinger','greisinger','Produzent/Werk',None,'no official site/logo')
for n in ['Cecchin','Stangl','Amlacher','Ackerl','Pure','Ager','Youcook','Njami','Feelfood','Marinus','Staudinger','Mühlen','Sushitime','Pop-Up','franuí','Ablinger','Indomie','Blue Elephant','Jürgen Langbein','Küchenbrüder','Lorado','DOVGAN','Every','My Vay','Auinger','Flotte Lotte','Ben Fatto','Bio Natura']:
  if n not in S: a(n,re.sub(r'[^a-z0-9]+','-',n.lower().replace('ü','ue').replace('í','i')).strip('-'),'Bio' if n=='Bio Natura' else 'Markenhersteller',None,'no verified official logo found (site missing, parked, captcha or ambiguous)')
json.dump(S,open('l3_spec.json','w'),indent=1,ensure_ascii=False)
B=json.load(open('l3_brands.json')); miss=[b for b in B if b not in S]; print('unmapped',miss)
