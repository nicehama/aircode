# -*- coding: utf-8 -*-
"""현장 진단 탭 로컬 검수: 단계 진행·해결·판정·코드 연결·오버플로."""
import os, asyncio, json
from playwright.async_api import async_playwright

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
url = 'file://' + os.path.join(root, 'downloads', '에어컨_에러코드_앱_프로토타입.html')
shots = os.path.join(root, 'downloads')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)
        await page.goto(url); await page.wait_for_timeout(600)

        # 1) 현장 진단 탭 진입
        await page.click('#tabbar button[data-tab="check"]'); await page.wait_for_timeout(400)
        print('START visible:', await page.is_visible('#dxStart'),
              '| fams:', await page.locator('#dxFams .dx-fam').count(),
              '| situ:', await page.locator('#dxSitu button').count())
        await page.screenshot(path=os.path.join(shots, 'dx_local_1_start.png'))

        # 2) 계열 시작 → 그대로 2회 → 해결
        await page.click('#dxFams .dx-fam[data-fam="inv"]'); await page.wait_for_timeout(350)
        print('step1:', (await page.text_content('.dx-stepno') or '').strip(),
              '|', (await page.text_content('.dx-card h3') or '').strip())
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(350)
        print('after fail1:', (await page.text_content('.dx-stepno') or '').strip(),
              '| timeline:', await page.locator('.dx-tl-i').count())
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(350)
        print('after fail2:', (await page.text_content('.dx-stepno') or '').strip(),
              '| timeline:', await page.locator('.dx-tl-i').count())
        await page.screenshot(path=os.path.join(shots, 'dx_local_2_step3.png'))
        await page.click('[data-dx="ok"]'); await page.wait_for_timeout(450)
        print('SOLVED:', (await page.text_content('.dx-result h3') or '').strip(),
              '| summary rows:', await page.locator('.dx-sum .r').count())
        await page.screenshot(path=os.path.join(shots, 'dx_local_3_solved.png'))

        # 3) 처음부터 다시 → 4단계 모두 그대로 → 판정
        await page.click('.dx-prog [data-dx="reset"]'); await page.wait_for_timeout(300)
        print('back to start:', await page.is_visible('#dxStart'))
        await page.click('#dxFams .dx-fam[data-fam="fan"]'); await page.wait_for_timeout(300)
        for i in range(4):
            await page.click('[data-dx="fail"]'); await page.wait_for_timeout(300)
        print('ESCALATE:', (await page.text_content('.dx-result h3') or '').replace('\n', ' ').strip(),
              '| contacts:', await page.locator('.dx-contact').count(),
              '| summary rows:', await page.locator('.dx-sum .r').count())
        await page.screenshot(path=os.path.join(shots, 'dx_local_4_escalate.png'))

        # 4) 검색 상세 시트 → 이 코드로 현장 진단
        await page.click('#tabbar button[data-tab="search"]'); await page.wait_for_timeout(300)
        await page.fill('#q', 'C101'); await page.wait_for_timeout(300)
        await page.click('#cards .card'); await page.wait_for_timeout(500)
        print('sheet diag btn:', (await page.text_content('#shDiag') or '').strip())
        await page.screenshot(path=os.path.join(shots, 'dx_local_5_sheet.png'))
        await page.click('#shDiag'); await page.wait_for_timeout(500)
        print('codebar:', (await page.text_content('.dx-cb-code') or '').strip(),
              '|', (await page.text_content('.dx-cb-main b') or '').strip()[:40],
              '| tab on:', await page.get_attribute('#tabbar button[data-tab="check"]', 'class'))
        await page.screenshot(path=os.path.join(shots, 'dx_local_6_code.png'))

        # 5) 코드 직접 입력 + 잘못된 코드
        await page.click('.dx-prog [data-dx="reset"]'); await page.wait_for_timeout(300)
        await page.fill('#dxCode', 'CH21'); await page.click('#dxCodeGo'); await page.wait_for_timeout(400)
        print('typed CH21 codebar:', (await page.text_content('.dx-cb-code') or '').strip())
        await page.click('.dx-prog [data-dx="reset"]'); await page.wait_for_timeout(300)
        await page.fill('#dxCode', 'ZZZ9'); await page.click('#dxCodeGo'); await page.wait_for_timeout(400)
        print('unknown code codebar:', (await page.text_content('.dx-cb-code') or '').strip(),
              '| lead:', (await page.text_content('.dx-cb-main b') or '').strip()[:30])

        # 6) 진행 상태 유지 (reload)
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(300)
        await page.reload(); await page.wait_for_timeout(500)
        await page.click('#tabbar button[data-tab="check"]'); await page.wait_for_timeout(300)
        print('after reload step:', (await page.text_content('.dx-stepno') or '').strip(),
              '| timeline:', await page.locator('.dx-tl-i').count())

        # 7) 오버플로 / 높이 점검
        ov = await page.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('#tab-check *').forEach(el => {
            const s = getComputedStyle(el);
            if (el.scrollWidth - el.clientWidth > 2 && s.overflowX !== 'auto' && s.overflowX !== 'scroll')
              bad.push((el.tagName+'.'+el.className).slice(0,50)+' '+el.scrollWidth+'/'+el.clientWidth);
          });
          return {body:document.body.scrollWidth, win:window.innerWidth, bad:bad.slice(0,8)};
        }""")
        print('overflow:', json.dumps(ov, ensure_ascii=False))

        # 8) 기존 탭 회귀
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)
        await page.click('#tapRed'); await page.click('#tapRed'); await page.click('#tapGreen'); await page.wait_for_timeout(300)
        print('LG:', (await page.text_content('#lgCode') or '').strip())
        await page.click('#tabbar button[data-tab="promo"]'); await page.wait_for_timeout(300)
        print('centers rows:', await page.locator('#centers .center-row').count())
        print('ERRORS:', errs)
        await b.close()

asyncio.run(main())
