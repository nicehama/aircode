# -*- coding: utf-8 -*-
"""추가 화면 검수: 각 탭 하단부, 패널 펼침, 375px 폭 오버플로 확인."""
import os, asyncio
from playwright.async_api import async_playwright

here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
url = 'file://' + os.path.join(root, 'downloads', '에어컨_에러코드_앱_프로토타입.html')
outdir = os.path.join(root, 'downloads')

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h, tag in [(390, 844, ''), (375, 667, '_se')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, locale='ko-KR', is_mobile=True, has_touch=True)
            page = await ctx.new_page()
            errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            await page.goto(url); await page.wait_for_timeout(500)
            ov = await page.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('*').forEach(el => {
                const s = getComputedStyle(el);
                if (el.scrollWidth - el.clientWidth > 2 && s.overflowX !== 'auto' && s.overflowX !== 'scroll')
                  bad.push((el.tagName+'.'+el.className).slice(0,50)+' '+el.scrollWidth+'/'+el.clientWidth);
              });
              return {body:document.body.scrollWidth, win:window.innerWidth, bad:bad.slice(0,8)};
            }""")
            print(tag or '390', 'overflow', ov, 'errors', errs)

            if tag == '':
                # 검색 하단
                await page.evaluate("document.querySelector('#main').scrollTop = 700")
                await page.wait_for_timeout(300); await page.screenshot(path=os.path.join(outdir, 'chk_search_scroll.png'))
                # 체크리스트 하단
                await page.click('#tabbar button[data-tab="check"]'); await page.wait_for_timeout(300)
                await page.evaluate("document.querySelector('#main').scrollTop = document.querySelector('#main').scrollHeight")
                await page.wait_for_timeout(300); await page.screenshot(path=os.path.join(outdir, 'chk_check_bottom.png'))
                # 아카데미 하단
                await page.click('#tabbar button[data-tab="promo"]'); await page.wait_for_timeout(300)
                await page.evaluate("document.querySelector('#main').scrollTop = document.querySelector('#main').scrollHeight")
                await page.wait_for_timeout(300); await page.screenshot(path=os.path.join(outdir, 'chk_promo_bottom.png'))
                # LED: 캐리어/촬영 패널 펼침
                await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)
                await page.click('#toolEtc .tool-head'); await page.click('#toolShoot .tool-head')
                await page.wait_for_timeout(300)
                await page.evaluate("document.querySelector('#toolEtc').scrollIntoView({block:'start'})")
                await page.wait_for_timeout(300); await page.screenshot(path=os.path.join(outdir, 'chk_led_panels.png'))
                # 파일 업로드 흐름 (이미지)
                await page.set_input_files('#fileIn', os.path.join(root, 'work-aircon-codes', 'figs', 'fig2.png'))
                await page.wait_for_timeout(5200)
                await page.screenshot(path=os.path.join(outdir, 'chk_ai_upload.png'))
                print('upload result:', (await page.text_content('#aiResult') or '')[:90].replace('\n', ' '))
            await ctx.close()
        await b.close()

asyncio.run(run())
