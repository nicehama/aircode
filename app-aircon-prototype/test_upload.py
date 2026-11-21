# -*- coding: utf-8 -*-
"""로컬 파일에서 실제 영상 업로드 → 판독 결과 확인"""
import asyncio, sys
from playwright.async_api import async_playwright
URL = 'file:///workspace/app-aircon-prototype/dist/index.html'
VID = sys.argv[1] if len(sys.argv) > 1 else '/workspace/downloads/test_led_ch21.mp4'

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs=[]
        page.on('pageerror', lambda e: errs.append('PAGEERROR: '+str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: '+m.text) if m.type=='error' else None)
        await page.goto(URL, wait_until='load'); await page.wait_for_timeout(500)
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)
        await page.set_input_files('#fileIn', VID)
        try:
            await page.wait_for_function('ai && ai.result', timeout=40000)
        except Exception as e:
            print('TIMEOUT', await page.evaluate('({busy:ai.busy, deriv: !!ai.derived, t: ai.times && ai.times.length})'))
        await page.wait_for_timeout(600)
        print('code', (await page.text_content('.ai-res-code') or '').strip())
        print('meas', (await page.text_content('.meas-row b') or '').strip())
        print('state', await page.evaluate('({mode:ai.result&&ai.result.mode, pulses:ai.result&&ai.result.pulses.length, red:ai.result&&ai.result.red, green:ai.result&&ai.result.green, frames:ai.result&&ai.result.frames, auto:ai.result&&ai.result.auto, code:ai.result&&ai.result.code})'))
        print('roi', await page.evaluate('ai.derived ? (ai.roiNorm ? "manual" : JSON.stringify(autoRoi(ai.derived))) : null'))
        await page.screenshot(path='/workspace/downloads/app_v5_video_local.png')
        print('ERRORS', errs)
        await b.close()
asyncio.run(main())
