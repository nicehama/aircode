# -*- coding: utf-8 -*-
"""390x844 아이폰 크기로 렌더해 탭별 스크린샷을 찍고 레이아웃 이상을 점검한다."""
import os, asyncio, json
from playwright.async_api import async_playwright

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
url = 'file://' + os.path.join(root, 'downloads', '에어컨_에러코드_앱_프로토타입.html')
outdir = os.path.join(root, 'downloads')
shots = [
    ('search', 'app_preview_1_search.png'),
    ('led', 'app_preview_2_led.png'),
    ('check', 'app_preview_3_checklist.png'),
    ('promo', 'app_preview_4_promo.png'),
]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errors = []
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append('PAGEERROR: ' + str(e)))
        await page.goto(url)
        await page.wait_for_timeout(600)

        info = await page.evaluate("""() => {
          const r = {entries: DATA.entries.length, bodyW: document.body.scrollWidth, winW: window.innerWidth};
          r.overflow = Array.from(document.querySelectorAll('*')).filter(el =>
             el.scrollWidth - el.clientWidth > 2 && getComputedStyle(el).overflowX !== 'auto' && getComputedStyle(el).overflowX !== 'scroll'
          ).slice(0, 12).map(el => (el.tagName + '.' + el.className).slice(0, 60) + ' sw=' + el.scrollWidth + ' cw=' + el.clientWidth);
          return r;
        }""")
        print('INFO', json.dumps(info, ensure_ascii=False))

        for tab, fname in shots:
            await page.click('#tabbar button[data-tab="%s"]' % tab)
            await page.wait_for_timeout(450)
            await page.screenshot(path=os.path.join(outdir, fname))
            print('shot', fname)

        # LED 상호작용 검증: LG 적2·녹1 → CH21
        await page.click('#tabbar button[data-tab="led"]')
        await page.wait_for_timeout(300)
        await page.click('#tapRed'); await page.click('#tapRed'); await page.click('#tapGreen')
        await page.wait_for_timeout(250)
        code = await page.text_content('#lgCode')
        match = await page.text_content('#lgMatch')
        print('LG COUNTER:', code, '|', (match or '').strip()[:80])
        await page.evaluate("document.querySelector('#lgMatch').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path=os.path.join(outdir, 'app_preview_5_lg_counter.png'))

        # 삼성 4WAY 물방울+시계+바둑판
        await page.click('#toolSam .tool-head')
        await page.wait_for_timeout(250)
        for k in ['물방울', '시계', '바둑판']:
            await page.click('#samIcons [data-icon="%s"]' % k)
        await page.wait_for_timeout(250)
        sm = await page.text_content('#samMatch')
        print('SAMSUNG MATCH:', (sm or '').strip()[:100])

        # 360 카세트 패널
        await page.click('#samForms [data-form="360"]')
        await page.wait_for_timeout(200)
        await page.click('#samIcons [data-color="빨간색"]')
        await page.wait_for_timeout(200)
        await page.click('#samIcons [data-disp]')
        await page.wait_for_timeout(250)
        print('360 MATCH:', (await page.text_content('#samMatch') or '').strip()[:80].replace('\n',' '))
        await page.evaluate("document.querySelector('#toolSam').scrollIntoView({block:'start'})")
        await page.wait_for_timeout(250)
        await page.screenshot(path=os.path.join(outdir, 'app_preview_8_cassette.png'))
        await page.click('#toolSam .tool-head')

        # AI 샘플 판독 (분석 중 화면 포함)
        await page.click('#toolSam .tool-head')
        await page.evaluate("document.querySelector('#tab-led').scrollTo(0,0)")
        await page.click('#samples [data-sample="sam"]')
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(outdir, 'app_preview_9_ai_scanning.png'))
        await page.wait_for_timeout(3000)
        ai = await page.text_content('#aiResult')
        print('AI RESULT:', (ai or '').strip()[:160].replace('\n', ' '))
        await page.screenshot(path=os.path.join(outdir, 'app_preview_6_ai_result.png'))

        # 검색 검증
        await page.click('#tabbar button[data-tab="search"]')
        await page.fill('#q', 'CH21')
        await page.wait_for_timeout(300)
        first = await page.text_content('#cards .card')
        print('SEARCH CH21:', (first or '').strip().replace('\n', ' ')[:120])
        await page.fill('#q', '배수')
        await page.wait_for_timeout(300)
        cnt = await page.text_content('#listCount')
        print('SEARCH 배수:', cnt)
        await page.fill('#q', '')
        await page.wait_for_timeout(200)

        # 상세 시트
        await page.click('#cards .card')
        await page.wait_for_timeout(500)
        await page.screenshot(path=os.path.join(outdir, 'app_preview_7_detail.png'))
        sh = await page.text_content('#shBody')
        print('SHEET:', (sh or '').strip()[:120].replace('\n', ' '))

        print('CONSOLE ERRORS:', errors)
        await b.close()

asyncio.run(main())
