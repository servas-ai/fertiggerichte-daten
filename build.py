import json,re,html,collections,statistics as st
d=json.load(open('scored.json')); S=json.load(open('packaging_stats.json'))
def store(x):
    s=str(x.get('store') or '').lower()
    for k,v in [('nah&frisch','Nah&Frisch'),('nah & frisch','Nah&Frisch'),('nahundfrisch','Nah&Frisch'),('adeg','ADEG'),('nordsee','NORDSEE'),('subway','Subway'),('fit to go','Fit to Go'),('fittaste','FitTaste'),('fit taste','FitTaste'),('prepmymeal','PrepMyMeal'),('livefresh','LiveFresh'),('juit','Juit'),('bofrost','bofrost*'),('gurkerl','Gurkerl'),('interspar','Spar'),('spar','Spar'),('billa','Billa'),('merkur','Billa'),('hofer','Hofer'),('aldi','Hofer'),('lidl','Lidl'),('penny','Penny'),('dm','dm'),('denn','Denn\'s'),('mpreis','MPreis'),('unimarkt','Unimarkt'),('gourmetfein','Gourmetfein')]:
        if k in s: return v
    return 'unbekannt (OFF)'
def f(v):
    try: return float(v)
    except: return None
R=[]
for x in d:
    if not x.get('is_meal'): continue
    k=f(x.get('kcal_100')); p=f(x.get('protein_100')); sz=f(x.get('size_g'))
    pp=f(x.get('protein_pack')) or (round(p*sz/100,1) if p is not None and sz else None)
    R.append(dict(dishKey=x.get('dish_key'),dish=x.get('dish'),img=x.get('image_url'),name=(x.get('name') or '').strip(),brand=x.get('brand') or '',store=store(x),pack=x['packaging'],
      price=f(x.get('price_eur')),pstat=x.get('price_status'),ppk=f(x.get('price_per_kg')),size=sz,protpack=pp,p100=p,p100k=x.get('protein_per_100kcal'),kcal=k,
      kcalpack=f(x.get('kcal_pack')) or (round(k*sz/100) if k and sz else None),salt=f(x.get('salt_100')),sat=f(x.get('satfat_100')),fib=f(x.get('fiber_100')),
      score=x.get('health_score'),rankable=x.get('rankable'),dry=x.get('dry'),incomplete=x.get('incomplete'),flags=x.get('flags',[]),ppe=x.get('protein_per_euro'),pid=x.get('producer_id'),
      herst=x.get('producer_company') or (str(x.get('manufacturer') or '').split('\n')[0][:80]),ort=x.get('producer_town') or '',ooe=x.get('ooe'),
      mp=x.get('instantpot') or '',url=x.get('url')))
print('rows',len(R),collections.Counter(r['store'] for r in R))
# Top lists
top_h=sorted([r for r in R if r['score'] is not None and r['rankable']],key=lambda r:-r['score'])[:30]
top_pe=sorted([r for r in R if r['rankable'] and r['ppe'] and r['pstat']=='live 2026' and r['pack']!='Trocken/Instant' and not re.search(r'soja geschnetzel',r['name'],re.I)],key=lambda r:-r['ppe'])[:30]
# same producer
G=collections.defaultdict(list)
for r in R:
    if r['pid']: G[re.sub(r'[^A-Z0-9]','',r['pid'].upper())].append(r)
same=[(k,v) for k,v in G.items() if len({(r['brand'] or '').lower().split()[0] if r['brand'] else '' for r in v})>1 or len({r['store'] for r in v})>1]
same.sort(key=lambda kv:-len(kv[1]))
# Fit to Go vs Supermarkt
ftg=[r for r in R if r['store']=='Fit to Go']
sup=[r for r in R if r['store']!='Fit to Go' and r['protpack'] and r['price'] and r['pstat']=='live 2026' and (r['size'] or 0)>=300]
def md(L,k):
    v=[r[k] for r in L if r[k] is not None]; return round(st.median(v),2) if v else None
