# 에러코드.zip — 에어컨 LED·에러코드 현장 앱

## 배포 URL
- **https://nicehama.github.io/aircode/** (GitHub Pages — 배지·광고 없음, 로그인·비밀번호 없음)
- 저장소: **https://github.com/nicehama/aircode** (Public, `main` = 소스 / `gh-pages` = 배포본)
- 배포 파일: `index.html` (저장소 루트 = `dist/index.html` = `downloads/에어컨_에러코드_앱_프로토타입.html`)
- 최신 배포: **v12 (GitHub Pages)** — 2026-11-21 22:19 KST, **543,036 bytes** (sha256 `8e7a4988…f6154`). 앱 표시 이름을 **에러코드.zip**으로 변경. 주소·저장소·`qr_site.svg` QR 값·`localStorage` 키(`aircode_fav_v1`·`aircode_recent_v1`)는 그대로.
  - v11 22:06 (543,116 bytes, sha256 `a2047138…c9c91`) → **v12: `<title>`·apple/application-name·PWA 매니페스트(name/short_name)·상단 헤더·공유 제목·QR aria-label을 `에러코드.zip`으로** (헤더의 `AirCode` 영문 표기 제거)
  - v12 라이브 검증(390×844): `https://nicehama.github.io/aircode/` HTTP 200 + 내려받은 본문 **바이트 동일**, 타이틀 `에러코드.zip — 에어컨 LED·에러코드`, 헤더 `에러코드.zip`, 매니페스트 name/short_name `에러코드.zip`, QR OpenCV 디코드 `https://nicehama.github.io/aircode/`, LED `test_led_ch21.mp4` → `CH21`, 하단 탭바 4개 완전 노출, **콘솔·페이지 오류 0건**. 캡처 `downloads/gh_pages_errorcodezip.png`·`gh_pages_errorcodezip_header.png`.
  - v10 22:00 → **v11 22:05: 아카데미 탭에 쾌적하마 홍보(서비스 대상·기종·절차·강점)·홈페이지/네이버 블로그/대표번호 링크·문의 모달 링크 보강**
  - v1 11-17 20:35 (체크리스트 탭) → v2 20:58 (현장 진단 개편) → v3 21:00 (코드바·진행바) → v4 21:10 (반응 띠)
  - **v5~v10 11-21: 에어코드 이름·QR 배포 모달·즐겨찾기·tel 링크·실제 LED 영상 판독 엔진** (v6 tel 정규식, v7 PWA 매니페스트, v8 모드 칩 폭, v9 미매칭 코드 전화 링크, v10 전화 링크 스타일)
- 이전 deed.page 주소(`https://aircon-code-demo-1120.deed.page/`)는 옛 빌드로 남아 있다(QR이 deed.page를 가리키고 "Published with deed.page" 배지가 붙음). **새로 배포·공유할 주소는 GitHub Pages만 쓴다.**
- GitHub Pages 소스는 `gh-pages` 브랜치다(빈 저장소에 `gh-pages`를 처음 푸시했을 때 자동 활성화됨, `build_type: legacy`, 경로 `/`). Pages 설정 API는 GitHub App 권한(`Pages`)이 없어 403이므로, 배포는 `gh-pages` 푸시로 한다.

## v5에서 바뀐 것 — 앱 이름과 배포
- 이름 표기 위치: `<title>`, 헤더 타이틀, `apple-mobile-web-app-title`, `application-name`, PWA 매니페스트(name/short_name), 아이콘. (v5~v11 `에어코드 (AirCode)` → **v12 `에러코드.zip`**)
- 아이콘은 `assets/icon.svg`(파비콘·매니페스트)와 `assets/icon-180.png`·`icon-512.png`(apple-touch-icon)를 **base64로 HTML 안에 인라인**했다. 외부 CDN·별도 파일 없이 동작한다.
- **교육생 배포 QR 모달**: 헤더 오른쪽 QR 버튼, 아카데미 탭 '교육생에게 앱 배포' 카드에서 연다. QR은 `assets/qr_site.svg`(빌드 시 생성한 SVG path)로 HTML에 내장돼 **인터넷 없이도 화면에 뜨고**, [링크 복사]·[공유하기](`navigator.share` 있으면 공유 시트)가 붙는다.
  - QR이 실제로 읽히는지 배포 화면을 캡처해 OpenCV `QRCodeDetector`로 디코드해 확인했다 → `https://aircon-code-demo-1120.deed.page/`.
