# -*- coding: utf-8 -*-
"""앱 아이콘(SVG·PNG)과 배포 QR(SVG)를 만들어 assets/ 에 남긴다.
build_app.py 가 이 파일들을 HTML 에 인라인한다(외부 CDN·네트워크 불필요)."""
import os, io, json
import qrcode
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets')
os.makedirs(OUT, exist_ok=True)

SITE_URL = 'https://nicehama.github.io/aircode/'

# ---------------- QR ----------------
qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                   box_size=1, border=0)
qr.add_data(SITE_URL)
qr.make(fit=True)
m = qr.get_matrix()
n = len(m)


def qr_svg(matrix, module=8, quiet=3, dark='#0B2E3A', light='#FFFFFF'):
    n = len(matrix)
    size = (n + quiet * 2) * module
    # 한 줄씩 가로로 이어진 검은 모듈을 path 로 묶어 파일을 작게 만든다
    parts = []
    for y, row in enumerate(matrix):
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                parts.append('M%d %dh%dv1h-%dz' % (x0 + quiet, y + quiet, x - x0, x - x0))
            else:
                x += 1
    d = ''.join(parts)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'shape-rendering="crispEdges" role="img" aria-label="에어코드 설치 QR">'
            '<rect width="%d" height="%d" fill="%s"/>'
            '<path d="%s" fill="%s"/></svg>') % (n + quiet * 2, n + quiet * 2, size, size,
                                                 n + quiet * 2, n + quiet * 2, light, d, dark)


svg = qr_svg(m)
open(os.path.join(OUT, 'qr_site.svg'), 'w', encoding='utf-8').write(svg)
open(os.path.join(OUT, 'qr_site.txt'), 'w', encoding='utf-8').write(json.dumps(
    {'url': SITE_URL, 'modules': n, 'version': qr.version}, ensure_ascii=False))

# ---------------- 아이콘 ----------------
ICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#0E8A80"/><stop offset="1" stop-color="#0B4A5A"/>'
            '</linearGradient></defs>'
            '<rect width="512" height="512" rx="112" fill="url(#g)"/>'
            '<g fill="none" stroke="#EAFBF8" stroke-width="26" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M118 300c0-78 62-140 138-140s138 62 138 140"/>'
            '<path d="M118 300h276"/>'
            '<path d="M180 300v46M240 300v64M300 300v46M360 300v40"/>'
            '<path d="M214 208l42 46 42-46"/>'
            '</g>'
            '<circle cx="256" cy="126" r="26" fill="#38E1C6"/>'
            '</svg>')
open(os.path.join(OUT, 'icon.svg'), 'w', encoding='utf-8').write(ICON_SVG)

# PNG (apple-touch-icon 은 PNG 만 받는다)
for px in (180, 512):
    img = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(px * 0.22)
    # 그라데이션 배경
    for y in range(px):
        t = y / max(1, px - 1)
        c = (int(14 + (11 - 14) * t), int(138 + (74 - 138) * t), int(128 + (90 - 128) * t), 255)
        d.line([(0, y), (px, y)], fill=c)
    # 둥근 모서리 마스크
    mask = Image.new('L', (px, px), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, px - 1, px - 1], radius=r, fill=255)
    base = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    base.paste(img, (0, 0), mask)
    d = ImageDraw.Draw(base)
    lw = max(2, int(px * 0.05))
    # 지붕(아치) + 본체
    d.arc([int(px * .23), int(px * .31), int(px * .77), int(px * .78)], 180, 360,
          fill=(234, 251, 248, 255), width=lw)
    d.line([(int(px * .23), int(px * .585)), (int(px * .77), int(px * .585))],
           fill=(234, 251, 248, 255), width=lw)
    for i, (fx, fh) in enumerate([(.35, .09), (.47, .125), (.59, .09), (.70, .075)]):
        y0 = int(px * .585)
        d.line([(int(px * fx), y0), (int(px * fx), y0 + int(px * fh))],
               fill=(234, 251, 248, 255), width=lw)
    d.line([(int(px * .42), int(px * .40)), (int(px * .50), int(px * .49)), (int(px * .58), int(px * .40))],
           fill=(234, 251, 248, 255), width=lw, joint='curve')
    rr = int(px * .05)
    cxp, cyp = int(px * .5), int(px * .245)
    d.ellipse([cxp - rr, cyp - rr, cxp + rr, cyp + rr], fill=(56, 225, 198, 255))
    base.save(os.path.join(OUT, 'icon-%d.png' % px))

print('assets:', os.listdir(OUT), '| QR version', qr.version, 'modules', n)
