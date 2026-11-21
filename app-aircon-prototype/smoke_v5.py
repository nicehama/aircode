# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright
URL = 'file:///workspace/app-aircon-prototype/dist/index.html'

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs=[]
        page.on('pageerror', lambda e: errs.append('PAGEERROR: '+str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: '+m.text) if m.type=='error' else None)
        await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(600)
        print('title', await page.title())
        print('badge', await page.text_content('#topBadge'))
        print('cards', await page.locator('#cards .card').count())
        print('viewchips', await page.locator('#viewChips .chip').count())
        # 별 토글
        await page.click('#cards .card:first-child [data-star]')
        await page.wait_for_timeout(200)
        print('toast', (await page.text_content('#toast')).strip())
        await page.click('#viewChips .chip[data-view="fav"]')
        await page.wait_for_timeout(200)
        print('fav list', await page.text_content('#listCount'), '| title', (await page.text_content('#listTitle')).strip())
        await page.click('#viewChips .chip[data-view="all"]')
        await page.wait_for_timeout(200)
        # QR
        await page.click('#qrBtn'); await page.wait_for_timeout(300)
        print('qr on', 'on' in (await page.get_attribute('#qrModal','class')), '| url', await page.text_content('#qrUrl'))
        await page.screenshot(path='/workspace/downloads/app_v5_qr_modal.png')
        await page.click('#qrCopy'); await page.wait_for_timeout(200)
        print('copy toast', (await page.text_content('#toast')).strip())
        await page.click('#qrClose'); await page.wait_for_timeout(200)
        # LED 탭 샘플
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)
        await page.click('#sampleBtn'); await page.wait_for_timeout(1200)
        print('sample code', (await page.text_content('.ai-res-code') or '').strip())
        print('meas', (await page.text_content('.meas-row b') or '').strip())
        print('pulses', await page.evaluate('ai.result && ai.result.pulses.length'))
        await page.screenshot(path='/workspace/downloads/app_v5_sample.png')
        print('ERRORS', errs)
        await b.close()
asyncio.run(main())
