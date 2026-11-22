# -*- coding: utf-8 -*-
"""홈 화면 추가 안내 — 로컬 dist 검수 (390x844)
 a) 진입 3곳(검색 탭 칩 / 아카데미 배포 카드 / QR 모달) 모두 모달을 연다
 b) 기종·브라우저 탭 3개 전환 + 자동 선택(UA별)
 c) 단계 문구·아이콘·글자 크기, 가로 넘침·세로 스크롤 확인
 d) 기존 기능 회귀: 검색 / LED / QR 모달
 e) 콘솔·페이지 오류 0건
"""
import os, asyncio, json
from playwright.async_api import async_playwright

LOCAL = 'file:///workspace/app-aircon-prototype/dist/index.html'
OUT = '/workspace/downloads'

UAS = {
    'iphone': ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 '
               '(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'ios'),
    'android': ('Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/126.0.0.0 Mobile Safari/537.36', 'android'),
    'desktop': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/126.0.0.0 Safari/537.36', 'ios'),
}


async def inspect(page):
    return await page.evaluate("""(() => {
      const box = document.querySelector('.howto-box').getBoundingClientRect();
      const sc = document.getElementById('howtoScroll');
      const pane = document.querySelector('.howto-pane.on');
      const steps = Array.from(pane.querySelectorAll('.how')).map(li => ({
        n: li.querySelector('.num').textContent.trim(),
        title: li.querySelector('.bd b').textContent.replace(/\\s+/g,' ').trim(),
        body: (li.querySelector('.bd p')||{}).textContent || '',
        pics: li.querySelectorAll('.pic, .word').length
      }));
      const sizes = {};
      ['pane .how .bd b', 'pane .how .bd p', '.kakao-box p', '.howto-done'].forEach(sel => {
        const el = document.querySelector('.howto-pane.on ' + sel.replace('pane ', ''));
        if (el) sizes[sel] = getComputedStyle(el).fontSize;
      });
      const tabW = Array.from(document.querySelectorAll('.howto-tab')).map(t => +t.getBoundingClientRect().width.toFixed(1));
      return {
        open: document.getElementById('howtoModal').classList.contains('on'),
        box: {w: +box.width.toFixed(1), h: +box.height.toFixed(1), top: +box.top.toFixed(1), bottom: +box.bottom.toFixed(1), vh: window.innerHeight},
        activeTab: (document.querySelector('.howto-tab.on')||{}).innerText,
        pane: pane ? pane.dataset.pane : null,
        steps, sizes, tabW,
        hasKakao: !!pane.querySelector('.kakao-box'),
        scroll: {sh: sc.scrollHeight, ch: sc.clientHeight, scrollable: sc.scrollHeight > sc.clientHeight + 1},
        overflowX: Array.from(pane.querySelectorAll('*')).some(el => el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).display !== 'inline'),
        docOverflow: document.documentElement.scrollWidth > window.innerWidth + 0.5,
      };
    })()""")


