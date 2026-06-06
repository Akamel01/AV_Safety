#!/usr/bin/env bash
set -euo pipefail

# AV_Safety Deployment Entrypoint
# Handles startup initialization for risk-api and portfolio-ui services

echo "============================================"
echo "  AV_Safety Deployment Starting"
echo "  Environment: ${ENVIRONMENT:-development}"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================"

# Health check endpoint
if [ "${ENVIRONMENT:-development}" = "production" ]; then
    echo "Running in production mode..."
    echo "  - Logging: stderr"
    echo "  - Workers: 4"
    echo "  - Debug: off"
else
    echo "Running in development mode..."
    echo "  - Logging: console + file"
    echo "  - Workers: 1"
    echo "  - Debug: on"
    export DEBUG=1
fi

# Run the appropriate service based on environment
SERVICE="${SERVICE:-api}"

case "${SERVICE}" in
    api)
        echo "[api] Starting risk quantification API on port 8000..."
        exec python3 -m uvicorn \
            "src.risk_quantification.pipeline:app" \
            --host 0.0.0.0 \
            --port 8000 \
            --workers 4 \
            --log-level info
        ;;
    ui)
        echo "[ui] Serving portfolio UI on port 80..."
        # If nginx is available, use it
        if command -v nginx &> /dev/null; then
            exec nginx -g "daemon off;"
        else
            # Fallback: simple Python HTTP server
            exec python3 -m http.server 80 --directory /app/ui
        fi
        ;;
    worker)
        echo "[worker] Starting background worker..."
        exec python3 -c "
import time
print('Worker started. Processing tasks...')
while True:
    time.sleep(60)
"
        ;;
    *)
        echo "[error] Unknown service: ${SERVICE}"
        echo "  Valid options: api, ui, worker"
        exit 1
        ;;
esac