- 검색 탭: 카드마다 **★ 즐겨찾기** 토글 + `전체 코드 / ★ 즐겨찾기 / 최근 본` 필터. `localStorage: aircode_fav_v1 · aircode_recent_v1`(최근 20건)에 남아 새로고침·앱 전환 후에도 유지된다.
- 제조사 고객센터 8곳 중 번호가 있는 7곳과 현장 진단 판정 화면의 고객센터가 **`tel:` 원터치 전화** 링크가 됐다(파세코·신우공조·에이피의 지역번호, 삼성·LG·캐리어·위니아의 1588·1544 번호 모두).

## 핵심: 실제 작동하는 LED 영상 판독 엔진 (서버·API 키 없음)
`app_template.html`의 `ai` 객체 + `AI_MODES`가 전부다. 업로드한 영상은 브라우저 메모리에서만 읽고 어디로도 보내지 않는다.

- **입력**: ① 영상 바로 찍기(`<input type="file" accept="video/*" capture="environment">`) ② 영상·사진 불러오기(`video/*,image/*`) ③ 샘플로 체험. 모드 칩은 `LG 실외기(적/녹) · LG 실내기(단색) · 캐리어(운전램프) · 삼성 4WAY(사진·램프)`.
- **샘플링**: `<video>`를 160×120 캔버스에 그려 13fps로 최대 12초(최소 3초) 프레임을 읽는다. 재생이 멈추면(헤드리스·코덱 문제) `seeked` 이벤트 기반 시킹으로 자동 전환한다. 4×4px 셀(40×30 격자) 평균 R/G/B만 남겨 메모리를 2MB 안쪽으로 유지한다.
- **ROI(보는 지점)**: 미리보기 위를 한 번 누르면 그 지점을, 누르지 않으면 중앙 가이드 안에서 **시간에 따른 적색·녹색·밝기 변화가 가장 큰 셀 군집**을 자동으로 찾는다(3×3 평균으로 군집화). 분석 후 다른 곳을 눌러도 재촬영 없이 캐시된 프레임으로 즉시 다시 센다.
- **신호**: 셀별 `적색 우세 = R − max(G,B)×0.6`, `녹색 우세 = G − max(R,B)×0.6`, `휘도 = 0.299R+0.587G+0.114B`를 ROI 가중 평균으로 시계열화.
- **검출**: 3프레임 평균 → 10/90 백분위 기반 **적응형 임계값(히스테리시스 30%/60%)** → 짧은 소등 병합(60ms)·1프레임 미만 제거. 점멸마다 적/녹/무채색을 판정하고, 점멸 사이 **휴지 구간**으로 코드 묶음을 나눈다(적2·녹1이 두 번 반복되면 한 묶음만 센다 — 첫 묶음이 잘려도 가장 많이 반복된 패턴을 고른다).
- **품질 게이트**: ROI 신호의 절대 변화폭이 12레벨 미만이거나 점멸이 26회를 넘으면 **엉뚱한 코드를 만들지 않고 '검출 실패'** 로 돌려보낸다(어두운 곳을 눌렀을 때 CH09 같은 오판 방지).
- **코드 매칭**
  - `LG 실외기`: 적색 횟수×10 + 녹색 횟수 → `CH21`, `DATA.led.lgPcb`·`DATA.entries` 대조
  - `LG 실내기`: 0.8초 이상 긴 소등으로 자릿수 분리 → `CH{1}{2}`(한 자리면 `CH0{n}`)
  - `캐리어`: 연속 점멸 횟수 → `DATA.led.carrierLamp`(운전램프 5회 등)
  - `삼성 4WAY`·정지 사진: 켜진 램프의 위치·색을 클러스터로 찾아 보여 주고, **[4WAY 조합기에서 확정 →]** 으로 램프 개수(4/5)에 맞는 조합기를 바로 연다.
- **결과 카드**: 실측 파형(캔버스, 적/녹/밝기 + 점멸 구간 음영), `적색 2회 · 녹색 1회` 같은 실측값, **±1 보정 버튼**(적/녹·자릿수·횟수 — 빛번짐 1회 오차를 재촬영 없이 수정), 매칭 코드·원인·점검·리셋, [상세 점검 보기]·[현장 진단 시작 →], 그리고 "영상은 기기 내에서만 실시간 분석되며 외부로 전송되지 않습니다." 문구.

