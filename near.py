import json,urllib.request,urllib.parse,math,re
LAT,LON=48.3102805,14.2992021
d=json.load(open('ovp.json'))
CH={'Billa':r'^billa','Spar':r'spar','Hofer':r'hofer|aldi','Lidl':r'lidl','Penny':r'penny','dm':r'^dm\b|dm-drogerie|dm drogerie'}
def hav(a,b,c,e):
    R=6371000;p1,p2=math.radians(a),math.radians(c);dp=p2-p1;dl=math.radians(e-b)
    return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
shops=[]
for el in d['elements']:
    t=el.get('tags',{}); nm=(t.get('brand') or t.get('name') or '')
    lat=el.get('lat') or el.get('center',{}).get('lat'); lon=el.get('lon') or el.get('center',{}).get('lon')
    for ch,pat in CH.items():
        if re.search(pat,nm,re.I):
            if ch=='Spar' and re.search(r'sparkasse',nm,re.I): continue
            addr=' '.join(filter(None,[t.get('addr:street'),t.get('addr:housenumber')]))+(', '+t.get('addr:postcode','')+' '+t.get('addr:city','') if t.get('addr:postcode') else '')
            shops.append(dict(chain=ch,name=t.get('name') or nm,addr=addr.strip(', ') or None,lat=lat,lon=lon,dist=round(hav(LAT,LON,lat,lon)),hours=t.get('opening_hours')))
            break
shops.sort(key=lambda s:s['dist'])
# walking via OSRM foot for nearest 4 per chain
cnt={}
for s in shops:
    cnt[s['chain']]=cnt.get(s['chain'],0)+1
    if cnt[s['chain']]>4: continue
    try:
        u=f"https://routing.openstreetmap.de/routed-foot/route/v1/foot/{LON},{LAT};{s['lon']},{s['lat']}?overview=false"
        r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'fertig-research/1.0'}),timeout=20))
        s['walk_m']=round(r['routes'][0]['distance']); s['walk_min']=round(r['routes'][0]['duration']/60)
    except Exception as e: pass
    if not s['addr']:
        try:
            g=json.load(urllib.request.urlopen(urllib.request.Request(f"https://nominatim.openstreetmap.org/reverse?lat={s['lat']}&lon={s['lon']}&format=json",headers={'User-Agent':'fertig-research/1.0'}),timeout=15))
            a=g.get('address',{}); s['addr']=f"{a.get('road','')} {a.get('house_number','')}, {a.get('postcode','')} {a.get('city') or a.get('town','')}".strip()
        except: pass
    s['gmaps']=f"https://www.google.com/maps/dir/?api=1&origin={LAT},{LON}&destination={s['lat']},{s['lon']}&travelmode=walking"
out=dict(home=dict(addr='Gruberstraße 19, 4020 Linz',lat=LAT,lon=LON),shops=[s for s in shops if 'gmaps' in s])
json.dump(out,open('/workspace/fertig-app/public/stores.json','w'),ensure_ascii=False)
for s in out['shops']: print(s['chain'],s['name'],s['addr'],s['dist'],s.get('walk_m'),s.get('walk_min'))