cmp=[('Fit to Go',ftg),('Supermarkt-Gerichte ≥300 g (live Preis)',sup),('Supermarkt Top-30 Protein/€',top_pe)]
# Kombi-Ideen
mains=[r for r in R if not re.search(r'soja geschnetzel',r['name'],re.I) and r['pack']!='Trocken/Instant' and r['protpack'] and 25<=r['protpack']<=80 and (r['kcalpack'] or 0)<=800 and r['kcalpack'] and r['price'] and r['score'] is not None and r['pstat']=='live 2026']
veg=[r for r in R if r['pack']!='Trocken/Instant' and not re.search(r'brühe|eintopf|suppe|fond|topf|ravioli|tortell|lasagne|pizza|strudel|knödel|laibchen|burger|nuggets|knacker|wurst',r['name'],re.I) and r['store']!='Fit to Go' and (r['protpack'] or 0)<15 and not re.search(r'huhn|hühn|rind|schwein|fleisch|lachs|reis|nudel|pasta|curry',r['name'],re.I) and re.search(r'gemüse|brokkoli|broccoli|fisolen|erbsen|spinat|karfiol|kohlsprossen|ratatouille|letscho',r['name'],re.I) and not re.search(r'suppe|lasagne|strudel|pizza|knödel',r['name'],re.I) and r['kcalpack'] and r['price']]
kn=[r for r in R if r['pack']!='Trocken/Instant' and not re.search(r'brühe|eintopf|suppe|fond|topf|teller',r['name'],re.I) and r['store']!='Fit to Go' and (r['protpack'] or 0)<20 and re.search(r'^(?!.*(huhn|hühn|rind|schwein|curry|sauce|soße|gulasch)).*(knödel|reis\b|erdäpfel|kartoffel|gnocchi|püree)',r['name'],re.I) and r['kcalpack'] and r['price'] and (r['p100'] or 0)<12 and not re.search(r'suppe|grammel|faschiert|fleisch|speck',r['name'],re.I)]
combos=[]
for m in sorted(mains,key=lambda r:-r['score'])[:25]:
    best=None
    for v in veg[:200]:
        for k in ([None] if re.search(r'reis|kartoffel|erdäpfel|püree|nudel|pasta|spätzle',m['name'],re.I) else kn[:200]):
            K=k or {'kcalpack':0,'protpack':0,'price':0,'name':'– (Beilage schon enthalten)','store':''}
            kc=m['kcalpack']+v['kcalpack']/2+K['kcalpack']/2  # halbe Packung Beilage
            pr=m['protpack']+(v['protpack'] or 0)/2+(K['protpack'] or 0)/2
            if not 450<=kc<=950: continue
            sc=pr/kc*100 - (0 if v['salt'] is None else v['salt'])*2 + (v['fib'] or 2)
            if not best or sc>best[0]: best=(sc,v,K,kc,pr,m['price']+v['price']/2+K['price']/2)
    if best: combos.append((m,)+best[1:])
    if len(combos)>=15: break
# Multipot guide (aus Datensätzen, Richtwerte)
guide=collections.OrderedDict()
for r in R:
    if r['mp']:
        key=r['mp'].split(':')[0][:60] if ':' in r['mp'][:60] else r['pack']
        guide.setdefault(key,[]).append(r)
g2=sorted(guide.items(),key=lambda kv:-len(kv[1]))[:20]
E=html.escape
def cell(v):
    return '' if v is None else (f'{v:.2f}'.rstrip('0').rstrip('.') if isinstance(v,float) else E(str(v)))
