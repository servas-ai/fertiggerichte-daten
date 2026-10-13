import json,re,difflib,collections,os
A=json.load(open('scored.json'))+json.load(open('expand.json'))
B=json.load(open('billa_det_extract.json'))
OV=json.load(open('ovis_codes.json'))
OFFP=json.load(open('off_prod.json'))
OFFB=json.load(open('off_brand.json')) if os.path.exists('off_brand.json') else []
FIX={'31538':'Wiesbauer Gourmet Gastro GmbH','61904':'Wilhelm Blasko Convenience-Food GmbH (Werk Bruck/Mur)','31353':'Wilhelm Blasko Convenience-Food GmbH (Werk Oberwaltersdorf)','62028':'Landgenossenschaft Ennstal / Landena (Werk Stainach-Pürgg)'}
GROUP={'32629':'REWE Group Austria','42152':'REWE Group Austria','61904':'Blasko (Aibler-Gruppe)','31353':'Blasko (Aibler-Gruppe)','62028':'Landgenossenschaft Ennstal (Landena)','30733':'GMS Gourmet (Do & Co-Beteiligung? – nicht verifiziert)'}
GROUP['30733']='GMS Gourmet GmbH'
FOREIGN={
 'DE EV 219':dict(company='Abbelen GmbH (Abbelen Fleischwaren)',town='Tönisvorst',state='Nordrhein-Westfalen',country='Deutschland',url='https://das-ist-drin.de/glossar/betriebsnummern/EV-219-Abbelen-Fleischwaren-GmbH-Co-KG--2698/'),
 'DE NW EV 215':dict(company='M+P Tiefkühlkost GmbH',town='Leopoldshöhe',state='Nordrhein-Westfalen',country='Deutschland',url='https://das-ist-drin.de/glossar/betriebsnummern/NW-EV-215-M+P-Tiefkuehlkost-GmbH--2692/'),
 'IT 221L':dict(company='Meridionale Alimenti S.r.l. (lt. blia.it-Index)',town='Avellino',state='Kampanien',country='Italien',url='https://www.blia.it/stabilimenti?c=AVELLINO'),
 'DE NI 34000':dict(company='Meica Ammerländische Fleischwarenfabrik Fritz Meinen GmbH & Co. KG (Markeninhaber, Code lt. Etikett)',town='Edewecht',state='Niedersachsen',country='Deutschland',url=None),
 'DE NE 34000':dict(company='Meica Ammerländische Fleischwarenfabrik Fritz Meinen GmbH & Co. KG (Markeninhaber, Code lt. Etikett)',town='Edewecht',state='Niedersachsen',country='Deutschland',url=None),
 'DE NW 20108':dict(company='Wonnemeyer Feinkost / Kühlmann GmbH (lt. OFF-Marke)',town=None,state='Nordrhein-Westfalen',country='Deutschland',url=None),
}
RETAIL=re.compile(r'billa ag|ja! natürlich|spar österreich|hofer kg|lidl|rewe|penny|merkur',re.I)
def norm_code(s):
  s=s.upper().replace('-',' ')
  s=re.sub(r'\s+',' ',s)
  return s
def find_codes(t):
  t=t or ''
  out=[]
  for m in re.finditer(r'\b(AT)[ -]?(\d{4,5})[ -]?E[GUC]\b',t): out.append(('AT',m.group(2)))
  for m in re.finditer(r'\bDE[ -]?(?:([A-Z]{2})[ -]?)?(EV|[0-9]{0})[ -]?(\d{2,6})[ -]?E[GU]\b',t):
    pre=('DE '+(m.group(1)+' ' if m.group(1) else '')+m.group(2)+' '+m.group(3)).replace('  ',' ')
    out.append(('X',pre))
  for m in re.finditer(r'\bDE[ -]([A-Z]{2})[ -](\d{3,6})[ -]E[GU]\b',t): out.append(('X',f'DE {m.group(1)} {m.group(2)}'))
  for m in re.finditer(r'\bIT[ -]?(\w{2,6})[ -]?(?:EU|CE)\b',t): out.append(('X','IT '+m.group(1)))
  for m in re.finditer(r'\bPL[ -]?(\d{6,10})\b',t): out.append(('X','PL '+m.group(1)))
  return out