async def main():
    r = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        errs = []

        # ---------- 1) 아이폰 UA: 검색 탭 칩 → 모달 ----------
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True, user_agent=UAS['iphone'][0])
        page = await ctx.new_page()
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)
        await page.goto(LOCAL, wait_until='load')
        await page.wait_for_timeout(700)

        chip = await page.evaluate("""(() => {
          const c = document.getElementById('howtoChip'), b = c.getBoundingClientRect();
          const main = document.querySelector('main').getBoundingClientRect();
          return {text: c.innerText.replace(/\\s+/g,' ').trim(), w: +b.width.toFixed(1), h: +b.height.toFixed(1),
                  inView: b.top >= main.top && b.bottom <= main.bottom};
        })()""")
        r['chip'] = chip
        await page.screenshot(path=os.path.join(OUT, 'howto_01_main_chip.png'))

        await page.click('#howtoChip')
        await page.wait_for_timeout(450)
        r['ios'] = await inspect(page)
        await page.screenshot(path=os.path.join(OUT, 'howto_02_ios_safari.png'))

        # 탭 전환
        await page.click('.howto-tab[data-howto="android"]')
        await page.wait_for_timeout(350)
        r['android'] = await inspect(page)
        await page.screenshot(path=os.path.join(OUT, 'howto_03_android_chrome.png'))

        await page.click('.howto-tab[data-howto="samsung"]')
        await page.wait_for_timeout(350)
        r['samsung'] = await inspect(page)
        await page.screenshot(path=os.path.join(OUT, 'howto_04_samsung_internet.png'))

        r['switch_link'] = await page.evaluate("""(() => {
          document.querySelector('.howto-tab[data-howto="android"]').click();
          const b = document.getElementById('howtoSwitchSam');
          b.click();
          return document.querySelector('.howto-tab.on').dataset.howto;
        })()""")

        # 닫기 (백드롭/Escape/버튼)
        await page.click('#howtoOk')
        await page.wait_for_timeout(300)
        r['closed_by_ok'] = not await page.evaluate("document.getElementById('howtoModal').classList.contains('on')")

        # ---------- 2) 아카데미 배포 카드 버튼 ----------
        await page.click('#tabbar button[data-tab="promo"]')
        await page.wait_for_timeout(500)
        r['deploy_btn'] = await page.evaluate("""(() => {
          const card = document.querySelector('#tab-promo .deploy-card');
          const btns = Array.from(card.querySelectorAll('.deploy-btns button')).map(b => {
            const r = b.getBoundingClientRect();
            return {text: b.innerText.trim(), w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                    top: +r.top.toFixed(1), overflow: b.scrollWidth > b.clientWidth + 1};
          });
          const cr = card.getBoundingClientRect();
          return {btns, cardH: +cr.height.toFixed(1),
                  inside: Array.from(card.querySelectorAll('.deploy-btns button')).every(b => {
                    const r = b.getBoundingClientRect(); return r.right <= cr.right + .5 && r.left >= cr.left - .5;})};
        })()""")
        await page.evaluate("""(() => {
          const main = document.querySelector('main');
          const card = document.querySelector('#tab-promo .deploy-card');
          main.scrollTop = card.getBoundingClientRect().top + main.scrollTop - main.getBoundingClientRect().top - 12;
        })()""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(OUT, 'howto_05_academy_card.png'))
        await page.click('#tab-promo .deploy-card button.wide')
        await page.wait_for_timeout(450)
        r['from_academy'] = await page.evaluate("document.getElementById('howtoModal').classList.contains('on')")
        await page.click('#howtoClose')
        await page.wait_for_timeout(300)

        # ---------- 3) QR 모달 안내 버튼 ----------
        await page.evaluate("document.querySelector('main').scrollTop = 0")
        await page.click('#qrBtn')
        await page.wait_for_timeout(450)
        r['qr_btn'] = await page.evaluate("""(() => {
          const b = document.querySelector('.qr-howto'), box = document.querySelector('.qr-box').getBoundingClientRect();
          const r = b.getBoundingClientRect();
          return {text: b.innerText.trim(), visible: r.height > 0 && r.bottom <= box.bottom + .5,
                  fitsViewport: r.bottom <= window.innerHeight + .5, boxH: +box.height.toFixed(1)};
        })()""")
        await page.screenshot(path=os.path.join(OUT, 'howto_06_qr_modal.png'))
        await page.click('.qr-howto')
        await page.wait_for_timeout(450)
        r['from_qr'] = await page.evaluate("""({howto: document.getElementById('howtoModal').classList.contains('on'),
              qr: document.getElementById('qrModal').classList.contains('on')})""")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(300)
        r['closed_by_esc'] = not await page.evaluate("document.getElementById('howtoModal').classList.contains('on')")

        # ---------- 4) 기존 기능 회귀 ----------
        await page.click('#tabbar button[data-tab="search"]')
        await page.wait_for_timeout(300)
        await page.fill('#q', 'CH21')
        await page.wait_for_timeout(600)
        r['search'] = await page.evaluate("""({title: document.getElementById('listTitle').textContent,
            cards: document.querySelectorAll('#cards .card').length})""")
        await page.fill('#q', '')
        await page.wait_for_timeout(300)
        r['layout'] = await page.evaluate("""({
          docOverflowX: document.documentElement.scrollWidth > window.innerWidth + 0.5,
          tabs: Array.from(document.querySelectorAll('#tabbar button')).map(bt => {
            const b = bt.getBoundingClientRect();
            return {label: bt.textContent.trim(), inside: b.top >= -0.5 && b.bottom <= window.innerHeight + 0.5};})})""")

        # ---------- 5) 안드로이드 UA: 자동 선택 ----------
        ctx2 = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                   locale='ko-KR', is_mobile=True, has_touch=True, user_agent=UAS['android'][0])
        page2 = await ctx2.new_page()
        page2.on('pageerror', lambda e: errs.append('PAGEERROR(android): ' + str(e)))
        page2.on('console', lambda m: errs.append('CONSOLE(android): ' + m.text) if m.type == 'error' else None)
        await page2.goto(LOCAL, wait_until='load')
        await page2.wait_for_timeout(600)
        await page2.click('#howtoChip')
        await page2.wait_for_timeout(450)
        r['auto_android'] = await page2.evaluate("document.querySelector('.howto-tab.on').dataset.howto")
        r['install_btn'] = await page2.evaluate("""({hidden: document.getElementById('howtoInstallBtn').hidden,
            text: document.getElementById('howtoInstallBtn').innerText.trim()})""")
        await page2.screenshot(path=os.path.join(OUT, 'howto_07_android_auto.png'))
        await ctx2.close()

        # ---------- 6) 데스크톱 폴백 ----------
        ctx3 = await b.new_context(viewport={'width': 390, 'height': 844}, locale='ko-KR',
                                   user_agent=UAS['desktop'][0])
        page3 = await ctx3.new_page()
        page3.on('pageerror', lambda e: errs.append('PAGEERROR(desktop): ' + str(e)))
        await page3.goto(LOCAL, wait_until='load')
        await page3.wait_for_timeout(500)
        await page3.click('#howtoChip')
        await page3.wait_for_timeout(400)
        r['auto_desktop'] = await page3.evaluate("document.querySelector('.howto-tab.on').dataset.howto")
        await ctx3.close()

        r['errors'] = errs
        await b.close()

    print(json.dumps(r, ensure_ascii=False, indent=2))


asyncio.run(main())
