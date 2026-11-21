# -*- coding: utf-8 -*-
"""v5 기능 전수 점검 (로컬 dist)"""
import asyncio
from playwright.async_api import async_playwright
URL = 'file:///workspace/app-aircon-prototype/dist/index.html'
VID = '/workspace/downloads/test_led_ch21.mp4'
IMG = '/workspace/downloads/test_led_frame_red.png'

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs=[]
        page.on('pageerror', lambda e: errs.append('PAGEERROR: '+str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: '+m.text) if m.type=='error' else None)
        await page.goto(URL, wait_until='load'); await page.wait_for_timeout(400)
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)

        # 1) 실제 영상 업로드
        await page.set_input_files('#fileIn', VID)
        await page.wait_for_function('ai && ai.result', timeout=40000)
        await page.wait_for_timeout(500)
        print('1 video code', (await page.text_content('.ai-res-code')).strip(),
              '| meas', (await page.text_content('.meas-row b')).strip())
        print('  video visible', await page.evaluate("""() => {const v=document.querySelector('#frameInner video'); if(!v) return 'no-el';
            const r=v.getBoundingClientRect(), s=getComputedStyle(v); return [Math.round(r.width),Math.round(r.height),s.display,s.objectFit].join('/');}"""))
        await page.locator('#frame').screenshot(path='/workspace/downloads/app_v5_frame_video.png')

        # 2) ROI 를 구석으로 옮기면 검출 실패
        await page.locator('#frame').scroll_into_view_if_needed(); await page.wait_for_timeout(300)
        cr = await page.evaluate("() => { const r = document.querySelector('#frame').getBoundingClientRect(); return mediaContentRect(r.width, r.height); }")
        box = await page.locator('#frame').bounding_box()
        await page.mouse.click(box['x'] + cr['x'] + cr['w'] * 0.08, box['y'] + cr['y'] + cr['h'] * 0.9)
        await page.wait_for_timeout(1200)
        print('2 roi corner →', (await page.text_content('.ai-res-code') or '').strip(), '|', (await page.text_content('.ai-res-top') or '').strip()[:44])
        # 3) LED 위치로 되돌리기
        await page.locator('#frame').scroll_into_view_if_needed(); await page.wait_for_timeout(300)
        cr = await page.evaluate("() => { const r = document.querySelector('#frame').getBoundingClientRect(); return mediaContentRect(r.width, r.height); }")
        box = await page.locator('#frame').bounding_box()
        await page.mouse.click(box['x'] + cr['x'] + cr['w'] * 0.503, box['y'] + cr['y'] + cr['h'] * 0.525)
        await page.wait_for_timeout(1200)
        print('3 roi back →', (await page.text_content('.ai-res-code') or '').strip())
        await page.locator('#frame').screenshot(path='/workspace/downloads/app_v5_frame_roi.png')

        # 4) ± 보정
        await page.click('[data-adj="red:1"]'); await page.wait_for_timeout(300)
        print('4 red+1 →', (await page.text_content('.ai-res-code') or '').strip(), '|', ((await page.text_content('.ai-res-check')) or '').strip()[:60])
        await page.click('[data-adj="red:-1"]'); await page.wait_for_timeout(300)
        print('  red-1 →', (await page.text_content('.ai-res-code') or '').strip())

        # 5) LG 실내기 샘플
        await page.click('#samples [data-samp="lgIn"]'); await page.wait_for_timeout(900)
        print('5 LG indoor', (await page.text_content('.ai-res-code') or '').strip(), '|', (await page.text_content('.meas-row b') or '').strip())
        # 6) 캐리어 샘플
        await page.click('#samples [data-samp="carrier"]'); await page.wait_for_timeout(900)
        print('6 carrier', (await page.text_content('.ai-res-code') or '').strip(), '|', ((await page.text_content('.ai-res-cause')) or '').strip())
        # 7) 삼성 샘플
        await page.click('#samples [data-samp="samsung"]'); await page.wait_for_timeout(700)
        print('7 samsung', (await page.text_content('.ai-res-code') or '').strip(), '| leds', await page.locator('.res-leds span').count())
        await page.screenshot(path='/workspace/downloads/app_v5_samsung.png')

        # 8) 사진 업로드
        await page.click('#aiModes .mode[data-mode="lgOut"]'); await page.wait_for_timeout(300)
        await page.set_input_files('#fileIn', IMG); await page.wait_for_timeout(1500)
        print('8 photo', (await page.text_content('.ai-res-code') or '').strip(), '|', (await page.text_content('.ai-res-check') or '').strip()[:60])
        await page.screenshot(path='/workspace/downloads/app_v5_photo.png')

        # 9) 즐겨찾기 유지(새로고침)
        await page.click('#tabbar button[data-tab="search"]'); await page.wait_for_timeout(200)
        await page.click('#cards .card:nth-child(2) [data-star]'); await page.wait_for_timeout(200)
        await page.reload(wait_until='load'); await page.wait_for_timeout(500)
        await page.click('#viewChips .chip[data-view="fav"]'); await page.wait_for_timeout(300)
        print('9 fav after reload', (await page.text_content('#listCount')).strip())
        await page.click('#viewChips .chip[data-view="all"]'); await page.wait_for_timeout(200)

        # 10) 최근 본
        await page.click('#cards .card:first-child'); await page.wait_for_timeout(400)
        await page.click('#sheetClose'); await page.wait_for_timeout(300)
        await page.click('#viewChips .chip[data-view="recent"]'); await page.wait_for_timeout(300)
        print('10 recent', (await page.text_content('#listCount')).strip())
        print('ERRORS', errs)
        await b.close()
asyncio.run(main())
