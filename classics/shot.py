from playwright.sync_api import sync_playwright
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1500,'height':1000})
  pg.goto('https://martin-hausleitner.github.io/fertiggerichte-vergleich/?r=11#tab=gerichte&dish=wiener-suppentopf',wait_until='networkidle'); pg.wait_for_timeout(6000)
  loc=pg.locator('h2:has-text("Gericht vergleichen")'); print(loc.count())
  if loc.count(): loc.first.scroll_into_view_if_needed(); pg.mouse.wheel(0,-250); pg.wait_for_timeout(1500); pg.screenshot(path='/workspace/fertig/classics/gerichte_martin.png')
