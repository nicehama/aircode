# -*- coding: utf-8 -*-
"""GitHub Pages 라이브 검증 — https://nicehama.github.io/aircode/ (390x844 모바일)
a) 메인: deed.page 배지 없음 + 하단 탭바 4개 완전 노출
b) QR 모달: URL 표기 + OpenCV 디코드 일치
c) LED 찾기: test_led_ch21.mp4 업로드 → CH21
d) 콘솔/페이지 에러 0건
"""
import os, asyncio, json
import cv2
from playwright.async_api import async_playwright

URL = 'https://nicehama.github.io/aircode/'
VID = '/workspace/downloads/test_led_ch21.mp4'
OUT = '/workspace/downloads'


async def main():
    results = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True,
                                  permissions=['clipboard-read', 'clipboard-write'])
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)

        r = await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(900)
        results['http'] = r.status
        results['title'] = await page.title()
        results['h1'] = (await page.text_content('.top-title')).strip()
        results['entries'] = await page.evaluate('DATA.entries.length')

        # ---------- a) 배지 없음 + 하단 탭바 ----------
        html = await page.content()
        badge_hits = {k: (k in html) for k in ('deed.page', 'Published with', 'Report abuse', 'deed')}
        results['badge_text_hits'] = badge_hits
        # 화면 하단 고정 요소 중 외부 배지 흉내(링크) 확인
        results['external_links'] = await page.evaluate(
            """Array.from(document.querySelectorAll('a[href^="http"]'))
                 .filter(a => !a.href.includes('nicehama.github.io'))
                 .map(a => ({href: a.href, text: (a.textContent||'').trim().slice(0,40)}))""")
        tabs = await page.evaluate("""
            (() => {
              const vh = window.innerHeight, vw = window.innerWidth;
              const bar = document.getElementById('tabbar');
              const br = bar.getBoundingClientRect();
              const cs = getComputedStyle(bar);
              const buttons = Array.from(bar.querySelectorAll('button')).map(btn => {
                const r = btn.getBoundingClientRect();
                const cx = r.left + r.width/2, cy = r.top + r.height/2;
                const hit = document.elementFromPoint(cx, cy);
                return {label: (btn.textContent||'').trim(),
                        top: +r.top.toFixed(1), bottom: +r.bottom.toFixed(1),
                        w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                        insideViewport: r.top >= -0.5 && r.bottom <= vh + 0.5 && r.left >= -0.5 && r.right <= vw + 0.5,
                        hitIsSelf: !!(hit && (btn === hit || btn.contains(hit)))};
              });
              const clip = document.elementFromPoint(br.left + br.width/2, Math.min(br.bottom - 2, vh - 2));
              return {vh, vw, barTop: +br.top.toFixed(1), barBottom: +br.bottom.toFixed(1),
                      barInside: br.bottom <= vh + 0.5, opacity: cs.opacity,
                      visible: cs.visibility, buttons,
                      bottomHitInBar: !!(clip && bar.contains(clip))};
            })()""")
        results['tabbar'] = tabs
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_main.png'))

        # ---------- b) QR 모달 ----------
        await page.click('#qrBtn')
        await page.wait_for_timeout(500)
        results['qr_url_text'] = (await page.text_content('#qrUrl')).strip()
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_qr.png'))
        await page.locator('#qrWrap').screenshot(path='/workspace/tmp_gh_qr_only.png')
        img = cv2.imread('/workspace/tmp_gh_qr_only.png')
        val, pts, _ = cv2.QRCodeDetector().detectAndDecode(img)
        results['qr_decoded'] = val
        results['qr_match'] = (val == 'https://nicehama.github.io/aircode/')
        await page.click('#qrClose')
        await page.wait_for_timeout(300)

        # ---------- c) LED 영상 판독 ----------
        await page.click('#tabbar button[data-tab="led"]')
        await page.wait_for_timeout(600)
        await page.set_input_files('#fileIn', VID)
        await page.wait_for_function('ai && ai.result', timeout=60000)
        await page.wait_for_timeout(800)
        results['led_code'] = (await page.text_content('.ai-res-code')).strip()
        results['led_meas'] = (await page.text_content('.meas-row b')).strip()
        results['led_state'] = await page.evaluate(
            '({mode:ai.result.mode, red:ai.result.red, green:ai.result.green, frames:ai.result.frames, auto:ai.result.auto, pulses:ai.result.pulses.length})')
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_led_ch21.png'))

        # ---------- d) 오류 ----------
        results['errors'] = errs
        await b.close()

    print(json.dumps(results, ensure_ascii=False, indent=2))
    ok = (results['http'] == 200 and not any(results['badge_text_hits'].values())
          and all(t['insideViewport'] and t['hitIsSelf'] for t in results['tabbar']['buttons'])
          and results['tabbar']['barInside']
          and results['qr_match'] and results['qr_url_text'] == 'https://nicehama.github.io/aircode/'
          and results['led_code'].startswith('CH21') and not results['errors'])
    print('\nALL CHECKS:', 'PASS' if ok else 'FAIL')


asyncio.run(main())
