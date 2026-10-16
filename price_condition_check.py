"""Review 13 G follow-up: re-check app-only price notes ('NUR MIT APP') on the shop product page.
Run as part of the price update (before export_app.py). Respects robots.txt, >=1 s between requests per host.
Drops (active=False) a condition whose note is no longer on the page; keeps it unchanged if the page can't be fetched."""
import json, re, time, sys, urllib.request, urllib.robotparser, urllib.parse, datetime
P='price_conditions.json'; UA='GoodChoiceBot/1.0 (+price check)'
D=json.load(open(P)); last={}; rp={}
def allowed(u):
    h=urllib.parse.urlsplit(u); base=f'{h.scheme}://{h.netloc}'
    if base not in rp:
        r=urllib.robotparser.RobotFileParser(base+'/robots.txt')
        try: r.read()
        except Exception: r=None
        rp[base]=r; last[h.netloc]=time.time()
    return rp[base] is None or rp[base].can_fetch(UA,u)
for c in D['conditions']:
    u=c['source_url']; host=urllib.parse.urlsplit(u).netloc
    if not allowed(u): print('robots disallow',u); continue
    w=1.0-(time.time()-last.get(host,0))
    if w>0: time.sleep(w)
    try: html=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=20).read().decode('utf-8','ignore')
    except Exception as e: print('fetch failed, kept',u,e); last[host]=time.time(); continue
    last[host]=time.time()
    found=bool(re.search(re.escape(c['text']).replace('\\ ','\\s+'),html,re.I))
    c['checked']=datetime.date.today().isoformat(); c['active']=found
    print(c['name'],'note found' if found else 'note GONE → dropped')
json.dump(D,open(P,'w'),ensure_ascii=False,indent=1)