## v11에서 바뀐 것 — 아카데미 탭 쾌적하마 홍보
- 히어로 버튼을 2×2로: `아카데미 홈페이지`(cjyacademy.com, 청록) · `쾌적하마 홈페이지`(nicehama.co.kr, 주황) · `교육 문의` · `출장·견적 문의`. 390px에서 159px씩 두 줄, 320px 이하에서는 한 줄씩으로 자연스럽게 접힌다(`flex:1 1 calc(50% - 4px); min-width:132px`).
- 쾌적하마 카드: 대상·기종·장비·약품 요약 + 태그 6개 + 링크 3개 — `nicehama.co.kr`(홈페이지) · `네이버 블로그`(blog.naver.com/nice_hama) · `02-6346-0075`(`tel:` 원터치) + `출장·견적 문의` 버튼.
- 새 패널 **쾌적하마 서비스 안내**: 서비스 대상(가정·주택/매장·상가/기업·오피스/학교/병원·의료/관공서), 취급 기종(벽걸이·스탠드·천장형 1/2/4WAY·원형·매립덕트), 진행 절차 5단계, 강점 4개(완전 분해·40℃/120bar 고온고압·친환경 전용 약품·S2B 학교장터 등록/나라장터 입찰 요건).
- `data-inquiry="service"` 모달에 `nicehama.co.kr` · `네이버 블로그` · `02-6346-0075` 링크(`#modalLinks`, 서비스 모달에서만 노출).
- 공개 홍보 정보만 수록: 옛 법인명(`(주)잡고릴라`)·주소·사업자번호·대표자명은 넣지 않았다(본문 문자열 0건 검증).

## GitHub Pages 라이브 검증 (2026-11-21 21:58, `verify_pages.py`)
- `https://nicehama.github.io/aircode/` → **HTTP 200**, 내려받은 HTML이 로컬 `dist/index.html`과 **바이트 동일**(sha256 `29f4738…0334`, 536,331 bytes).
- 메인: `deed.page`·`Published with`·`Report abuse` 문자열 **0건**, 외부 링크는 `cjyacademy.com` 2개 + `nicehama.co.kr`(히어로·카드·모달) · `blog.naver.com/nice_hama`(카드·모달) · `tel:02-6346-0075`(카드·모달) 등 쾌적하마 공식 채널뿐. 하단 탭바 4개(검색·LED 찾기·현장 진단·아카데미) 모두 뷰포트 안(`783~838px`, 844px 화면), 다른 요소에 가려짐 없음(`elementFromPoint` 일치).
- QR 모달: 표기 `https://nicehama.github.io/aircode/`, QR 이미지를 OpenCV `QRCodeDetector`로 디코드한 값 **동일**.
- LED 찾기: `test_led_ch21.mp4` 업로드 → **`CH21` / 적색 2회 · 녹색 1회 / 122프레임 / 자동 ROI**, 점멸 6개.
- **콘솔·페이지 오류 0건.** 스크린샷: `downloads/gh_pages_main.png` · `gh_pages_qr.png` · `gh_pages_led_ch21.png`

## v11 라이브 검증 — 아카데미 탭 쾌적하마 홍보 (`verify_promo_live.py`)
- `https://nicehama.github.io/aircode/` → **HTTP 200**, 내려받은 HTML이 `index.html`과 **바이트 동일**(sha256 `a2047138…c9c91`, 543,116 bytes). 푸시 후 약 20초(폴링 5회)에 새 본문 반영.
- 히어로 버튼 4개 모두 159×42px·두 줄 배치, 가로 넘침 0(`scrollWidth > clientWidth` 검사). 링크: `cjyacademy.com`·`https://www.nicehama.co.kr`.
- 쾌적하마 카드(362×381px): `nicehama.co.kr`·`네이버 블로그`·`tel:02-6346-0075`·`출장·견적 문의` 4개 모두 카드 안에 들어옴(오버플로 0).
- 문의 모달: 제목 `출장·견적 문의`, 링크 3개(`nicehama.co.kr`·`네이버 블로그`·`02-6346-0075`) 노출.
- 금지어 `잡고릴라` 본문 **0건**. 문서 가로 스크롤 없음, 탭바 4개 모두 뷰포트 안.
- 회귀: 검색 `CH21` → `‘CH21’ 검색` 1건, QR URL·OpenCV 디코드 `https://nicehama.github.io/aircode/` 일치, LED `test_led_ch21.mp4` → **`CH21`**(123프레임·점멸 6개), **콘솔·페이지 오류 0건**.
- 스크린샷: `downloads/gh_pages_academy_promo.png`(390×1600 한눈에) · `gh_pages_academy_promo_top.png`(390×844 상단) · `gh_pages_academy_promo_card.png` · `gh_pages_academy_inquiry_modal.png` · `gh_pages_search_regress.png`

