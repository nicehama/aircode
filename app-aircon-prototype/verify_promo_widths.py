# -*- coding: utf-8 -*-
"""아카데미 탭 폭별 배치 점검 (320/360/390/430/520) — 로컬 빌드 기준"""
import asyncio, json
from playwright.async_api import async_playwright

PATH = 'file:///workspace/downloads/에어컨_에러코드_앱_프로토타입.html'


async def main():
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        for w in (320, 360, 390, 430, 520):
            ctx = await b.new_context(viewport={'width': w, 'height': 844}, device_scale_factor=2,
                                      locale='ko-KR', is_mobile=w < 500, has_touch=True)
            page = await ctx.new_page()
            errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            await page.goto(PATH, wait_until='load')
            await page.wait_for_timeout(400)
            await page.click('#tabbar button[data-tab="promo"]')
            await page.wait_for_timeout(400)
            out[w] = await page.evaluate("""
              (() => {
                const hero = document.querySelector('.promo-hero').getBoundingClientRect();
                const btns = Array.from(document.querySelectorAll('#tab-promo .promo-btns > *')).map(el => {
                  const b = el.getBoundingClientRect();
                  return {t: el.textContent.trim(), x: +b.left.toFixed(0), y: +b.top.toFixed(0),
                          w: +b.width.toFixed(0), h: +b.height.toFixed(0)};
                });
                const card = Array.from(document.querySelectorAll('#tab-promo .promo-card'))
                  .find(c => c.textContent.includes('쾌적하마'));
                const cr = card.getBoundingClientRect();
                const links = Array.from(card.querySelectorAll('.promo-links a, .promo-links a.tel, .link-btn.go')).map(el => {
                  const b = el.getBoundingClientRect();
                  return {t: el.textContent.trim().replace(/\\s+/g,' '), w: +b.width.toFixed(0),
                          sq: el.scrollWidth > el.clientWidth + 1};
                });
                const svc = Array.from(document.querySelectorAll('#tab-promo .panel'))
                  .find(x => x.textContent.includes('서비스 대상'));
                const sr = svc.getBoundingClientRect();
                const svcOver = Array.from(svc.querySelectorAll('.svc-chips span, .svc-list li'))
                  .filter(el => el.getBoundingClientRect().right > sr.right - 8).length;
                const rowTops = [...new Set(btns.map(b => b.y))];
                return {hero: {w: +hero.width.toFixed(0), h: +hero.height.toFixed(0)},
                        rows: rowTops.length, btns, cardH: +cr.height.toFixed(0),
                        cardRight: +cr.right.toFixed(0), links, svcH: +sr.height.toFixed(0), svcOver,
                        docOverflowX: document.documentElement.scrollWidth > window.innerWidth + 0.5};
              })()""")
            out[w]['errors'] = errs
            if w in (320, 430):
                await page.screenshot(path=f'/workspace/browser/promo_{w}.png')
            await ctx.close()
        await b.close()
    print(json.dumps(out, ensure_ascii=False, indent=1))


asyncio.run(main())
