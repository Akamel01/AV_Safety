# Portfolio Deployment Guide

## Overview

AV_Safety portfolio deployment using Docker containers with CI/CD pipeline.

## Deployment Targets

- **Portfolio UI**: Static content served via nginx (port 80)
- **Risk API**: Python service via uvicorn (port 8000)
- **Documentation**: Research docs served as static content

## Quick Start

```bash
# Build all services
docker compose build

# Run all services
docker compose up

# Stop
docker compose down
```

## Environments

| Env | Config File | Notes |
|-----|-------------|-------|
| staging | deploy/env/.env.staging | Testing before production |
| production | deploy/env/.env.production | Live deployment |

## CI/CD Pipeline

```
Push -> Lint -> Test -> Build -> Deploy
```

Each step is a shell script in `deploy/ci/`.

## Monitoring

- Error logging: configure in src/risk_quantification/pipeline.py
- Health check: GET /api/health returns status
- Analytics: external (to be configured)

## Backup

- Database: docker exec into container to dump DB
- Static assets: ui/ and docs/ directories version-controlled

## Rollback

```bash
# Rollback to previous Docker image
docker compose pull av-safety:previous-tag
docker compose up -d
```