def resolve(c):
  if c[0]=='AT':
    o=OV.get(c[1])
    if o: return dict(producer_company=FIX.get(c[1],o['company']),plant_code=f'AT {c[1]} EU',plant_town=o['town'],plant_state=o['state'],country='Österreich',evidence_url='https://vis.statistik.at/fileadmin/ovis/pdf/'+o['list']+'.pdf',_group=GROUP.get(c[1]))
    return dict(producer_company=None,plant_code=f'AT {c[1]} EU',plant_town=None,plant_state=None,country='Österreich',evidence_url=None,_unres=True)
  f=FOREIGN.get(c[1])
  if f: return dict(producer_company=f['company'],plant_code=c[1]+' EU',plant_town=f['town'],plant_state=f['state'],country=f['country'],evidence_url=f['url'])
  return dict(producer_company=None,plant_code=c[1],plant_town=None,plant_state=None,country=None,evidence_url=None,_unres=True)
def meat(r,x):
  bits=[]
  if r:
    for k,l in [('meatBorn','geboren'),('meatRaised','aufgezogen'),('meatSlaughtered','geschlachtet'),('meatButchered','zerlegt')]:
      if r.get(k): bits.append(f"{l}: {r[k]}")
    m=r.get('mand') or ''
    for l in m.split('\n'):
      if re.search(r'geboren|aufgezogen|geschlachtet|zerlegt',l): bits.append(l.strip())
    ing=r.get('ingr') or ''
    for mm in re.finditer(r'([A-ZÄÖÜa-zäöü]*(?:fleisch|Huhn|Hühner|Rind|Schwein|Pute)[a-zäöü]*)[^,;()]{0,40}?\(?(?:aus|Herkunft:?)\s+(Österreich|Deutschland|der EU|EU|Nicht-EU|Brasilien|Thailand|Polen|Ungarn|Italien)',ing): bits.append(f"{mm.group(1)} aus {mm.group(2)}")
    for mm in re.finditer(r'([^,;:()]{3,40}?)\s*(?:\(|,)?\s*(?:aus|Herkunft:?|Ursprung:?)\s+(Österreich|Deutschland|der EU|EU|Nicht-EU|Brasilien|Thailand|Polen|Ungarn|Italien|Spanien|Niederlande|Irland|China)',ing):
      if re.search(r'fleisch|huhn|hühner|hendl|rind|schwein|pute|kalb|speck|schinken|lachs|wurst',mm.group(1),re.I): bits.append(re.split(r'[\n.*]+',mm.group(1))[-1].strip()+' aus '+mm.group(2))
    if re.search(r'AMA[ -]?Gütesiegel',ing+m): bits.append('AMA-Gütesiegel')
  if re.search(r'\bAMA\b',x['name']): bits.append('AMA (lt. Name)')
  return '; '.join(dict.fromkeys(bits)) or None
# OFF brand index
offidx=[]
for p in OFFB:
  if p.get('emb_codes') and p.get('product_name'): offidx.append((re.sub(r'[^a-zäöüß0-9 ]','',p['product_name'].lower()),p))
def nm(s): return re.sub(r'[^a-zäöüß0-9 ]','',(s or '').lower())
seen={}
for x in A:
  k=(x['name'],x['store'])
  if k not in seen or sum(v is not None for v in x.values())>sum(v is not None for v in seen[k].values()): seen[k]=x
