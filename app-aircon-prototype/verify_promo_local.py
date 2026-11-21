# -*- coding: utf-8 -*-
"""아카데미 탭(쾌적하마 홍보) 로컬 검증 — 390x844 모바일
a) 히어로 버튼 배치(2열/줄바꿈) b) 쾌적하마 카드 링크 c) 문의 모달 링크
d) 탭바 가림/오버플로 없음 e) 콘솔·페이지 오류 0건
"""
import os, asyncio, json, sys
from playwright.async_api import async_playwright

PATH = '/workspace/downloads/에어컨_에러코드_앱_프로토타입.html'
OUT = os.environ.get('SHOT_DIR', '/workspace/browser')


async def main():
    r = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                  locale='ko-KR', is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        page.on('console', lambda m: errs.append('CONSOLE: ' + m.text) if m.type == 'error' else None)

        await page.goto('file://' + PATH, wait_until='load')
        await page.wait_for_timeout(500)
        await page.click('#tabbar button[data-tab="promo"]')
        await page.wait_for_timeout(500)

        r['hero_btns'] = await page.evaluate("""
          (() => {
            const bs = Array.from(document.querySelectorAll('#tab-promo .promo-btns > *'));
            const hero = document.querySelector('.promo-hero').getBoundingClientRect();
            return bs.map(el => {
              const b = el.getBoundingClientRect();
              return {text: (el.textContent||'').trim().replace(/\\s+/g,' '),
                      href: el.getAttribute('href'), w: +b.width.toFixed(1), h: +b.height.toFixed(1),
                      top: +b.top.toFixed(1), left: +b.left.toFixed(1),
                      overflowX: b.right > hero.right + 0.5 || b.left < hero.left - 0.5,
                      scrollOverflow: el.scrollWidth > el.clientWidth + 1,
                      lines: getComputedStyle(el).whiteSpace};
            });
          })()""")

        r['links'] = await page.evaluate("""
          (() => {
            const card = Array.from(document.querySelectorAll('#tab-promo .promo-card'))
              .find(c => (c.textContent||'').includes('쾌적하마'));
            const as = Array.from(card.querySelectorAll('a,button')).map(el => ({
              tag: el.tagName, text: (el.textContent||'').trim().replace(/\\s+/g,' '),
              href: el.getAttribute('href'), w: +el.getBoundingClientRect().width.toFixed(1),
              h: +el.getBoundingClientRect().height.toFixed(1),
              inside: (() => {const br = card.getBoundingClientRect(), b = el.getBoundingClientRect();
                              return b.left >= br.left - 0.5 && b.right <= br.right + 0.5;})()
            }));
            return {cardW: +card.getBoundingClientRect().width.toFixed(1),
                    cardH: +card.getBoundingClientRect().height.toFixed(1), items: as};
          })()""")

        r['has_homepage'] = await page.evaluate("!!document.querySelector('#tab-promo a[href=\"https://www.nicehama.co.kr\"]')")
        r['has_blog'] = await page.evaluate("!!document.querySelector('#tab-promo a[href=\"https://blog.naver.com/nice_hama\"]')")
        r['has_tel'] = await page.evaluate("!!document.querySelector('#tab-promo a[href=\"tel:02-6346-0075\"]')")
        r['has_academy'] = await page.evaluate("!!document.querySelector('#tab-promo a[href=\"https://cjyacademy.com\"]')")
        r['forbidden'] = await page.evaluate("(document.body.innerText.includes('잡고릴라'))")

        # 서비스 안내 패널
        r['svc'] = await page.evaluate("""
          (() => {
            const p = Array.from(document.querySelectorAll('#tab-promo .panel'))
              .find(x => (x.textContent||'').includes('서비스 대상'));
            const pr = p.getBoundingClientRect();
            let over = 0;
            p.querySelectorAll('.svc-chips span, .svc-list li').forEach(el => {
              const b = el.getBoundingClientRect();
              if (b.right > pr.right - 10 || b.left < pr.left + 5) over++;
            });
            return {h: +pr.height.toFixed(1), overflowCount: over,
                    text: (p.textContent||'').replace(/\\s+/g,' ').trim().slice(0, 400)};
          })()""")

        # 문의 모달 (서비스)
        await page.evaluate("""Array.from(document.querySelectorAll('[data-inquiry="service"]'))
              .find(b => b.closest('#tab-promo'))""")
        await page.click('#tab-promo .link-btn.go')
        await page.wait_for_timeout(400)
        r['modal'] = await page.evaluate("""
          (() => {
            const m = document.getElementById('modal');
            const links = document.getElementById('modalLinks');
            return {title: document.getElementById('modalTitle').textContent,
                    text: document.getElementById('modalText').textContent,
                    shown: m.classList.contains('on'),
                    linksVisible: getComputedStyle(links).display !== 'none',
                    links: Array.from(links.querySelectorAll('a')).map(a => ({t: a.textContent.trim(), h: a.getAttribute('href')})),
                    boxFits: (() => {const b = m.querySelector('.modal-box').getBoundingClientRect();
                                     return b.top >= 0 && b.bottom <= window.innerHeight;})()};
          })()""")
        for i, sel in enumerate(['.promo-hero', '.promo-card.deploy-card']):
            pass

        # 탭바·스크롤 확인
        r['layout'] = await page.evaluate("""
          (() => {
            const main = document.querySelector('main');
            const promo = document.getElementById('tab-promo');
            const cs = getComputedStyle(promo);
            return {display: cs.display, mainScrollH: main ? main.scrollHeight : null,
                    mainClientH: main ? main.clientHeight : null,
                    promoH: +promo.getBoundingClientRect().height.toFixed(1),
                    docOverflowX: document.documentElement.scrollWidth > window.innerWidth + 0.5};
          })()""")

        # 모달 닫고 스크린샷 (스크롤 위쪽 / 카드 / 서비스 패널)
        await page.click('#modalOk')
        await page.wait_for_timeout(300)
        os.makedirs(OUT, exist_ok=True)
        await page.evaluate("document.querySelector('main').scrollTop = 0")
        await page.wait_for_timeout(200)
        await page.screenshot(path=os.path.join(OUT, 'local_top.png'))
        card = page.locator('#tab-promo .promo-card', has_text='쾌적하마').first
        await card.screenshot(path=os.path.join(OUT, 'local_card.png'))
        svc = page.locator('#tab-promo .panel', has_text='서비스 대상').first
        await svc.screenshot(path=os.path.join(OUT, 'local_svc.png'))

        # 모달 스크린샷 (다시 열어서)
        await page.click('#tab-promo .link-btn.go')
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(OUT, 'local_modal.png'))

        # 콘솔 오류
        r['errors'] = errs
        await b.close()
    print(json.dumps(r, ensure_ascii=False, indent=2))


asyncio.run(main())
