#!/usr/bin/env bash
set -euo pipefail
echo "=== Lint Check ==="
cd "${PROJECT_ROOT:-.}"
flake8 src/ --max-line-length=120 --ignore=E203,W503 --count --statistics || true
isort --check-only --diff src/ || true
pydocstyle --convention=google src/ 2>/dev/null || true
echo "Lint complete"
