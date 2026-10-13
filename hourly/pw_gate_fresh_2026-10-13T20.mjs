import { chromium } from 'playwright'
import { createServer } from 'http'
import { readFileSync, existsSync, statSync } from 'fs'
import { join, extname } from 'path'

const ROOT = '/workspace/fertig-app/dist'
const MIME = { '.html':'text/html', '.js':'application/javascript', '.css':'text/css', '.json':'application/json', '.bin':'application/octet-stream', '.svg':'image/svg+xml', '.png':'image/png', '.jpg':'image/jpeg', '.webp':'image/webp', '.woff2':'font/woff2', '.ico':'image/x-icon' }
const server = createServer((req, res) => {
  let p = decodeURIComponent((req.url || '/').split('?')[0].split('#')[0])
  if (p === '/') p = '/index.html'
  const fp = join(ROOT, p)
  if (!fp.startsWith(ROOT) || !existsSync(fp) || statSync(fp).isDirectory()) { res.writeHead(404); res.end('404'); return }
  res.writeHead(200, { 'content-type': MIME[extname(fp)] || 'application/octet-stream' })
  res.end(readFileSync(fp))
})
await new Promise(r => server.listen(0, '127.0.0.1', r))
const port = server.address().port
const base = `http://127.0.0.1:${port}/`

const TABS = ['alle','feed','galerie','board','gerichte','top','kategorien','markenprofil','ladenprofil','marken','familien','dashboard','gesundheit','analyse','scatter','pack','matrix','hersteller-seiten','wer','firmen','qualitaet','logos','netz','hersteller','filialen','online','planer','kombi','ftg','multipot','methodik','abdeckung']
const VIEWPORTS = [{ w: 1920, h: 1080, name: 'desktop' }, { w: 390, h: 844, name: 'mobile' }]

const summary = { ok: true, errors: [], blank: [], overflow: [], brokenImg: 0, totalImg: 0, tabs: {} }

// T20: fresh page per tab + up to 2 retries in a fresh browser on renderer crash / nav timeout (box ~1.2 GB free, no swap)
async function check(br, vp, tab, key, shot) {
  const page = await br.newPage({ viewport: { width: vp.w, height: vp.h } })
  const cons = []
  page.on('console', m => { if (m.type() === 'error') cons.push(`[error] ${m.text()}`) })
  page.on('pageerror', e => cons.push(`[pageerror] ${e.message}`))
  try {
    await page.goto(`${base}#tab=${tab}`, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(700)
    const blank = (await page.locator('body').innerText()).trim().length < 40
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2)
    const imgs = await page.evaluate(() => { const l = [...document.images]; return { total: l.length, broken: l.filter(i => i.complete && i.naturalWidth === 0 && i.src && !i.src.startsWith('data:')).length } })
    if (shot) await page.screenshot({ path: shot }).catch(() => {})
    const real = cons.filter(e => !/favicon|Download the React DevTools|net::ERR_FAILED.*embeddings/i.test(e))
    return { blank, overflow, imgs, real }
  } finally { await page.close().catch(() => {}) }
}
let browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] })
for (const vp of VIEWPORTS) {
  for (const tab of TABS) {
    const key = `${vp.name}:${tab}`
    const shot = (vp.name === 'desktop' && tab === 'dashboard') ? '/workspace/fertig/hourly/screenshot_local_2026-10-13T20.png' : null
    let res = null, lastErr = null, tries = 0
    for (tries = 0; tries < 3 && !res; tries++) {
      try { res = await check(browser, vp, tab, key, shot) }
      catch (e) {
        lastErr = e
        await browser.close().catch(() => {})
        browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] })
      }
    }
    if (!res) { summary.ok = false; summary.errors.push(`${key} NAV(after ${tries} tries) ${lastErr && lastErr.message}`); continue }
    const { blank, overflow, imgs, real } = res
    summary.totalImg += imgs.total; summary.brokenImg += imgs.broken
    if (blank) { summary.blank.push(key); summary.ok = false }
    if (vp.name === 'mobile' && overflow) { summary.overflow.push(key); summary.ok = false }
    if (real.length) { summary.errors.push(...real.map(e => `${key} ${e}`)); summary.ok = false }
    summary.tabs[key] = { blank, overflow, imgs, errs: real.length, tries }
  }
}
await browser.close()
server.close()
const brate = summary.totalImg ? summary.brokenImg / summary.totalImg : 0
if (brate >= 0.02) { summary.ok = false; summary.errors.push(`broken image rate ${(brate*100).toFixed(2)}% >= 2%`) }
summary.brokenRate = brate
console.log(JSON.stringify(summary, null, 2))
process.exit(summary.ok ? 0 : 1)
