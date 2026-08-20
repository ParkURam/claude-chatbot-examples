#!/usr/bin/env bash
# Render 의 Build Command 로 이 파일을 지정합니다:  ./build.sh
# package.json 은 web/ 안에 있으므로 npm 은 그 안에서 돌려야 합니다.
set -euo pipefail

pip install -r requirements.txt

cd web
npm ci
npm run build