## 검증 기록 (이전 deed.page 배포, Playwright 390×844, `LD_LIBRARY_PATH=/workspace/tmp/libs/root/usr/lib/x86_64-linux-gnu`)
- **실제 영상 E2E**(WebM·H.264 mp4 둘 다 확인): `make_test_video.py`로 적색 2회 → 녹색 1회 패턴이 두 번 반복되는 9.5초 640×480 30fps 영상(`downloads/test_led_ch21.mp4`, H.264 30KB)을 만들고, 배포 URL에서 `#fileIn`에 실제 업로드 → **`CH21` / 적색 2회 · 녹색 1회 / 123프레임 / 자동 ROI** 판독. 파형에 점멸 6개(2묶음)가 그려지고 ± 보정으로 CH22↔CH21 전환 확인.
- 샘플 3종: LG 실내기 `CH21`(1번째 2회·2번째 1회), 캐리어 `운전램프 5회 연속 점멸`(냉매 점검 필요), 삼성 4WAY `램프 2개 감지`.
- ROI를 LED가 없는 구석으로 옮기면 `LED 점멸을 찾지 못했습니다`로 바뀌고, LED 자리로 되돌리면 `CH21` 복귀.
- 사진 업로드: `불빛 2곳` 감지 + "사진 한 장으로는 점멸 횟수를 셀 수 없습니다" 안내, [영상으로 찍기] 버튼.
- QR: 모달 열림, 링크 복사 → 클립보드에 `https://aircon-code-demo-1120.deed.page/`, 캡처 PNG를 OpenCV로 디코드해 같은 URL 확인.
- 검색 Enter(`C101` 1건·포커스 해제)·`배수` 15건, 즐겨찾기 1건(새로고침 후 유지), 최근 본 2건, LG 카운터 적2+녹1=`CH21`.
- 현장 진단: 계열 8·상황 7, 1→2→3단계, 해결 카드(3줄), 팬 4단계 전부 그대로 → 판정 카드 + 고객센터 tel 1건(`1544-7777`).
- 아카데미: 고객센터 8행·tel 7개, 수록 통계 378건.
- **콘솔/페이지 오류 0건**. 375×667에서도 결과·버튼 정상. 오버플로 검사에 잡히는 `promo-hero`·`ai-card`는 장식용 글로우 원이 `overflow:hidden`으로 잘린 것으로 실제 가로 스크롤은 없다.
- 기존 회귀: `verify_live.py`(배포 URL)와 `test_dx.py`(로컬) 모두 오류 0으로 통과.

## 스크린샷 (`downloads/`)
| 파일 | 내용 |
|---|---|
| `app_v5_01_main.png` | 배포 URL 메인 — 에어코드 헤더·QR 버튼·378건·즐겨찾기/최근 필터 |
| `app_v5_02_video_ch21.png` | 실제 영상 업로드 판독 결과 `CH21` + 파형·±보정 |
| `app_v5_03_result_card.png` | 결과 카드 확대 |
| `app_v5_04_sheet.png` | 결과에서 연 상세 점검 시트 |
| `app_v5_05_qr_modal.png` / `app_v5_06_qr_only.png` | 교육생 배포 QR 모달 / QR만 캡처(디코드 검증용) |
| `app_v5_07_star_sheet.png` / `app_v5_08_recent.png` | 즐겨찾기·최근 본 |
| `app_v5_09_dx_escalate.png` / `app_v5_09b_dx_tel.png` | 현장 진단 판정·고객센터 전화 |
| `app_v5_10_academy.png` | 아카데미 탭(배포 카드·고객센터 tel) |
| `app_v5_frame_video.png` / `app_v5_frame_roi.png` | 업로드 영상 미리보기 / LED 위치(ROI) 지정 |
| `app_v5_11_375_main.png` / `app_v5_12_375_result.png` | 375×667 소형 화면 |
| `app_v5_13_led_top.png` | LED 탭 상단(모드 칩·가이드 프레임·촬영 버튼) |
| `app_v5_14_unmatched.png` | 표에 없는 조합 → 고객센터 전화 링크 |
| `app_v5_15_live_mp4.png` | 라이브에서 H.264 mp4 업로드 판독 |
| `test_led_ch21.mp4` / `test_led_frame_*.png` | E2E용 실제 점멸 영상(H.264 30KB)·프레임 |
| `gh_pages_main.png` | GitHub Pages 라이브 메인 — 배지 없음·하단 탭바 4개 완전 노출 |
| `gh_pages_qr.png` | GitHub Pages QR 모달 — `https://nicehama.github.io/aircode/` 표기 |
| `gh_pages_led_ch21.png` | GitHub Pages 라이브에서 실제 영상 업로드 → `CH21` 판독 |

