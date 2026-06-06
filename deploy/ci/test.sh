#!/usr/bin/env bash
set -euo pipefail
echo "=== Test Suite ==="
cd "${PROJECT_ROOT:-.}"
python -m pytest tests/ -v --tb=short --maxfail=5
echo "Tests complete"
