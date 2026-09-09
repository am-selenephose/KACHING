#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

printf '\n== KACHING judge verification ==\n'
python -m unittest discover -s tests -v
python demo_attack_suite.py
python -m compileall -q tradegate tests
npm test --prefix ui
npm run build --prefix ui
npm test --prefix judge
npm run build --prefix judge
python scripts/release_safety_audit.py
git diff --check
printf '\nKACHING_JUDGE_VERIFY=PASS\n'
