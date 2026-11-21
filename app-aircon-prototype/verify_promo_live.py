# -*- coding: utf-8 -*-
"""GitHub Pages 라이브 검증 — 아카데미 탭 쾌적하마 홍보 반영 확인 (390x844)
검사:
 a) 히어로 버튼 4개 배치(2열, 넘침 없음) + nicehama.co.kr/cjyacademy.com 링크
 b) 쾌적하마 카드: 홈페이지·블로그·tel: 링크, 금지어((주)잡고릴라) 없음
 c) 문의 모달: 홈페이지·블로그·전화 링크 노출
 d) QR 모달: URL + OpenCV 디코드 일치
 e) LED 찾기: test_led_ch21.mp4 → CH21
 f) 검색 회귀: CH21 입력 시 결과 노출
 g) 콘솔/페이지 오류 0건, 탭바 4개 완전 노출, 가로 넘침 없음
"""
import os, asyncio, json
import cv2
from playwright.async_api import async_playwright

URL = 'https://nicehama.github.io/aircode/'
VID = '/workspace/downloads/test_led_ch21.mp4'
OUT = '/workspace/downloads'


async def main():
    r = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True,
                                  permissions=['clipboard-read', 'clipboard-write'])
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)

        resp = await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(900)
        r['http'] = resp.status
        r['title'] = await page.title()
        r['entries'] = await page.evaluate('DATA.entries.length')
        r['served_new'] = await page.evaluate("document.body.innerHTML.includes('쾌적하마 서비스 안내')")

        # ---------- 아카데미 탭 ----------
        await page.click('#tabbar button[data-tab="promo"]')
        await page.wait_for_timeout(600)
        r['hero_btns'] = await page.evaluate("""
          (() => {
            const hero = document.querySelector('.promo-hero').getBoundingClientRect();
            return Array.from(document.querySelectorAll('#tab-promo .promo-btns > *')).map(el => {
              const b = el.getBoundingClientRect();
              return {text: (el.textContent||'').trim(), href: el.getAttribute('href'),
                      w: +b.width.toFixed(1), top: +b.top.toFixed(1), left: +b.left.toFixed(1),
                      overflow: b.right > hero.right - 0.5 || el.scrollWidth > el.clientWidth + 1};
            });
          })()""")
        r['card_links'] = await page.evaluate("""
          (() => {
            const card = Array.from(document.querySelectorAll('#tab-promo .promo-card'))
              .find(c => (c.textContent||'').includes('쾌적하마'));
            return {h: +card.getBoundingClientRect().height.toFixed(1),
                    items: Array.from(card.querySelectorAll('a,button')).map(el => ({
                      text: (el.textContent||'').trim().replace(/\\s+/g,' '), href: el.getAttribute('href'),
                      overflow: el.scrollWidth > el.clientWidth + 1}))};
          })()""")
        r['links'] = await page.evaluate("""({
          homepage: !!document.querySelector('#tab-promo a[href="https://www.nicehama.co.kr"]'),
          blog: !!document.querySelector('#tab-promo a[href="https://blog.naver.com/nice_hama"]'),
          tel: !!document.querySelector('#tab-promo a[href="tel:02-6346-0075"]'),
          academy: !!document.querySelector('#tab-promo a[href="https://cjyacademy.com"]')
        })""")
        r['forbidden_word'] = await page.evaluate("document.body.innerText.includes('잡고릴라')")
        r['layout'] = await page.evaluate("""({
          docOverflowX: document.documentElement.scrollWidth > window.innerWidth + 0.5,
          tabs: Array.from(document.querySelectorAll('#tabbar button')).map(bt => {
            const b = bt.getBoundingClientRect();
            return {label: bt.textContent.trim(), inside: b.top >= -0.5 && b.bottom <= window.innerHeight + 0.5};
          })
        })""")

        # 스크린샷: (1) 844 상단, (2) 한눈에 보이는 긴 뷰포트는 별도 컨텍스트
        await page.evaluate("document.querySelector('main').scrollTop = 0")
        await page.wait_for_timeout(250)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_academy_promo_top.png'))
        card = page.locator('#tab-promo .promo-card', has_text='쾌적하마').first
        await page.evaluate("""(() => {
          const main = document.querySelector('main');
          const card = Array.from(document.querySelectorAll('#tab-promo .promo-card'))
            .find(c => c.textContent.includes('쾌적하마'));
          const top = card.getBoundingClientRect().top + main.scrollTop - main.getBoundingClientRect().top - 16;
          main.scrollTop = top;
        })()""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_academy_promo_card.png'))

        # ---------- 문의 모달 ----------
        await page.click('#tab-promo .link-btn.go')
        await page.wait_for_timeout(450)
        r['modal'] = await page.evaluate("""(() => {
          const l = document.getElementById('modalLinks');
          return {title: document.getElementById('modalTitle').textContent,
                  links: Array.from(l.querySelectorAll('a')).map(a => ({t: a.textContent.trim(), h: a.getAttribute('href')})),
                  visible: getComputedStyle(l).display !== 'none'};})()""")
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_academy_inquiry_modal.png'))
        await page.click('#modalOk')
        await page.wait_for_timeout(300)

        # ---------- QR ----------
        await page.evaluate("document.querySelector('main').scrollTop = 0")
        await page.click('#qrBtn')
        await page.wait_for_timeout(500)
        r['qr_url_text'] = (await page.text_content('#qrUrl')).strip()
        await page.locator('#qrWrap').screenshot(path='/workspace/tmp_gh_qr_only.png')
        val, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread('/workspace/tmp_gh_qr_only.png'))
        r['qr_decoded'] = val
        await page.click('#qrClose')
        await page.wait_for_timeout(300)

        # ---------- 검색 회귀 ----------
        await page.click('#tabbar button[data-tab="search"]')
        await page.wait_for_timeout(400)
        await page.fill('#q', 'CH21')
        await page.wait_for_timeout(700)
        r['search'] = await page.evaluate("""({title: document.getElementById('listTitle').textContent,
            count: document.getElementById('listCount').textContent,
            cards: document.querySelectorAll('#cards .card').length})""")
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_search_regress.png'))
        await page.fill('#q', '')
        await page.wait_for_timeout(400)

        # ---------- LED 판독 ----------
        await page.click('#tabbar button[data-tab="led"]')
        await page.wait_for_timeout(600)
        await page.set_input_files('#fileIn', VID)
        await page.wait_for_function('ai && ai.result', timeout=60000)
        await page.wait_for_timeout(800)
        r['led_code'] = (await page.text_content('.ai-res-code')).strip()
        r['led_state'] = await page.evaluate('({mode:ai.result.mode, frames:ai.result.frames, pulses:ai.result.pulses.length})')

        r['errors'] = errs
        await b.close()

    # ---------- 한눈에 보는 스크린샷(390 폭, 긴 뷰포트) ----------
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        ctx = await b.new_context(viewport={'width': 390, 'height': 1600}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(900)
        await page.click('#tabbar button[data-tab="promo"]')
        await page.wait_for_timeout(600)
        await page.evaluate("document.querySelector('main').scrollTop = 0")
        await page.wait_for_timeout(200)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_academy_promo.png'))
        r['tall_shot'] = await page.evaluate("""(() => {
          const card = Array.from(document.querySelectorAll('#tab-promo .promo-card'))
            .find(c => (c.textContent||'').includes('쾌적하마')).getBoundingClientRect();
          return {top: +card.top.toFixed(1), bottom: +card.bottom.toFixed(1), vh: window.innerHeight};})()""")
        await b.close()

    print(json.dumps(r, ensure_ascii=False, indent=2))
    ok = (r['http'] == 200 and r['served_new'] and r['entries'] > 0
          and all(x in r for x in ('links',))
          and all(r['links'].values())
          and not r['forbidden_word']
          and len(r['hero_btns']) == 4 and not any(x['overflow'] for x in r['hero_btns'])
          and not any(x['overflow'] for x in r['card_links']['items'])
          and r['modal']['visible'] and len(r['modal']['links']) == 3
          and r['qr_decoded'] == 'https://nicehama.github.io/aircode/'
          and r['search']['cards'] >= 1
          and r['led_code'].startswith('CH21')
          and not r['layout']['docOverflowX']
          and all(t['inside'] for t in r['layout']['tabs'])
          and not r['errors'])
    print('\nALL CHECKS:', 'PASS' if ok else 'FAIL')


asyncio.run(main())