COLS=[('Foto',None),('Produkt','name'),('Marke','brand'),('Laden','store'),('Verpackung','pack'),('Preis €','price'),('€/kg','ppk'),('Protein/Pkg g','protpack'),('Protein/100kcal','p100k'),('kcal/100g','kcal'),('Salz g/100g','salt'),('ges. Fett','sat'),('Health-Score','score'),('Protein/€','ppe'),('Hersteller + Ort','herst'),('Multipot-Pro','mp'),('Link','url')]
def row(r):
    t=[f'<td>{"<img loading=lazy src="+chr(34)+E(r["img"])+chr(34)+">" if r["img"] else ""}</td>',f'<td>{E(r["name"])}</td>',f'<td>{E(r["brand"])}</td>',f'<td>{r["store"]}</td>',f'<td>{E(r["pack"])}</td>']
    pc='stale' if r['pstat'] in('Preis 2025','Preis unbestätigt') else ''
    mk=f' <span class=tag>{r["pstat"]}</span>' if pc else ''
    t.append(f'<td class="num {pc}" data-v="{r["price"] or ""}">{cell(r["price"])}{mk}</td>')
    for k in ['ppk','protpack','p100k','kcal','salt','sat','score','ppe']:
        t.append(f'<td class=num data-v="{r[k] if r[k] is not None else ""}">{cell(r[k])}</td>')
    oo=' <span class=ooe>OÖ</span>' if r['ooe'] else ''
    t.append(f'<td>{E(r["herst"] or "")}{"<br><small>"+E(r["ort"])+"</small>" if r["ort"] else ""}{oo}</td>')
    t.append(f'<td><small>{E(r["mp"])}</small></td>')
    t.append(f'<td>{"<a href="+chr(34)+E(r["url"])+chr(34)+" target=_blank>↗</a>" if r["url"] else ""}</td>')
    return f'<tr data-store="{r["store"]}" data-pack="{E(r["pack"])}" data-prot="{r["protpack"] or 0}">'+''.join(t)+'</tr>'
def table(rows,tid):
    return f'<table class=t id={tid}><thead><tr>'+''.join(f'<th>{c}</th>' for c,_ in COLS)+'</tr></thead><tbody>'+''.join(row(r) for r in rows)+'</tbody></table>'
stores=sorted({r['store'] for r in R}); packs=sorted({r['pack'] for r in R})
sec={}
sec['alle']=f'''<div class=filters>Laden <select id=fs><option value="">alle</option>{''.join(f"<option>{s}</option>" for s in stores)}</select>
Verpackung <select id=fp><option value="">alle</option>{''.join(f"<option>{E(p)}</option>" for p in packs)}</select>
min. Protein/Pkg (g) <input id=fm type=number value=0 style="width:5em"> Suche <input id=fq placeholder="Name/Marke…"> <span id=cnt></span></div>'''+table(sorted(R,key=lambda r:-(r['score'] or -1)),'tall')
sec['gesund']='<p>Top 30 nach Health-Score (0–100).</p>'+table(top_h,'th')
sec['pe']='<p>Top 30 Gramm Protein pro Euro – nur aktuelle Preise 2026.</p>'+table(top_pe,'tpe')
pv='<table class=t><thead><tr><th>Verpackung</th><th>n</th><th>Protein g/100g</th><th>Protein/100kcal</th><th>Salz</th><th>ges. Fett</th><th>Zucker</th><th>€/kg</th><th>€/10 g Protein</th><th>Health-Score</th></tr></thead><tbody>'
for t,s in sorted(S.items(),key=lambda kv:-(kv[1]['health_score'][0] or 0)):
    pv+=f"<tr><td>{E(t)}</td><td class=num>{s['n']}</td>"+''.join(f"<td class=num>{cell(s[k][0])}</td>" for k in ['protein_100','protein_per_100kcal','salt_100','satfat_100','sugar_100','price_per_kg','price_per_10g_protein','health_score'])+'</tr>'
sec['pack']=pv+'</tbody></table><p class=note>Mediane. Bei Trocken/Instant beziehen sich die Nährwerte meist aufs Pulver, darum ist Protein/100 kcal maßgeblich. „Glas“ hat sehr kleines n. Details und Quellen (Nährstoffverluste, BPA-Verbot VO (EU) 2024/3190, NOVA) stehen in packaging_report.md.</p>'
sh=''
for k,v in same[:40]:
    sh+=f'<h4>{E(v[0]["pid"])} – {E(v[0]["herst"] or "")} {E(v[0]["ort"])} {"<span class=ooe>OÖ</span>" if v[0]["ooe"] else ""}</h4><ul>'+''.join(f'<li>{E(r["brand"])} · {E(r["name"])} · {r["store"]} · {cell(r["price"])} € · {cell(r["ppk"])} €/kg</li>' for r in v)+'</ul>'
