#!/bin/bash
# Hourly hook: re-export, validate, push. Company registry enrichment only if older than 24h.
set -e; cd "$(dirname "$0")/.."
git pull -q --rebase || true
python3 scripts/export.py >/dev/null
if [ -z "$(find data/companies.json -mmin -1440 2>/dev/null)" ]; then python3 scripts/companies_enrich.py 2>/dev/null; fi
python3 scripts/app_companies.py >/dev/null
python3 scripts/datapackage.py >/dev/null && python3 scripts/validate.py
git add -A && git -c user.name="Martin Hausleitner" -c user.email="Martin-Hausleitner@users.noreply.github.com" commit -qm "data: refresh $(date -u +%FT%H:%MZ)" && git push -q origin main || echo "nothing to push"