A=list(seen.values())
out=[];stat=collections.Counter()
for x in A:
  rec=dict(name=x['name'],store=x['store'],brand=x.get('brand'),producer_company=None,plant_code=None,plant_town=None,plant_state=None,country=None,confidence=None,evidence_url=None,meat_origin=None,label_distributor=None,url=x.get('url'),note=None)
  r=None
  m=re.search(r'-(\d{8})$',x.get('url') or '')
  if m:
    sku=m.group(1)[:2]+'-'+m.group(1)[2:]; r=B.get(sku)
  codes=[]
  if r: codes=find_codes((r.get('mand') or ''))
  if not codes and x.get('producer_id'): codes=find_codes(x['producer_id']); src0='pid'
  ean=None
  if 'openfoodfacts' in (x.get('url') or ''):
    ean=x['url'].rstrip('/').split('/')[-1]; p=OFFP.get(ean) or {}
    if p.get('emb_codes'): codes+=find_codes(p['emb_codes'])
    if p.get('manufacturing_places'): rec['note']='OFF manufacturing_places: '+p['manufacturing_places']
  src='billa' if r and codes else ('off' if codes else None)
  if not codes and not r and x.get('store') and 'SPAR' in str(x['store']).upper() or (not codes and not r and not ean):
    n=nm(x['name']); best=None;bs=0
    for k,p in offidx:
      s=difflib.SequenceMatcher(None,n,k).ratio()
      if s>bs: bs,best=s,p
    if best and bs>=0.9:
      c2=find_codes(best['emb_codes'])
      if c2: codes=c2; src='offname'; rec['note']=f"OFF Namensmatch {bs:.2f}: {best['product_name']} ({best['code']})"; ean=best['code']
  if codes:
    res=resolve(codes[0]); rec.update({k:v for k,v in res.items() if not k.startswith('_')})
    if res.get('_group'): rec['owner_group']=res['_group']
    if res.get('_unres'): rec['confidence']='confirmed-code (unresolved)'
    else: rec['confidence']='confirmed-code'
    if src=='billa': rec['code_source']='BILLA Online-Shop Pflichtangabe (mandatoryIndicator)'
    else: rec['code_source']='Open Food Facts emb_codes'+(' (crowdsourced)' if True else ''); 
    if src!='billa' and not rec['evidence_url']: rec['evidence_url']=f'https://world.openfoodfacts.org/product/{ean}'
    if len(codes)>1: rec['note']=((rec['note'] or '')+' weitere Codes: '+', '.join(' '.join(c) for c in codes[1:])).strip()
  mf=(x.get('manufacturer') or (r or {}).get('maddr') or '').strip()
  if mf:
    first=mf.split('\n')[0].split(',')[0].strip()
    if RETAIL.search(first): rec['label_distributor']=mf.replace('\n',', ')
    elif not rec['producer_company']:
      rec['producer_company']=first; rec['confidence']='label-address'; rec['evidence_url']=x.get('url')
      am=re.search(r'(\d{4})\s+([A-ZÄÖÜ][\wäöüß\.\- ]+)',mf)
      if am: rec['plant_town']=am.group(2).strip(); 
      rec['note']=((rec['note'] or '')+' Herstelleradresse lt. Etikett (Firmensitz, nicht zwingend Werk): '+mf.replace('\n',', ')).strip()
      if 'Fit2go' in mf: rec['confidence']='recall/press'; rec['producer_company']='Fit2go GmbH (Pucking); Produktion lt. Krone-Bericht in Wiener Manufaktur'
  rec['meat_origin']=meat(r,x)
  rec['product_origin_label']=(r or {}).get('country') or x.get('origin')
  if not rec['producer_company'] and not rec['plant_code']:
    rec['confidence']='unknown'
  stat[rec['confidence']]+=1
  out.append(rec)
json.dump(out,open('_prod_tmp.json','w'),ensure_ascii=False)
print(len(out),stat)
print(collections.Counter(r['plant_code'] for r in out if r['plant_code']).most_common(40))
