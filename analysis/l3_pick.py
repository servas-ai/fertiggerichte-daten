import json,re
R=json.load(open('l3_pw2.json'))
def score(c):
  s=0
  if c['logo']: s+=5
  if c['kw']: s+=4
  if c['hdr']: s+=3
  if 0<=c['y']<250: s+=2
  if c['t']=='svg' or (c.get('src','').lower().split('?')[0].endswith('.svg')): s+=2
  bad=re.search(r'cookielaw|onetrust|powered_by|app-store|google-play|badge|icon|arrow|whatsapp|facebook|instagram|payment|visa|paypal|flag|search|cart|menu|close',(c.get('src','')+c.get('alt','')).lower())
  if bad: s-=10
  if c['t']=='img' and c['nw'] and c['nw']<60: s-=4
  if c['t']=='svg' and not c['svg']: s-=10
  if c['t']=='svg' and not (c['logo'] or c['kw'] or c['hdr']): s-=6
  return s
P={}
for k,v in R.items():
  key=k.split('|')[0]
  if 'err' in v: print(key,'ERR',v['err'][:80]); continue
  cs=[c for c in v['c'] if (c['t']=='img' and c['src'] and not c['src'].startswith('data:image/gif')) or c['t']=='svg']
  seen=set();cs2=[]
  for c in sorted(cs,key=score,reverse=True):
    sig=c.get('src') or c.get('svg','')[:200]
    if sig in seen: continue
    seen.add(sig);cs2.append(c)
  P[key]={'title':v['title'],'url':v['url'],'og':v['og'],'cands':cs2[:4]}
  print('##',key,'|',v['title'][:50],'|',v['url'][:60])
  for c in cs2[:3]: print('   ',score(c),c['t'],c.get('nw'),c.get('nh'),int(c['w']),int(c['y']),(c.get('alt') or '')[:25],(c.get('src') or c['svg'][:80])[-100:])
json.dump(P,open('l3_pick.json','w'),ensure_ascii=False)
