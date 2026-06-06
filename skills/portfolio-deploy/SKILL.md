---
name: portfolio-deploy
description: "Deploy the AV_Safety portfolio application (UI, risk pipeline results, documentation) to production hosting with CI/CD pipeline."
---

# Portfolio Deployment

Deploy the AV_Safety portfolio application (UI, risk pipeline results, documentation) to production hosting with CI/CD pipeline.

## Deployment Targets

| Target | Platform | Purpose |
|---|-|-|
| Portfolio UI | Static hosting (GitHub Pages, Netlify, Vercel) | Collision risk playground |
| Pipeline API | Server hosting (Render, Railway, AWS) | Risk quantification API |
| Documentation | Static hosting (GitHub Pages) | Research documentation |

## CI/CD Pipeline

```
Push → Lint → Test → Build → Deploy
  ↓       ↓      ↓      ↓       ↓
code   flake8  pytest  portfolio  portfolio
quality  + isort  + mypy  + docs    UI + docs
```

## Deployment Checklist

- [ ] All tests pass (pytest, flake8, mypy)
- [ ] Portfolio UI builds (HTML, CSS, JS)
- [ ] Risk pipeline results generated
- [ ] Documentation generated (mkdocs or similar)
- [ ] Environment variables configured (API keys, thresholds)
- [ ] HTTPS enabled
- [ ] Custom domain configured
- [ ] Monitoring set up (error logging, analytics)
- [ ] Backup strategy defined
- [ ] Rollback procedure documented

## Cross-Skill Dependencies

- **portfolio-ui** (upstream) — portfolio UI built here, deployed by this skill
- **risk-quantification** (upstream) — pipeline results deployed as data artifacts
- **standards-research** (upstream) — compliance documentation deployed
- **portfolio-ui** (sibling) — portfolio UI built here, deployed to production

## File Structure (deployment)
```
deploy/
├── docker-compose.yml    Container orchestration
├── Dockerfile            Production container
├── nginx.conf            Reverse proxy config
├── ci/
│   ├── lint.sh           Lint and code quality
│   ├── test.sh           Run tests
│   ├── build.sh          Build portfolio + docs
│   └── deploy.sh         Deploy to hosting
├── env/
│   ├── .env.production   Production environment
│   └── .env.staging     Staging environment
└── docs/
    └── deployment.md     Deployment guide
```
