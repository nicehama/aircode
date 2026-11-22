# -*- coding: utf-8 -*-
"""GitHub Pages 라이브 검증 — 홈 화면 추가 안내 (v13, 390x844)
 a) HTTP 200 + 내려받은 본문이 dist/index.html과 바이트 동일
 b) 콘솔·페이지 오류 0건
 c) 진입 3곳(검색 탭 칩 / 아카데미 배포 카드 / QR 모달) → 모달 열림
 d) 기종·브라우저 탭 3개 전환 + UA별 자동 선택, 단계 문구·글자 크기·넘침
 e) 회귀: 검색 CH21, LED 영상 판독 CH21, QR URL·OpenCV 디코드, 탭바 4개, 가로 스크롤 없음
 f) 스크린샷 저장(downloads/)
"""
import os, asyncio, json, hashlib
import cv2
from playwright.async_api import async_playwright

URL = 'https://nicehama.github.io/aircode/'
DIST = '/workspace/app-aircon-prototype/dist/index.html'
VID = '/workspace/downloads/test_led_ch21.mp4'
OUT = '/workspace/downloads'

UA_IPHONE = ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 '
             '(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1')
UA_ANDROID = ('Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/126.0.0.0 Mobile Safari/537.36')


async def pane_info(page):
    return await page.evaluate("""(() => {
      const box = document.querySelector('.howto-box').getBoundingClientRect();
      const sc = document.getElementById('howtoScroll');
      const pane = document.querySelector('.howto-pane.on');
      return {
        tab: document.querySelector('.howto-tab.on').dataset.howto,
        box: {w: +box.width.toFixed(1), h: +box.height.toFixed(1),
              top: +box.top.toFixed(1), bottom: +box.bottom.toFixed(1), vh: window.innerHeight},
        steps: Array.from(pane.querySelectorAll('.how')).map(li => ({
          n: li.querySelector('.num').textContent.trim(),
          title: li.querySelector('.bd > b').textContent.replace(/\\s+/g, ' ').trim(),
          fs: getComputedStyle(li.querySelector('.bd > b')).fontSize,
          pfs: getComputedStyle(li.querySelector('.bd p')).fontSize,
          pics: li.querySelectorAll('.pic, .word').length})),
        kakao: (pane.querySelector('.kakao-box') || {}).textContent ? pane.querySelector('.kakao-box').textContent.replace(/\\s+/g, ' ').trim() : null,
        done: (pane.querySelector('.howto-done') || {}).textContent ? pane.querySelector('.howto-done').textContent.replace(/\\s+/g, ' ').trim() : null,
        scroll: {sh: sc.scrollHeight, ch: sc.clientHeight, fits: sc.scrollHeight <= sc.clientHeight + 1},
        overflowX: document.documentElement.scrollWidth > window.innerWidth + 0.5,
      };
    })()""")


