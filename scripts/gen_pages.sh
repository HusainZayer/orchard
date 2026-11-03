#!/usr/bin/env bash
# Build the static pages with Astro and copy them to the repo root (where Vercel serves them).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/export_data.py
(cd astro && npm install --no-audit --no-fund && npx astro build)
rm -rf duo-apps news duo-apps.html news.html
cp -r astro/dist/duo-apps astro/dist/news .
cp astro/dist/duo-apps.html astro/dist/news.html astro/dist/sitemap.xml astro/dist/feed.xml astro/dist/robots.txt .
echo "pages: $(ls duo-apps | wc -l) apps, $(ls news | wc -l) stories"
