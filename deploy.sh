#!/bin/sh
# 에어코드 빌드 후 GitHub Pages(gh-pages 브랜치)로 배포한다.
set -e
cd "$(dirname "$0")/app-aircon-prototype"
python3 make_assets.py       # 아이콘·QR을 다시 만들 때만 (매번 돌려도 결과 동일)
mkdir -p ../downloads
python3 build_app.py
cp ../downloads/에어컨_에러코드_앱_프로토타입.html ../index.html
cd ..
git add -A
git commit -m "deploy: $(date '+%Y-%m-%d %H:%M')"
git push origin main
git push origin main:gh-pages   # 이 브랜치가 GitHub Pages 배포 소스
echo "배포 완료 — 1분 뒤 https://nicehama.github.io/aircode/ 확인"