## 파일 구성
```
app_template.html      앱 원본 (여기만 고치면 된다)
build_app.py           템플릿 + JSON + 아이콘 + QR + 매니페스트 → 단일 HTML
make_assets.py         아이콘 SVG/PNG, 배포 QR SVG 생성 (assets/)
make_test_video.py     E2E용 CH21 점멸 영상 생성
verify_v5_live.py      배포 URL 전 기능 + 실제 영상 업로드 E2E
verify_pages.py        GitHub Pages 라이브 검증(배지·탭바·QR·CH21·오류)
test_v5_local.py       로컬 파일 기준 기능 전수 점검
test_v5_small.py       375×667 + 매니페스트 확인
test_upload.py         파일 하나만 지정해 판독 결과 확인 (python3 test_upload.py 경로)
verify_live.py         기존(현장 진단·검색) 회귀
test_dx.py             기존 현장 진단 로컬 회귀
smoke_v5.py            빠른 로드 점검
```

## 빌드 · 배포 방법 (같은 URL 유지)
```sh
cd /workspace/app-aircon-prototype
python3 make_assets.py      # 아이콘·QR 다시 만들 때만
python3 build_app.py        # app_template.html → downloads/…html (자원 인라인)
cp ../downloads/에어컨_에러코드_앱_프로토타입.html dist/index.html
# 저장소 사본(/workspace/aircode-repo)에 반영
cp dist/index.html /workspace/aircode-repo/index.html
cd /workspace/aircode-repo && git add -A && git commit -m "deploy: v11" \
  && git push origin main && git push origin main:gh-pages
```
`gh-pages`에 푸시하면 GitHub Pages가 1분 안에 같은 주소에 반영한다. (Pages 설정 API는 GitHub App 권한 문제로 403 — 저장소 화면에서 바꾸지 않는다.)

이전 deed.page 배포용 토큰: `app-aircon-prototype/.deed-token` (chmod 600, 저장소에는 올리지 않음).

## 로컬 검수 방법
이 환경의 Playwright Chromium은 시스템 라이브러리가 빠져 있어 `LD_LIBRARY_PATH`가 필요하다.
```sh
LD_LIBRARY_PATH=/workspace/tmp/libs/root/usr/lib/x86_64-linux-gnu python3 verify_v5_live.py   # 배포 URL
LD_LIBRARY_PATH=/workspace/tmp/libs/root/usr/lib/x86_64-linux-gnu python3 test_v5_local.py    # 로컬 dist
```

## 3번째 탭: 현장 진단 (단계별 고장 추적, v2 개편 유지)
- 진입 4가지: 고장 계열 8장 / 자주 나오는 상황 7종 / 코드 직접 입력 / 검색 시트·LED 결과의 [현장 진단]
- 진행 화면: 코드 배너 → 진행 바 + [처음부터 다시] → 시도 타임라인 → 현재 단계 카드(조치 / 정상 기준 / 주의)
- `✅ 에러 없어짐` → 해결 카드 + 조치 내역 복사, `❌ 그대로 뜸` → 다음 예상 원인으로 전개, 4단계 모두 그대로면 부품·기판 교체/제조사 접수 판정 + 제조사 고객센터(전화 걸기)
- 진행 상태는 `localStorage: aircon_dx_v2`, 현장 메모는 `aircon_memo_v1`에 저장. 진단 단계 문구는 `DX_FAMILIES` 배열에서 고친다.

## 개인정보 점검
- 휴대폰 번호(010), 이메일 주소, 주소, 계좌번호, 사업자번호: 없음
- 페이지에 나온 전화번호 031-492-8341 / 031-953-8725 / 031-942-2237 / 1588·1544 번호는 모두 **제조사 고객센터** 번호다.
- 사업명(최정예홈케어아카데미·쾌적하마)과 cjyacademy.com 링크는 이미 공개된 브랜드 정보. 앱에 입력한 영상·사진은 서버로 전송되지 않고 브라우저 안에서만 처리된다.
