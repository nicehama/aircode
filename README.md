# 에러코드.zip

에어컨 실외기·실내기 LED 점멸을 영상으로 읽어 에러코드와 점검 순서를 알려 주는 현장 도구입니다. 378건의 에러코드 검색, 단계별 현장 진단, 최정예홈케어아카데미 교육 자료를 한 파일에 담았습니다.

- **배포 주소: https://nicehama.github.io/aircode/**
- 저장소: https://github.com/nicehama/aircode
- 서버·API 키·외부 CDN 없이 동작합니다. 업로드한 영상·사진은 브라우저 안에서만 분석되고 어디로도 전송되지 않습니다.

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

- **검색**: 378건 에러코드, 제조사·증상 필터, ★ 즐겨찾기, 최근 본 코드
- **LED 찾기**: 영상·사진을 올리면 점멸 횟수(적/녹)를 실측해 `CH21` 같은 코드로 매칭 (LG 실외기·LG 실내기·캐리어·삼성 4WAY)
- **현장 진단**: 고장 계열 8종 → 단계별 조치 → 해결/부품 교체 판정 + 제조사 고객센터 전화
- **아카데미**: 교육 자료, 교육생 배포 QR, 제조사 고객센터 8곳
- **홈 화면 바로가기**: 검색 탭 칩·아카데미 배포 카드·QR 모달 세 곳에서 안내를 열 수 있습니다. 아이폰(사파리)·안드로이드(크롬)·삼성 인터넷별로 카톡에서 연 경우까지 그림과 단계로 설명합니다(접속 기기 자동 선택).
