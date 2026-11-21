# -*- coding: utf-8 -*-
"""배포 URL 검증: 현장 진단 흐름·코드 연결·기존 탭 회귀, 390x844 스크린샷."""
import os, asyncio, json
from playwright.async_api import async_playwright

URL = 'https://nicehama.github.io/aircode/'
out = '/workspace/downloads'

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)
        r = await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(700)
        print('HTTP', r.status, '| title', await page.title())
        print('badge', await page.text_content('#topBadge'), '| entries', await page.evaluate('DATA.entries.length'))

        # 1) 현장 진단 탭 진입 + 스크린샷
        await page.click('#tabbar button[data-tab="check"]'); await page.wait_for_timeout(500)
        print('start:', await page.is_visible('#dxStart'), '| fams', await page.locator('#dxFams .dx-fam').count(),
              '| situ', await page.locator('#dxSitu button').count())
        await page.screenshot(path=os.path.join(out, 'app_preview_3_checklist.png'))

        # 2) 계열 → 그대로 2회 → 해결
        await page.click('#dxFams .dx-fam[data-fam="inv"]'); await page.wait_for_timeout(400)
        s1 = (await page.text_content('.dx-stepno') or '').strip()
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(400)
        s2 = (await page.text_content('.dx-stepno') or '').strip()
        t2 = await page.locator('.dx-tl-i').count()
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(400)
        s3 = (await page.text_content('.dx-stepno') or '').strip()
        await page.screenshot(path=os.path.join(out, 'app_preview_10_dx_step.png'))
        await page.click('[data-dx="ok"]'); await page.wait_for_timeout(500)
        print('steps:', s1, '->', s2, '(tl', t2, ') ->', s3)
        print('solved:', (await page.text_content('.dx-result h3') or '').strip(),
              '| rows', await page.locator('.dx-sum .r').count())
        await page.screenshot(path=os.path.join(out, 'app_preview_11_dx_solved.png'))
        # 복사 버튼 동작(클립보드 권한 없이도 토스트 확인)
        await page.click('[data-dx="copy"]'); await page.wait_for_timeout(400)
        print('copy toast:', (await page.text_content('#toast') or '').strip())

        # 3) 판정 경로
        await page.click('.dx-foot [data-dx="reset"]'); await page.wait_for_timeout(400)
        await page.click('#dxFams .dx-fam[data-fam="fan"]'); await page.wait_for_timeout(400)
        for i in range(4):
            await page.click('[data-dx="fail"]'); await page.wait_for_timeout(320)
        print('escalate:', (await page.text_content('.dx-result h3') or '').replace('\n', ' ').strip(),
              '| rows', await page.locator('.dx-sum .r').count(),
              '| contact', await page.locator('.dx-contact .center-row').count())
        await page.screenshot(path=os.path.join(out, 'app_preview_12_dx_escalate.png'))

        # 4) 검색 상세 시트 → 이 코드로 현장 진단
        await page.click('#tabbar button[data-tab="search"]'); await page.wait_for_timeout(300)
        await page.fill('#q', 'CH21'); await page.wait_for_timeout(300)
        await page.click('#cards .card'); await page.wait_for_timeout(600)
        print('sheet open:', await page.get_attribute('#sheet', 'class'))
        await page.screenshot(path=os.path.join(out, 'app_preview_13_sheet_diag.png'))
        await page.click('#shDiag'); await page.wait_for_timeout(600)
        print('from sheet →', (await page.text_content('.dx-cb-code') or '').strip(),
              '|', (await page.text_content('.dx-cb-main b') or '').strip()[:40],
              '| tabclass', await page.get_attribute('#tabbar button[data-tab="check"]', 'class'))

        # 5) 코드 직접 입력 / 표에 없는 코드
        await page.click('.dx-prog [data-dx="reset"]'); await page.wait_for_timeout(400)
        await page.fill('#dxCode', 'C101'); await page.click('#dxCodeGo'); await page.wait_for_timeout(500)
        print('typed C101 →', (await page.text_content('.dx-cb-code') or '').strip())
        await page.click('.dx-prog [data-dx="reset"]'); await page.wait_for_timeout(400)
        await page.fill('#dxCode', 'ZZZ9'); await page.click('#dxCodeGo'); await page.wait_for_timeout(500)
        print('unknown →', (await page.text_content('.dx-cb-code') or '').strip(),
              '|', (await page.text_content('.dx-cb-main b') or '').strip()[:30])

        # 6) 새로고침 후 상태 유지
        await page.click('[data-dx="fail"]'); await page.wait_for_timeout(300)
        await page.reload(wait_until='load'); await page.wait_for_timeout(700)
        await page.click('#tabbar button[data-tab="check"]'); await page.wait_for_timeout(400)
        print('after reload:', (await page.text_content('.dx-stepno') or '').strip(),
              '| tl', await page.locator('.dx-tl-i').count())

        # 7) 기존 탭 회귀
        await page.click('#tabbar button[data-tab="search"]'); await page.wait_for_timeout(300)
        await page.fill('#q', 'C101'); await page.press('#q', 'Enter'); await page.wait_for_timeout(400)
        print('search Enter:', await page.text_content('#listCount'),
              '| focus', await page.evaluate("document.activeElement.id"))
        await page.fill('#q', '배수'); await page.press('#q', 'Enter'); await page.wait_for_timeout(400)
        print('search 배수:', await page.text_content('#listCount'))
        await page.click('#clearQ'); await page.wait_for_timeout(300)
        await page.click('#tabbar button[data-tab="led"]'); await page.wait_for_timeout(300)
        await page.click('#tapRed'); await page.click('#tapRed'); await page.click('#tapGreen'); await page.wait_for_timeout(300)
        print('LG counter:', (await page.text_content('#lgCode') or '').strip())
        await page.click('#tabbar button[data-tab="promo"]'); await page.wait_for_timeout(300)
        print('centers:', await page.locator('#centers .center-row').count(),
              '| stats:', (await page.text_content('#stats') or '').strip()[:40])

        ov = await page.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('*').forEach(el => {
            const s = getComputedStyle(el);
            if (el.scrollWidth - el.clientWidth > 2 && s.overflowX !== 'auto' && s.overflowX !== 'scroll')
              bad.push((el.tagName+'.'+el.className).slice(0,50)+' '+el.scrollWidth+'/'+el.clientWidth);
          });
          return {body:document.body.scrollWidth, win:window.innerWidth, bad:bad.slice(0,6)};
        }""")
        print('overflow:', json.dumps(ov, ensure_ascii=False))
        print('ERRORS:', errs)
        await b.close()

asyncio.run(main())