async def main():
    r = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')

        # ---------- 기본(390x844, 모바일) ----------
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True,
                                  permissions=['clipboard-read', 'clipboard-write'])
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)

        resp = await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(900)
        body = await page.content()
        r['http'] = resp.status
        r['title'] = await page.title()
        r['served'] = await page.evaluate("document.getElementById('howtoChip') !== null")
        r['sum_local'] = hashlib.sha256(open(DIST, 'rb').read()).hexdigest()[:12]
        raw = await page.evaluate('fetch(location.href).then(r => r.text())')
        r['sum_live'] = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]
        r['bytes_live'] = len(raw.encode('utf-8'))
        r['same_bytes'] = r['sum_local'] == r['sum_live']
        r['forbidden'] = await page.evaluate("document.body.innerText.includes('잡고릴라')")

        # 메인 화면: 칩 위치·겹침
        r['chip'] = await page.evaluate("""(() => {
          const c = document.getElementById('howtoChip'), b = c.getBoundingClientRect();
          const main = document.querySelector('main').getBoundingClientRect();
          const el = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
          return {text: c.innerText.replace(/\\s+/g, ' ').trim(), w: +b.width.toFixed(1), h: +b.height.toFixed(1),
                  top: +b.top.toFixed(1), bottom: +b.bottom.toFixed(1),
                  inView: b.top >= main.top && b.bottom <= main.bottom,
                  hitSelf: !!(el && (el === c || c.contains(el)))};
        })()""")
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_01_main.png'))

        # 칩 → 모달 (기본 UA: 안드로이드 자동 선택 여부 확인)
        await page.click('#howtoChip')
        await page.wait_for_timeout(500)
        r['modal_opened'] = await page.evaluate("document.getElementById('howtoModal').classList.contains('on')")
        r['default_tab'] = await page.evaluate("document.querySelector('.howto-tab.on').dataset.howto")
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_02_default.png'))

        r['ios'] = None
        await page.click('.howto-tab[data-howto="ios"]')
        await page.wait_for_timeout(350)
        r['ios'] = await pane_info(page)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_03_ios_safari.png'))

        await page.click('.howto-tab[data-howto="android"]')
        await page.wait_for_timeout(350)
        r['android'] = await pane_info(page)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_04_android_chrome.png'))

        await page.click('.howto-tab[data-howto="samsung"]')
        await page.wait_for_timeout(350)
        r['samsung'] = await pane_info(page)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_05_samsung_internet.png'))

        await page.click('.howto-tab[data-howto="android"]')
        await page.wait_for_timeout(250)
        r['switch_to_samsung'] = await page.evaluate("""(() => {
          document.getElementById('howtoSwitchSam').click();
          return document.querySelector('.howto-tab.on').dataset.howto;})()""")
        r['install_btn_hidden'] = await page.evaluate("document.getElementById('howtoInstallBtn').hidden")

        await page.click('#howtoOk')
        await page.wait_for_timeout(300)
        r['closed_by_ok'] = not await page.evaluate("document.getElementById('howtoModal').classList.contains('on')")

        # ---------- 아카데미 탭 ----------
        await page.click('#tabbar button[data-tab="promo"]')
        await page.wait_for_timeout(600)
        r['academy_btn'] = await page.evaluate("""(() => {
          const card = document.querySelector('#tab-promo .deploy-card');
          const b = card.querySelector('.deploy-btns button.wide'), br = b.getBoundingClientRect();
          const cr = card.getBoundingClientRect();
          return {text: b.innerText.trim(), w: +br.width.toFixed(1), h: +br.height.toFixed(1),
                  insideCard: br.left >= cr.left - .5 && br.right <= cr.right + .5 && br.bottom <= cr.bottom + .5,
                  overflow: b.scrollWidth > b.clientWidth + 1};})()""")
        await page.evaluate("""(() => {
          const main = document.querySelector('main');
          const card = document.querySelector('#tab-promo .deploy-card');
          main.scrollTop = card.getBoundingClientRect().top + main.scrollTop - main.getBoundingClientRect().top - 12;
        })()""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_06_academy_card.png'))
        await page.click('#tab-promo .deploy-card button.wide')
        await page.wait_for_timeout(450)
        r['open_from_academy'] = await page.evaluate("document.getElementById('howtoModal').classList.contains('on')")
        await page.click('#howtoClose')
        await page.wait_for_timeout(300)

        # ---------- QR 모달 ----------
        await page.evaluate("document.querySelector('main').scrollTop = 0")
        await page.click('#qrBtn')
        await page.wait_for_timeout(500)
        r['qr'] = await page.evaluate("""(() => {
          const b = document.querySelector('.qr-howto'), br = b.getBoundingClientRect();
          const box = document.querySelector('.qr-box').getBoundingClientRect();
          return {text: b.innerText.trim(), h: +br.height.toFixed(1),
                  insideBox: br.bottom <= box.bottom + .5, inViewport: br.bottom <= window.innerHeight + .5,
                  url: document.getElementById('qrUrl').textContent.trim()};})()""")
        await page.locator('#qrWrap').screenshot(path='/workspace/tmp_howto_qr.png')
        val, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread('/workspace/tmp_howto_qr.png'))
        r['qr_decoded'] = val
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_07_qr_modal.png'))
        await page.click('.qr-howto')
        await page.wait_for_timeout(450)
        r['open_from_qr'] = await page.evaluate("""({howto: document.getElementById('howtoModal').classList.contains('on'),
              qr: document.getElementById('qrModal').classList.contains('on')})""")
        await page.screenshot(path=os.path.join(OUT, 'gh_pages_howto_08_from_qr.png'))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(300)

        # ---------- 회귀 ----------
        await page.click('#tabbar button[data-tab="search"]')
        await page.wait_for_timeout(400)
        await page.fill('#q', 'CH21')
        await page.wait_for_timeout(700)
        r['search'] = await page.evaluate("""({title: document.getElementById('listTitle').textContent,
            cards: document.querySelectorAll('#cards .card').length})""")
        await page.fill('#q', '')
        await page.wait_for_timeout(400)
        r['layout'] = await page.evaluate("""({
          docOverflowX: document.documentElement.scrollWidth > window.innerWidth + 0.5,
          tabs: Array.from(document.querySelectorAll('#tabbar button')).map(bt => {
            const b = bt.getBoundingClientRect();
            return {label: bt.textContent.trim(), inside: b.top >= -0.5 && b.bottom <= window.innerHeight + 0.5};})})""")

        await page.click('#tabbar button[data-tab="led"]')
        await page.wait_for_timeout(700)
        await page.set_input_files('#fileIn', VID)
        await page.wait_for_function('ai && ai.result', timeout=90000)
        await page.wait_for_timeout(900)
        r['led_code'] = (await page.text_content('.ai-res-code')).strip()
        r['led_state'] = await page.evaluate('({mode:ai.result.mode, frames:ai.result.frames, pulses:ai.result.pulses.length})')

        r['errors'] = errs
        await ctx.close()

        # ---------- UA별 자동 선택 ----------
        for name, ua in (('iphone', UA_IPHONE), ('android', UA_ANDROID)):
            ctx2 = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                       locale='ko-KR', is_mobile=True, has_touch=True, user_agent=ua)
            pg = await ctx2.new_page()
            errs2 = []
            pg.on('pageerror', lambda e: errs2.append('PAGEERROR(' + name + '): ' + str(e)))
            pg.on('console', lambda m: errs2.append('CONSOLE(' + name + '): ' + m.text) if m.type == 'error' else None)
            await pg.goto(URL, wait_until='load')
            await pg.wait_for_timeout(700)
            await pg.click('#howtoChip')
            await pg.wait_for_timeout(450)
            r['auto_' + name] = await pg.evaluate("document.querySelector('.howto-tab.on').dataset.howto")
            if name == 'iphone':
                await pg.screenshot(path=os.path.join(OUT, 'gh_pages_howto_09_iphone_auto.png'))
            errs.extend(errs2)
            await ctx2.close()

        await b.close()

        # ---------- 320 폭 확인(작은 폰) ----------
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        ctx = await b.new_context(viewport={'width': 375, 'height': 667}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True, user_agent=UA_IPHONE)
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR(375): ' + str(e)))
        await pg.goto(URL, wait_until='load')
        await pg.wait_for_timeout(700)
        await pg.click('#howtoChip')
        await pg.wait_for_timeout(450)
        r['small'] = await pane_info(pg)
        r['small']['errors'] = errs
        await pg.screenshot(path=os.path.join(OUT, 'gh_pages_howto_10_375.png'))
        await b.close()

    print(json.dumps(r, ensure_ascii=False, indent=2))

    ok = (r['http'] == 200 and r['served'] and r['same_bytes'] and not r['forbidden']
          and r['chip']['inView'] and r['chip']['hitSelf'] and r['modal_opened']
          and r['ios']['tab'] == 'ios' and len(r['ios']['steps']) == 3
          and r['android']['tab'] == 'android' and len(r['android']['steps']) == 3
          and r['samsung']['tab'] == 'samsung' and len(r['samsung']['steps']) == 3
          and all(pn['scroll']['fits'] for pn in (r['ios'], r['android'], r['samsung']))
          and r['switch_to_samsung'] == 'samsung'
          and r['closed_by_ok']
          and r['academy_btn']['insideCard'] and not r['academy_btn']['overflow']
          and r['open_from_academy']
          and r['qr']['insideBox'] and r['qr']['inViewport'] and r['open_from_qr']['howto']
          and r['qr_decoded'] == 'https://nicehama.github.io/aircode/'
          and r['search']['cards'] >= 1 and r['led_code'].startswith('CH21')
          and r['auto_iphone'] == 'ios' and r['auto_android'] == 'android'
          and not r['layout']['docOverflowX'] and all(t['inside'] for t in r['layout']['tabs'])
          and not r['errors'])
    print('\nALL CHECKS:', 'PASS' if ok else 'FAIL')


asyncio.run(main())
