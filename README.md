# 에러코드.zip

에어컨 실외기·실내기 LED 점멸을 영상으로 읽어 에러코드와 점검 순서를 알려 주는 현장 도구입니다. 378건의 에러코드 검색, 단계별 현장 진단, 최정예홈케어아카데미 교육 자료를 한 파일에 담았습니다.

- **배포 주소: https://aircode-zip.vercel.app** (Vercel · 푸시하면 자동 재배포)
- GitHub Pages 사본: https://nicehama.github.io/aircode/
- 저장소: https://github.com/nicehama/aircode
- 영상·사진 분석은 브라우저 안에서만 돌고 어디로도 전송되지 않습니다. 회원가입·로그인만 Supabase Auth 를 쓰며, 브라우저에는 **Project URL + Publishable key** 만 들어갑니다(Secret key 는 저장소·앱에 넣지 않습니다).

## 구조

```
index.html                  배포되는 앱 (GitHub Pages 진입점, 빌드 결과물)
.nojekyll                   GitHub Pages 가 Jekyll 처리 없이 정적 파일로 서빙
app-aircon-prototype/       앱 소스
  app_template.html         앱 원본 (수정은 여기서)
  build_app.py              템플릿 + JSON + 아이콘 + QR + 매니페스트 → 단일 HTML
  make_assets.py            아이콘(SVG·PNG)과 배포 QR(SVG) 생성
  aircon_codes.json         에러코드·LED 표·현장 진단 데이터
```

## 수정 후 다시 배포하기

```sh
./deploy.sh
```

`deploy.sh`는 `app_template.html` → 단일 HTML 빌드 → `index.html` 갱신 → `main`과 `gh-pages` 브랜치에 푸시까지 한다. **GitHub Pages 배포 소스는 `gh-pages` 브랜치**(경로 `/`)이고, 푸시하면 1분 안에 같은 주소에 반영된다.

수동으로 할 때:

```sh
cd app-aircon-prototype && mkdir -p ../downloads && python3 build_app.py
cp ../downloads/에어컨_에러코드_앱_프로토타입.html ../index.html
cd .. && git add -A && git commit -m "update app" && git push origin main && git push origin main:gh-pages
```

## 앱 구성

- **검색**: 378건 에러코드, 제조사·증상 필터, ★ 즐겨찾기, 최근 본 코드 — **무료 공개**
- **LED 찾기**: 영상·사진을 올리면 점멸 횟수(적/녹)를 실측해 `CH21` 같은 코드로 매칭 (LG 실외기·LG 실내기·캐리어·삼성 4WAY) — **회원 전용**
- **현장 진단**: 고장 계열 8종 → 단계별 조치 → 해결/부품 교체 판정 + 제조사 고객센터 전화 — **회원 전용**
- **더보기**: 로그인 상태·로그인/로그아웃, 교육 자료, 교육생 배포 QR, 제조사 고객센터 8곳 — **무료 공개**

## v14 회원가입 · 탭 잠금 (2026-11-24)

- 하단 4번째 탭 이름을 `아카데미` → **`더보기`** 로 바꿨습니다(내용은 그대로 + 계정 카드 추가).
- QR·공유 링크를 `https://aircode-zip.vercel.app` 으로 바꿨습니다(QR 이미지는 `make_assets.py` 가 새 주소로 다시 만듭니다).
- 비로그인 상태에서 `LED 찾기` · `현장 진단` 탭을 누르면 로그인/회원가입 게이트가 뜨고, `검색` · `더보기` 는 그대로 열립니다. 상세 시트의 `이 코드로 현장 진단 →` 도 비로그인이면 로그인 화면으로 보냅니다.
- 회원가입: 이름 · 전화번호 · 이메일 · 비밀번호(Supabase Auth) → `public.profiles` 에 자동 저장(트리거 `on_auth_user_created`).
  - 테이블: `id uuid pk → auth.users(id) on delete cascade`, `name`, `phone`, `email`, `created_at`
  - RLS: 본인 행만 select/update/insert (`auth.uid() = id`) — 대시보드 `Table Editor > profiles` 에서 전체 목록·CSV 내려받기는 서비스 관리자 권한으로 됩니다.
- 이메일 인증(Confirm email)은 켜 둔 상태이며, 가입 직후 화면에 인증 안내·재발송 버튼을 보여 줍니다.
- 카카오·구글 로그인 버튼은 화면 구조만 만들어 두고 `준비 중`(비활성)으로 두었습니다.
- **홈 화면 바로가기**: 검색 탭 칩·아카데미 배포 카드·QR 모달 세 곳에서 안내를 열 수 있습니다. 아이폰(사파리)·안드로이드(크롬)·삼성 인터넷별로 카톡에서 연 경우까지 그림과 단계로 설명합니다(접속 기기 자동 선택).