sec['same']=f'<p>{len(same)} Betriebe (Identitätskennzeichen) beliefern mehrere Marken bzw. Läden. Quelle ist das Identitätskennzeichen auf der Packung, Firmenauflösung über die Statistik-Austria-Liste (vis.statistik.at).</p>'+sh
fc='<table class=t><thead><tr><th>Gruppe</th><th>n</th><th>Preis €</th><th>Protein/Pkg</th><th>kcal/Pkg</th><th>Protein/€</th><th>Protein/100kcal</th></tr></thead><tbody>'
for nme,L in cmp: fc+=f'<tr><td>{nme}</td><td class=num>{len(L)}</td>'+''.join(f'<td class=num>{cell(md(L,k))}</td>' for k in ['price','protpack','kcalpack','ppe','p100k'])+'</tr>'
sec['ftg']=fc+'</tbody></table><p class=note>Mediane. Fit to Go: Preise aus dem Online-Shop (Box-Preise können abweichen). Martins gezahlte 3 € entsprechen etwa dem Preisniveau der Supermarkt-Menüschalen.</p>'+table(sorted(ftg,key=lambda r:-(r['ppe'] or 0)),'tftg')
kc='<table class=t><thead><tr><th>Hauptgericht</th><th>+ Gemüse (½ Pkg)</th><th>+ Beilage (½ Pkg)</th><th>kcal</th><th>Protein g</th><th>Preis €</th></tr></thead><tbody>'
for m,v,k,kcv,pr,pc in combos: kc+=f'<tr><td>{E(m["name"])} <small>({m["store"]})</small></td><td>{E(v["name"])} <small>({v["store"]})</small></td><td>{E(k["name"])} <small>({k["store"]})</small></td><td class=num>{round(kcv)}</td><td class=num>{round(pr)}</td><td class=num>{pc:.2f}</td></tr>'
sec['kombi']='<p>Automatisch berechnet: ein proteinreiches Hauptgericht (≥25 g Protein/Pkg, bester Health-Score), dazu eine halbe Packung Gemüse und eine halbe Packung Knödel/Reis/Erdäpfel, Ziel 550–950 kcal bei maximaler Proteindichte. Das ist ein Vorschlag (Richtwert), keine Ernährungsberatung.</p>'+kc+'</tbody></table>'
gd='''<p class=note>⚠ Richtwerte (Guidance), nicht Herstellerangaben. Immer Mindestflüssigkeit beachten: Instant Pot Pro mind. 250 ml (1 Cup), Kerntemperatur bei Fleisch ≥ 75 °C. Fertiggerichte am besten aus der Kunststoffschale in einen Edelstahleinsatz umfüllen, auf den Dampfeinsatz (Trivet) über 250 ml Wasser stellen.</p>
<table class=t><thead><tr><th>Produktgruppe</th><th>Modus</th><th>Wasser</th><th>Zeit</th><th>Druckablass</th></tr></thead><tbody>
<tr><td>Kühl-Menüschale (Good Choice, Omis, Clever)</td><td>Steam High</td><td>250 ml unter Trivet</td><td>5–8 Min.</td><td>Quick Release</td></tr>
<tr><td>TK-Fertiggericht (Box/Beutel)</td><td>Steam High</td><td>250 ml</td><td>12–15 Min.</td><td>Quick Release, umrühren</td></tr>
<tr><td>Ripperl/Spareribs roh oder mariniert</td><td>Pressure Cook High</td><td>250 ml</td><td>25 Min.</td><td>10 Min. Natural Release, dann Backrohr/Grill 5 Min.</td></tr>
<tr><td>Hühnerspieße</td><td>Steam High</td><td>250 ml</td><td>8–10 Min.</td><td>Quick Release, danach kurz anbraten (Sauté)</td></tr>
<tr><td>TK-Fischfilet / Schlemmerfilet</td><td>Steam High</td><td>250 ml</td><td>8–10 Min.</td><td>Quick Release</td></tr>
<tr><td>Sous-vide-Fleisch (vakuumiert)</td><td>Sous Vide 60–70 °C oder Steam Low im Beutel</td><td>Wasserbad</td><td>20–30 Min.</td><td>–</td></tr>
<tr><td>Dosengericht</td><td>Sauté Low oder Steam im Einsatz</td><td>–/250 ml</td><td>5–7 Min.</td><td>–</td></tr>
<tr><td>Knödel (Kühl/TK)</td><td>Steam High</td><td>250 ml</td><td>6 (kühl) / 10 (TK) Min.</td><td>Quick Release</td></tr>
</tbody></table><h4>Häufigste Methoden aus den Produktdaten</h4><ul>'''+''.join(f'<li><b>{E(k)}</b> ({len(v)} Produkte): <small>{E(v[0]["mp"][:220])}</small></li>' for k,v in g2)+'</ul>'
sec['mp']=gd
tabs=[('alle',f'Alle Gerichte ({len(R)})'),('gesund','Top 30 Gesund'),('pe','Top 30 Protein/€'),('pack','Verpackungsvergleich'),('same','Gleicher Hersteller'),('ftg','Fit to Go vs Supermarkt'),('kombi','Kombi-Ideen'),('mp','Multipot-Pro Garzeiten')]
H=f'''<!doctype html><html lang=de><head><meta charset=utf-8><title>Fertiggerichte Linz – Vergleich</title><style>
body{{font-family:system-ui,sans-serif;margin:16px;background:#fafafa;color:#222}}h1{{margin:0 0 4px}}.sub{{color:#555;margin-bottom:10px}}
.tabs button{{border:1px solid #ccc;background:#fff;padding:7px 12px;margin:2px;border-radius:6px;cursor:pointer}}.tabs button.on{{background:#1b6e3a;color:#fff}}
section{{display:none}}section.on{{display:block}}table.t{{border-collapse:collapse;width:100%;font-size:12.5px;background:#fff}}.t th{{background:#1b6e3a;color:#fff;position:sticky;top:0;cursor:pointer;padding:5px}}
.t td{{border-bottom:1px solid #eee;padding:4px;vertical-align:top}}.t img{{width:56px;height:56px;object-fit:contain}}td:nth-child(16){{min-width:260px}}.num{{text-align:right;white-space:nowrap}}
.stale{{color:#999}}.tag{{font-size:10px;background:#ddd;color:#666;border-radius:3px;padding:0 3px}}.ooe{{background:#e30613;color:#fff;font-size:10px;border-radius:3px;padding:0 4px}}
.filters{{margin:8px 0;padding:8px;background:#fff;border:1px solid #ddd;border-radius:6px}}.note{{color:#666;font-size:13px}}.kpi{{display:inline-block;background:#fff;border:1px solid #ddd;border-radius:8px;padding:6px 12px;margin:3px}}
</style></head><body><h1>Fertig- &amp; Schnellgerichte rund um Linz</h1><div class=sub>Billa, Spar/Interspar, Hofer, Lidl, Penny, dm, Fit to Go · Stand 12.10.2026 · Preise: graue Werte mit „Preis 2025“ bzw. „Preis unbestätigt“ sind keine aktuellen Preise</div>
<div><span class=kpi><b>{len(R)}</b> Gerichte</span><span class=kpi><b>{sum(1 for r in R if r['score'] is not None)}</b> mit Health-Score</span><span class=kpi><b>{sum(1 for r in R if r['pstat']=='live 2026')}</b> mit Preis 2026</span><span class=kpi><b>{len(same)}</b> Werke mit mehreren Marken</span><span class=kpi><b>{sum(1 for r in R if r['ooe'])}</b> aus OÖ</span></div>
<p class=note>Health-Score: 30 Basis + Proteindichte (max. +40) − Salz (max. −20) − ges. Fett (max. −15) + Ballaststoffe/Gemüse (max. +20) − Verarbeitungsgrad (max. −10). Nur echte Produktdaten; Multipot-Angaben sind Richtwerte.</p>
<div class=tabs>{''.join(f'<button data-t="{k}">{v}</button>' for k,v in tabs)}</div>
{''.join(f'<section id="s_{k}">{sec[k]}</section>' for k,_ in tabs)}
<script>
const bs=document.querySelectorAll('.tabs button');function show(k){{bs.forEach(b=>b.classList.toggle('on',b.dataset.t==k));document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id=='s_'+k))}}
bs.forEach(b=>b.onclick=()=>show(b.dataset.t));show('alle');
document.querySelectorAll('table.t').forEach(t=>t.querySelectorAll('th').forEach((th,i)=>{{let asc=false;th.onclick=()=>{{asc=!asc;const tb=t.tBodies[0];const rs=[...tb.rows];
rs.sort((a,b)=>{{const x=a.cells[i],y=b.cells[i];let u=x.dataset.v,w=y.dataset.v;if(u!==undefined&&w!==undefined){{u=u===''?-1e9:+u;w=w===''?-1e9:+w;return asc?u-w:w-u}}return asc?x.innerText.localeCompare(y.innerText):y.innerText.localeCompare(x.innerText)}});rs.forEach(r=>tb.appendChild(r))}}}}));
function filt(){{const s=fs.value,p=fp.value,m=+fm.value||0,q=fq.value.toLowerCase();let n=0;document.querySelectorAll('#tall tbody tr').forEach(r=>{{const ok=(!s||r.dataset.store==s)&&(!p||r.dataset.pack==p)&&(+r.dataset.prot>=m)&&(!q||r.innerText.toLowerCase().includes(q));r.style.display=ok?'':'none';if(ok)n++}});cnt.textContent=n+' Treffer'}}
[fs,fp,fm,fq].forEach(e=>e.oninput=filt);filt();
</script></body></html>'''
open('fertiggerichte.html','w').write(H)
# XLSX
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
wb=Workbook();ws=wb.active;ws.title='Alle Gerichte'
hd=['Produkt','Marke','Laden','Verpackung','Preis €','Preisstatus','€/kg','Größe g','Protein/Pkg g','Protein/100g','Protein/100kcal','kcal/100g','Salz g/100g','ges. Fett g/100g','Ballaststoffe','Health-Score','Protein/€','Identitätskennzeichen','Hersteller','Ort','OÖ','Multipot-Pro (Richtwert)','Bild-URL','Link']
def xr(r): return [r['name'],r['brand'],r['store'],r['pack'],r['price'],r['pstat'],r['ppk'],r['size'],r['protpack'],r['p100'],r['p100k'],r['kcal'],r['salt'],r['sat'],r['fib'],r['score'],r['ppe'],r['pid'],r['herst'],r['ort'],'ja' if r['ooe'] else '',r['mp'],r['img'],r['url']]
def sheet(ws,rows):
    ws.append(hd)
    for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1B6E3A')
    for r in rows:
        ws.append(xr(r))
        if r['pstat'] in('Preis 2025','Preis unbestätigt'): ws.cell(ws.max_row,5).font=Font(color='999999')
    ws.freeze_panes='B2'; ws.auto_filter.ref=ws.dimensions; ws.column_dimensions['A'].width=45
