# -*- coding: utf-8 -*-
"""템플릿에 JSON 데이터·아이콘·QR 을 인라인해 단일 실행 HTML 로 만든다.
외부 CDN·네트워크 없이 동작하도록 모든 자원을 파일 안에 넣는다."""
import json, os, base64

SITE_URL = 'https://aircode-zip.vercel.app'

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
assets = os.path.join(here, 'assets')

data = open(os.path.join(here, 'aircon_codes.json'), encoding='utf-8').read()
json.loads(data)  # 유효성 검증
tpl = open(os.path.join(here, 'app_template.html'), encoding='utf-8').read()


def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


out_html = tpl.replace('__DATA_JSON__', data)
out_html = out_html.replace('__SITE_URL__', SITE_URL)

icon_svg = os.path.join(assets, 'icon.svg')
if os.path.exists(icon_svg):
    out_html = out_html.replace('__ICON_SVG_B64__', b64(icon_svg))
for key, name in (('__ICON_180__', 'icon-180.png'), ('__ICON_512__', 'icon-512.png')):
    p = os.path.join(assets, name)
    if os.path.exists(p):
        out_html = out_html.replace(key, b64(p))
qr = os.path.join(assets, 'qr_site.svg')
if os.path.exists(qr):
    out_html = out_html.replace('__QR_SVG__', open(qr, encoding='utf-8').read())

# PWA 매니페스트 (앱 이름·아이콘·테마색) — 데이터 URI 라 별도 파일·CDN 없이 동작
import urllib.parse
manifest = {
    'name': '에러코드.zip',
    'short_name': '에러코드.zip',
    'description': '에어컨 LED 점멸을 영상으로 읽어 에러코드와 점검 순서를 알려 주는 현장 도구',
    'lang': 'ko',
    'start_url': SITE_URL,
    'scope': SITE_URL,
    'display': 'standalone',
    'background_color': '#F1F5F6',
    'theme_color': '#0B6E6E',
    'icons': [
        {'src': 'data:image/svg+xml;base64,' + b64(icon_svg), 'sizes': 'any', 'type': 'image/svg+xml', 'purpose': 'any'},
        {'src': 'data:image/png;base64,' + b64(os.path.join(assets, 'icon-180.png')), 'sizes': '180x180', 'type': 'image/png'},
        {'src': 'data:image/png;base64,' + b64(os.path.join(assets, 'icon-512.png')), 'sizes': '512x512', 'type': 'image/png'},
    ],
}
out_html = out_html.replace('__MANIFEST__', 'data:application/manifest+json,' +
                            urllib.parse.quote(json.dumps(manifest, ensure_ascii=False)))

leftover = [k for k in ('__DATA_JSON__', '__SITE_URL__', '__ICON_SVG_B64__',
                        '__ICON_180__', '__ICON_512__', '__QR_SVG__', '__MANIFEST__') if k in out_html]
assert not leftover, leftover

out = os.path.join(root, 'downloads', '에어컨_에러코드_앱_프로토타입.html')
open(out, 'w', encoding='utf-8').write(out_html)
print(out, os.path.getsize(out), 'bytes')
