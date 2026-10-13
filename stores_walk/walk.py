import json,math,time,urllib.request
H=(48.3102805,14.2992021)
E=json.load(open('osm.json'))['elements']
S=[]
for e in E:
    t=e.get('tags',{});lat=e.get('lat') or e['center']['lat'];lon=e.get('lon') or e['center']['lon']
    S.append(dict(osm=f"{e['type']}/{e['id']}",name=t.get('name') or t.get('brand') or '(ohne Name)',brand=t.get('brand'),shop=t.get('shop'),
     addr=' '.join(filter(None,[t.get('addr:street'),t.get('addr:housenumber')]))+(', '+t['addr:postcode']+' '+t.get('addr:city','') if t.get('addr:postcode') else ''),
     lat=lat,lon=lon,hours=t.get('opening_hours'),cuisine=t.get('cuisine'),source='OpenStreetMap Overpass (ODbL), fetched 2026-10-13'))
import csv
ids={x['osm'] for x in S}
for r in csv.DictReader(open('/workspace/fertiggerichte-daten/data/stores.csv')):
    k=f"{r['osm_type']}/{r['osm_id']}"
    if k in ids: continue
    la,lo=float(r['lat']),float(r['lon'])
    if abs(la-H[0])>0.02 or abs(lo-H[1])>0.03: continue
    S.append(dict(osm=k,name=r['name'],brand=r['chain'] if 'sonstige' not in r['chain'] else None,shop='supermarket' if 'Supermarkt' in r['chain'] else 'convenience' if 'Convenience' in r['chain'] else None,
      addr=f"{r['street']} {r['housenumber']}, {r['postcode']} {r['city']}".strip(),lat=la,lon=lo,hours=r['opening_hours'] or None,cuisine=None,source='OpenStreetMap via fertiggerichte-daten/data/stores.csv (ODbL, fetched '+r['fetched_at']+')'))
def hv(a,b,c,d):
    R=6371000;p=math.radians;x=math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2;return 2*R*math.asin(math.sqrt(x))
for i in range(0,0 if __import__("os").environ.get("NOOSRM") else len(S),90):
    ch=S[i:i+90];coords=';'.join([f"{H[1]},{H[0]}"]+[f"{s['lon']},{s['lat']}" for s in ch])
    u=f"https://routing.openstreetmap.de/routed-foot/table/v1/foot/{coords}?sources=0&annotations=duration,distance"
    try:
        r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'servas-fertig/1.0'}),timeout=60))
        for s,du,di in zip(ch,r['durations'][0][1:],r['distances'][0][1:]):
            s['walk_m']=round(di);s['walk_min']=math.ceil(du/60);s['walk_method']='OSRM foot (routing.openstreetmap.de)'
    except Exception as ex: print('osrm fail',ex)
    time.sleep(1.5)
S=[s for s in S if hv(H[0],H[1],s['lat'],s['lon'])<=2000]
for s in S:
    s['dist_m']=round(hv(H[0],H[1],s['lat'],s['lon']))
    if 'walk_min' not in s:
        s['walk_m']=round(s['dist_m']*1.3);s['walk_min']=math.ceil(s['walk_m']/80);s['walk_method']='haversine*1.3 @4.8km/h (fallback)'
    s['walk_band']='5' if s['walk_min']<=5 else '10' if s['walk_min']<=10 else '15' if s['walk_min']<=15 else '20+'
    b=(s['brand'] or s['name']).lower()
    s['chain']=next((c for c in ['Billa','Spar','Hofer','Lidl','Penny','MPreis','Unimarkt','dm','Bipa','Nah&Frisch','ADEG'] if c.lower().replace('&',' & ') in b.replace('&',' & ') or c.lower() in b),None)
    s['type']='chain' if s['chain'] else ('ethnic/local' if s['shop'] in('supermarket','convenience','general','food') else s['shop'])
    s['availability_level']='chain' if s['chain'] else 'none (no product source)'
S.sort(key=lambda s:s['walk_min'])
gur={'name':'Gurkerl','type':'delivery','delivers_4020':None,'source':'TBD'}
json.dump({'home':{'addr':'Gruberstraße 19, 4020 Linz','lat':H[0],'lon':H[1]},'generated':'2026-10-13','stores':S},open('stores_linz_walk.json','w'),ensure_ascii=False,indent=1)
import collections as C
print(len(S),C.Counter(s['walk_band'] for s in S),C.Counter(s['type'] for s in S),C.Counter(s['walk_method'] for s in S))
print([(s['name'],s['walk_min']) for s in S[:15]])
