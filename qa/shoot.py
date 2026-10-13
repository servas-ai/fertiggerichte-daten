import json,sys
from playwright.sync_api import sync_playwright
U="https://martin-hausleitner.github.io/fertiggerichte-vergleich/"
tabs="pack hersteller-seiten matrix hersteller planer kombi ftg multipot methodik analyse".split()
out={}
with sync_playwright() as p:
  b=p.chromium.launch()
  for w,h in [(1920,1080),(390,844)]:
    pg=b.new_page(viewport={'width':w,'height':h})
    errs=[];pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
    bad=[];pg.on('response',lambda r:bad.append(f"{r.status} {r.url}") if r.status>=400 else None)
    for t in tabs:
      errs.clear();bad.clear()
      pg.goto("about:blank");pg.goto(U+"?r=1#tab="+t);pg.wait_for_timeout(4000)
      pg.mouse.wheel(0,20000);pg.wait_for_timeout(1500)
      pg.screenshot(path=f"render/v3/{t}_{w}.png",full_page=True)
      info=pg.evaluate("""()=>{const imgs=[...document.images];
       const broken=imgs.filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src);
       const svgs=[...document.querySelectorAll('.recharts-wrapper')];
       const empty=svgs.filter(s=>s.querySelectorAll('path.recharts-rectangle,.recharts-sector,.recharts-dot,.recharts-curve,.recharts-scatter-symbol,rect.recharts-rectangle').length===0).length;
       const charts=[...document.querySelectorAll('.recharts-wrapper')].map(s=>{let c=s.closest('[class*=card],section,div');let h=c?.parentElement?.querySelector('h2,h3,h4');return h?h.innerText:''});
       const txt=document.body.innerText;
       return {imgs:imgs.length,broken:[...new Set(broken)].slice(0,30),charts:svgs.length,empty,nan:(txt.match(/NaN|undefined|Infinity|null €/g)||[]).length,
        overflow:document.documentElement.scrollWidth>innerWidth, height:document.body.scrollHeight,text:txt.slice(0,6000)}}""")
      info['errs']=errs[:10];info['bad']=bad[:20]
      out[f"{t}_{w}"]=info
      print(t,w,info['imgs'],len(info['broken']),info['charts'],info['empty'],info['nan'],info['overflow'],len(errs),len(bad))
    # analyse charts individually
    pg.goto(U+"#tab=analyse");pg.wait_for_timeout(5000)
    for i,el in enumerate(pg.query_selector_all('.recharts-wrapper')):
      try: el.scroll_into_view_if_needed();pg.wait_for_timeout(300);el.screenshot(path=f"render/v3/analyse_chart{i:02d}_{w}.png")
      except Exception as e: print('chart',i,e)
  b.close()
json.dump(out,open('render/v3/qa2.json','w'),ensure_ascii=False,indent=1)
