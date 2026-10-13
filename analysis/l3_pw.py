import asyncio,json,sys,re,base64
from playwright.async_api import async_playwright
JOBS=json.load(open(sys.argv[1])); OUT=sys.argv[2]
JS=r"""(kw)=>{const out=[];const K=kw.map(k=>k.toLowerCase());
const hdr=(el)=>!!el.closest('header,nav,[class*=header],[id*=header],[class*=logo],[id*=logo],[class*=brand]');
for(const im of document.querySelectorAll('img,source')){let s=im.currentSrc||im.src||im.srcset||im.getAttribute('data-src')||'';if(!s)continue;
 const meta=(s+' '+(im.alt||'')+' '+(im.className||'')+' '+(im.id||'')+' '+(im.title||'')).toLowerCase();
 const r=im.getBoundingClientRect();
 out.push({t:'img',src:s.split(' ')[0],alt:im.alt||'',nw:im.naturalWidth||0,nh:im.naturalHeight||0,w:r.width,h:r.height,y:r.top,logo:/logo|brand|marke/.test(meta),kw:K.some(k=>meta.includes(k)),hdr:hdr(im)});}
for(const sv of document.querySelectorAll('svg')){const r=sv.getBoundingClientRect();if(r.width<40)continue;const meta=((sv.getAttribute('class')||'')+' '+(sv.id||'')+' '+(sv.getAttribute('aria-label')||'')+' '+(sv.closest('a')?.getAttribute('aria-label')||'')+' '+(sv.closest('a')?.className||'')+' '+(sv.querySelector('title')?.textContent||'')).toLowerCase();
 out.push({t:'svg',svg:sv.outerHTML.length<400000?sv.outerHTML:'',w:r.width,h:r.height,y:r.top,logo:/logo|brand/.test(meta),kw:K.some(k=>meta.includes(k)),hdr:hdr(sv)});}
const og=document.querySelector('meta[property="og:image"]');
return {title:document.title,url:location.href,og:og?og.content:null,c:out};}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(channel='chrome',headless=True,args=['--disable-blink-features=AutomationControlled'])
    ctx=await b.new_context(viewport={'width':1440,'height':1000},locale='de-AT',user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36')
    sem=asyncio.Semaphore(6);R={}
    async def one(j):
      async with sem:
        pg=await ctx.new_page()
        try:
          await pg.goto(j['url'],wait_until='domcontentloaded',timeout=35000); await pg.wait_for_timeout(3500)
          for sel in ['#onetrust-accept-btn-handler','button:has-text("Alle akzeptieren")','button:has-text("Akzeptieren")','button:has-text("Accept all")']:
            try: await pg.click(sel,timeout=800)
            except: pass
          R[j['key']+'|'+j['url']]=await pg.evaluate(JS,j.get('kw',[]))
        except Exception as e: R[j['key']+'|'+j['url']]={'err':str(e)[:150]}
        await pg.close()
    await asyncio.gather(*[one(j) for j in JOBS]); await b.close()
  json.dump(R,open(OUT,'w'),ensure_ascii=False)
asyncio.run(main())
