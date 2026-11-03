#!/usr/bin/env bash
# Build the static pages with Astro and copy them to the repo root (where Vercel serves them).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/export_data.py
(cd astro && npm install --no-audit --no-fund && npx astro build)
rm -rf duo-apps news picks devices calendar week og duo-apps.html news.html picks.html devices.html calendar.html week.html
cp -r astro/dist/duo-apps astro/dist/news astro/dist/picks astro/dist/devices astro/dist/calendar astro/dist/week astro/dist/og .
cp astro/dist/index.html index.html
cp astro/dist/duo-apps.html astro/dist/news.html astro/dist/picks.html astro/dist/devices.html astro/dist/calendar.html astro/dist/week.html astro/dist/sitemap.xml astro/dist/feed.xml astro/dist/robots.txt .
echo "pages: $(ls duo-apps | wc -l) apps, $(ls news | wc -l) stories"
