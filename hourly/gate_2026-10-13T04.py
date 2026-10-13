import json,sys,re,time
from playwright.sync_api import sync_playwright
base=sys.argv[1]; out=sys.argv[2]
tabs=re.findall(r"t\('([a-z-]+)'",open('/workspace/fertig-app/src/app/tabs.ts').read())
JS="""()=>{const im=[...document.images].filter(i=>i.src&&i.getBoundingClientRect().width>0);
return {ov:document.documentElement.scrollWidth-innerWidth,imgs:im.length,
broken:im.filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src),
textLen:(document.querySelector('main')||document.body).innerText.length,
eb:!!document.body.innerText.match(/Fehler in dieser Ansicht|Something went wrong|ist abgestürzt/)}}"""
res={}
with sync_playwright() as p:
  b=p.chromium.launch(args=['--disable-dev-shm-usage'])
  for w,h in [(1920,1080),(390,844)]:
    for t in tabs:
      errs=[]
      ctx=b.new_context(viewport={'width':w,'height':h});pg=ctx.new_page()
      pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
      pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
      try:
        pg.goto(f'{base}#tab={t}',wait_until='load',timeout=60000); pg.wait_for_timeout(3000)
        pg.mouse.wheel(0,1500); pg.wait_for_timeout(800)
        i=pg.evaluate(JS)
      except Exception as e: i={'ov':0,'imgs':0,'broken':[],'textLen':0,'eb':True,'exc':str(e)[:200]}
      ctx.close()
      nb=len(i['broken']); frac=nb/max(1,i['imgs'])
      r={'tab':t,'w':w,'overflow':i['ov']>0 and w==390,'imgs':i['imgs'],'broken':nb,'broken_sample':i['broken'][:3],'errs':errs[:4],'textLen':i['textLen'],'blank':i['textLen']<200,'errBoundary':i['eb']}
      r['fail']=bool(r['overflow'] or frac>=0.02 or errs or r['blank'] or i['eb'])
      res[f'{t}_{w}']=r; print('FAIL' if r['fail'] else 'ok  ',t,w,i['imgs'],nb,i['ov'],errs[:1],flush=True)
  b.close()
json.dump({'tabs':res,'pass':not any(r['fail'] for r in res.values())},open(out,'w'),indent=1)
