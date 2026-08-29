#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# DigiKitPro - build the site and export digikitpro-github-ready.zip
# macOS / Linux. Usage:  bash export-github-ready.sh
# ─────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python
echo "Using $($PY --version 2>&1), no external dependencies required."
# (Add: $PY -m pip install -r requirements.txt here if you ever add some.)

echo "Building the site…"
$PY tools/build.py

echo "Copying deploy support files and creating the ZIP…"
$PY tools/export.py

echo ""
echo "✅ Done. Upload digikitpro-github-ready.zip contents to GitHub, or drag the"
echo "   unzipped folder to app.netlify.com/drop. See GO-LIVE.md for click-by-click help."