sheet(ws,sorted(R,key=lambda r:-(r['score'] or -1)))
sheet(wb.create_sheet('Top 30 Gesund'),top_h); sheet(wb.create_sheet('Top 30 Protein je Euro'),top_pe); sheet(wb.create_sheet('Fit to Go'),ftg)
w=wb.create_sheet('Verpackungsvergleich');w.append(['Verpackung','n','Protein g/100g','Protein/100kcal','Salz','ges. Fett','Zucker','Ballaststoffe','€/kg','€/10g Protein','Health-Score'])
for t,s in S.items(): w.append([t,s['n']]+[s[k][0] for k in ['protein_100','protein_per_100kcal','salt_100','satfat_100','sugar_100','fiber_100','price_per_kg','price_per_10g_protein','health_score']])
w=wb.create_sheet('Gleicher Hersteller');w.append(['Kennzeichen','Hersteller','Ort','Marke','Produkt','Laden','Preis','€/kg'])
for k,v in same:
    for r in v: w.append([r['pid'],r['herst'],r['ort'],r['brand'],r['name'],r['store'],r['price'],r['ppk']])
w=wb.create_sheet('Kombi-Ideen');w.append(['Hauptgericht','Laden','Gemüse (½)','Beilage (½)','kcal','Protein g','Preis €'])
for m,v,k,kcv,pr,pc in combos: w.append([m['name'],m['store'],v['name'],k['name'],round(kcv),round(pr),round(pc,2)])
wb.save('fertiggerichte.xlsx')
print('top_h',len(top_h),'top_pe',len(top_pe),'same',len(same),'ftg',len(ftg),'combos',len(combos),'ooe',sum(1 for r in R if r['ooe']))
