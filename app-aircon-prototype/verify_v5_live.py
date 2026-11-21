# -*- coding: utf-8 -*-
"""v5 라이브(배포 URL) E2E — 실제 영상 업로드 판독 + 전 기능 회귀. 390x844."""
import os, asyncio, json
from playwright.async_api import async_playwright

URL = 'https://nicehama.github.io/aircode/'
VID = '/workspace/downloads/test_led_ch21.mp4'
IMG = '/workspace/downloads/test_led_frame_red.png'
OUT = '/workspace/downloads'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True,
                                  permissions=['clipboard-read', 'clipboard-write'])
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)
        r = await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(800)
        print('HTTP', r.status, '| title', await page.title())
        print('h1', (await page.text_content('.top-title')).strip(), '| badge', await page.text_content('#topBadge'),
              '| entries', await page.evaluate('DATA.entries.length'))
        await page.screenshot(path=os.path.join(OUT, 'app_v5_01_main.png'))

        # ---------- 1) 실제 영상 업로드 판독 ----------
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(500)
        print('modes', await page.locator('#aiModes .mode').count(),
              '| cam input', await page.evaluate("document.querySelector('#fileCam').getAttribute('capture')"),
              '| accept', await page.evaluate("document.querySelector('#fileIn').getAttribute('accept')"))
        await page.set_input_files('#fileIn', VID)
        await page.wait_for_function('ai && ai.result', timeout=45000)
        await page.wait_for_timeout(700)
        code = (await page.text_content('.ai-res-code')).strip()
        meas = (await page.text_content('.meas-row b')).strip()
        st = await page.evaluate('({mode:ai.result.mode,red:ai.result.red,green:ai.result.green,frames:ai.result.frames,auto:ai.result.auto,pulses:ai.result.pulses.length})')
        print('VIDEO RESULT:', code, '|', meas, '|', json.dumps(st, ensure_ascii=False))
        await page.screenshot(path=os.path.join(OUT, 'app_v5_02_video_ch21.png'))
        await page.locator('#aiResult').screenshot(path=os.path.join(OUT, 'app_v5_03_result_card.png'))
        # 파형·수치가 실제 측정값인지 캔버스 확인
        print('wave canvas', await page.evaluate("(() => {const c=document.querySelector('#aiWave'); return c ? [c.width,c.height] : null})()"))

        # 보정 버튼
        await page.click('[data-adj="green:1"]'); await page.wait_for_timeout(300)
        print('green+1 →', (await page.text_content('.ai-res-code')).strip())
        await page.click('[data-adj="green:-1"]'); await page.wait_for_timeout(300)
        print('green-1 →', (await page.text_content('.ai-res-code')).strip())

        # 상세 점검 / 현장 진단 연결
        if await page.locator('[data-ai-open]').count():
            await page.click('[data-ai-open]'); await page.wait_for_timeout(600)
            print('sheet code', (await page.text_content('#shCode')).strip())
            await page.screenshot(path=os.path.join(OUT, 'app_v5_04_sheet.png'))
            await page.click('#shDiag'); await page.wait_for_timeout(700)
            print('dx from ai:', (await page.text_content('.dx-cb-code')).strip(),
                  '| fam', (await page.text_content('.dx-pg-top b')).strip())
            await page.click('.dx-prog [data-dx="reset"]'); await page.wait_for_timeout(400)

        # ---------- 2) 샘플 3종 ----------
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)
        for sid, nm in (('lgIn', 'LG실내기'), ('carrier', '캐리어'), ('samsung', '삼성')):
            await page.click(f'#samples [data-samp="{sid}"]'); await page.wait_for_timeout(900)
            print('sample', nm, '→', (await page.text_content('.ai-res-code')).strip(),
                  '|', (await page.text_content('.meas-row b')).strip())

        # ---------- 3) QR 모달 ----------
        await page.click('#qrBtn'); await page.wait_for_timeout(500)
        print('qr open', 'on' in (await page.get_attribute('#qrModal', 'class')),
              '| modules', await page.evaluate("document.querySelectorAll('#qrWrap svg path').length"))
        await page.screenshot(path=os.path.join(OUT, 'app_v5_05_qr_modal.png'))
        await page.locator('#qrWrap').screenshot(path=os.path.join(OUT, 'app_v5_06_qr_only.png'))
        await page.click('#qrCopy'); await page.wait_for_timeout(300)
        print('copy toast', (await page.text_content('#toast')).strip(),
              '| clipboard', await page.evaluate("navigator.clipboard.readText().catch(()=> 'n/a')"))
        await page.click('#qrClose'); await page.wait_for_timeout(300)

        # ---------- 4) 검색 회귀 + 즐겨찾기 ----------
        await page.click('#tabbar button[data-tab="search"]'); await page.wait_for_timeout(300)
        await page.fill('#q', 'C101'); await page.press('#q', 'Enter'); await page.wait_for_timeout(400)
        print('search C101', (await page.text_content('#listCount')).strip(),
              '| focus', await page.evaluate('document.activeElement.id'))
        await page.fill('#q', '배수'); await page.press('#q', 'Enter'); await page.wait_for_timeout(400)
        print('search 배수', (await page.text_content('#listCount')).strip())
        await page.click('#clearQ'); await page.wait_for_timeout(300)
        await page.click('#cards .card:first-child [data-star]'); await page.wait_for_timeout(300)
        print('fav toast', (await page.text_content('#toast')).strip())
        await page.click('#viewChips .chip[data-view="fav"]'); await page.wait_for_timeout(300)
        fav = await page.text_content('#listCount')
        print('fav list', fav.strip())
        await page.click('#viewChips .chip[data-view="fav"] ~ .chip, #viewChips .chip[data-view="all"]')
        await page.wait_for_timeout(300)
        await page.click('#cards .card:nth-child(3)'); await page.wait_for_timeout(500)
        await page.screenshot(path=os.path.join(OUT, 'app_v5_07_star_sheet.png'))
        await page.click('#sheetClose'); await page.wait_for_timeout(300)
        await page.click('#viewChips .chip[data-view="recent"]'); await page.wait_for_timeout(300)
        print('recent list', (await page.text_content('#listCount')).strip())
        await page.screenshot(path=os.path.join(OUT, 'app_v5_08_recent.png'))
        await page.click('#viewChips .chip[data-view="all"]'); await page.wait_for_timeout(300)

        # ---------- 5) 현장 진단 회귀 ----------
        await page.click('#tabbar button[data-tab="check"]'); await page.wait_for_timeout(400)
        print('dx start fams', await page.locator('#dxFams .dx-fam').count(), '| situ', await page.locator('#dxSitu button').count())
        await page.click('#dxFams .dx-fam[data-fam="inv"]'); await page.wait_for_timeout(400)
        s1 = (await page.text_content('.dx-stepno')).strip()
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(350)
        s2 = (await page.text_content('.dx-stepno')).strip()
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(350)
        s3 = (await page.text_content('.dx-stepno')).strip()
        await page.click('[data-dx="ok"]'); await page.wait_for_timeout(500)
        print('dx', s1, '→', s2, '→', s3, '| result', (await page.text_content('.dx-result h3')).replace('\n', ' ').strip())
        await page.click('.dx-foot [data-dx="reset"]'); await page.wait_for_timeout(400)
        await page.click('#dxFams .dx-fam[data-fam="fan"]'); await page.wait_for_timeout(400)
        for i in range(4):
            await page.click('[data-dx="fail"]'); await page.wait_for_timeout(320)
        print('escalate', (await page.text_content('.dx-result h3')).replace('\n', ' ').strip(),
              '| tel links(브랜드 없음)', await page.locator('.dx-contact a[href^="tel:"]').count())
        await page.screenshot(path=os.path.join(OUT, 'app_v5_09_dx_escalate.png'))
        # 코드로 들어온 진단은 제조사 전화가 붙는다
        await page.click('#tabbar button[data-tab="search"]'); await page.wait_for_timeout(300)
        await page.fill('#q', 'CH21'); await page.press('#q', 'Enter'); await page.wait_for_timeout(400)
        await page.click('#cards .card'); await page.wait_for_timeout(500)
        await page.click('#shDiag'); await page.wait_for_timeout(600)
        for i in range(4):
            await page.click('[data-dx="fail"]'); await page.wait_for_timeout(320)
        tel_n = await page.locator('.dx-contact a[href^="tel:"]').count()
        tel_t = (await page.text_content('.dx-contact a[href^="tel:"] .cp')).strip() if tel_n else ''
        print('dx(CH21) escalate | tel', tel_n, '|', tel_t)
        await page.screenshot(path=os.path.join(OUT, 'app_v5_09b_dx_tel.png'))
        await page.click('.dx-foot [data-dx="reset"]'); await page.wait_for_timeout(300)

        # ---------- 6) 아카데미 ----------
        await page.click('#tabbar button[data-tab="promo"]'); await page.wait_for_timeout(400)
        print('centers', await page.locator('#centers .center-row').count(),
              '| tel', await page.locator('#centers a[href^="tel:"]').count(),
              '| stats', (await page.text_content('#stats')).strip()[:50])
        await page.screenshot(path=os.path.join(OUT, 'app_v5_10_academy.png'))
        await page.click('[data-qr]'); await page.wait_for_timeout(400)
        print('academy QR open', 'on' in (await page.get_attribute('#qrModal', 'class')))
        await page.click('#qrClose'); await page.wait_for_timeout(200)

        # ---------- 7): 오버플로·오류 ----------
        ov = await page.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('*').forEach(el => {
            const s = getComputedStyle(el);
            if (el.scrollWidth - el.clientWidth > 2 && s.overflowX !== 'auto' && s.overflowX !== 'scroll')
              bad.push((el.tagName + '.' + el.className).slice(0, 50) + ' ' + el.scrollWidth + '/' + el.clientWidth);
          });
          return { body: document.body.scrollWidth, win: window.innerWidth, bad: bad.slice(0, 6) };
        }""")
        print('overflow', json.dumps(ov, ensure_ascii=False))
        print('ERRORS', errs)
        await b.close()

asyncio.run(main())
