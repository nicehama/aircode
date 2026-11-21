# -*- coding: utf-8 -*-
"""375x667 소형 화면 + 매니페스트 확인"""
import asyncio, json
from playwright.async_api import async_playwright
URL = 'https://nicehama.github.io/aircode/'

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':375,'height':667}, device_scale_factor=2, locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        page.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        await page.goto(URL, wait_until='load'); await page.wait_for_timeout(600)
        await page.screenshot(path='/workspace/downloads/app_v5_11_375_main.png')
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(400)
        await page.click('#samples [data-samp="lgOut"]'); await page.wait_for_timeout(900)
        await page.screenshot(path='/workspace/downloads/app_v5_12_375_result.png')
        ov = await page.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('*').forEach(el => {
            const s = getComputedStyle(el);
            if (el.scrollWidth - el.clientWidth > 2 && s.overflowX !== 'auto' && s.overflowX !== 'scroll')
              bad.push((el.tagName + '.' + el.className).slice(0, 46) + ' ' + el.scrollWidth + '/' + el.clientWidth);
          });
          return { body: document.body.scrollWidth, win: window.innerWidth, bad: bad.slice(0, 8) };
        }""")
        print('375 overflow', json.dumps(ov, ensure_ascii=False))
        print('code', (await page.text_content('.ai-res-code')).strip())
        # 매니페스트 (CDP)
        cdp = await ctx.new_cdp_session(page)
        try:
            m = await cdp.send('Page.getAppManifest')
            print('manifest url', (m.get('url') or '')[:60], '| errors', m.get('errors'))
            raw = m.get('data') or ''
            print('manifest name', json.loads(raw).get('name') if raw else None)
        except Exception as e:
            print('manifest cdp err', e)
        print('ERRORS', errs)
        await b.close()
asyncio.run(main())
