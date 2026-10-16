"""evi.gv.at /f/<FN> (official Firmenbuch publication platform; robots allows /f/, /s search never used), 1 req/s."""
import json, time, urllib.request, re, html, datetime
d=json.load(open('../../data/companies.json'))
UA={'User-Agent':'servas-fertiggerichte-daten/1.0 (https://github.com/servas-ai/fertiggerichte-daten; data squad)'}
def dd(t,label):
    m=re.search(r'<dt[^>]*>'+re.escape(label)+r'</dt><dd[^>]*>(.*?)</dd>',t,re.S)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',m.group(1)))).strip() if m else None
out={}
for r in d:
    fn=(r.get('fn') or '').replace('FN','').strip().replace(' ','')
    if not re.fullmatch(r'\d+[a-z]',fn): continue
    u=f'https://www.evi.gv.at/f/{fn}'
    try:
        t=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read().decode('utf-8','replace')
    except Exception as e:
        out[r['slug']]={'url':u,'error':str(e)}; print(r['slug'],'ERR',e); time.sleep(1); continue
    title=re.search(r'<title>(.*?)</title>',t,re.S)
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',t,re.S)
    gs=[]
    m=re.search(r'<h3[^>]*>Gesellschafter/in</h3>(.*?)</details>',t,re.S)
    if m:
        for li in re.findall(r'<li[^>]*>(.*?)</li>',m.group(1),re.S):
            a=re.search(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',li,re.S)
            pn=re.search(r'<p class="text-lg[^"]*">(.*?)</p>',li,re.S)
            nm=a.group(2) if a else (pn.group(1) if pn else '')
            gs.append({'href':a.group(1) if a else None,'name':html.unescape(re.sub(r'<[^>]+>','',nm)).strip()})
        npers=re.search(r'<p class="text-sm text-gray-600">([^<]+)</p>',m.group(1)[:0] or '') 
    cnt=re.search(r'<h3[^>]*>Gesellschafter/in</h3><p[^>]*>([^<]+)</p>',t)
    out[r['slug']]={'url':u,'fetched_at':datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'name':html.unescape(re.sub(r'<[^>]+>','',h1.group(1))).strip() if h1 else None,
        'status':dd(t,'Status'),'eintragungsdatum':dd(t,'Eintragungsdatum'),'rechtsform':dd(t,'Rechtsform'),
        'stammkapital':dd(t,'Stammkapital'),'geschaeftszweig':dd(t,'Geschäftszweig'),'sitz':dd(t,'Sitz'),
        'gesellschafter_count':cnt.group(1) if cnt else None,'gesellschafter_links':gs,
        'row_legal_name':r['legal_name']}
    o=out[r['slug']]; print(r['slug'],'|',o['name'],'|',o['status'],'|',o['eintragungsdatum'],'|',o['stammkapital'],'|',o['gesellschafter_count'],[(g['href'],g['name']) for g in gs])
    time.sleep(1.1)
json.dump(out,open('evi_out.json','w'),ensure_ascii=False,indent=1)
