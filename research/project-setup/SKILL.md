---
name: project-setup
description: "Initialize and configure the AV_Safety development environment — install dependencies, create directories, validate setup, and run initial checks."
---

# Project Setup

Initialize and configure the AV_Safety development environment — install dependencies, create directories, validate setup, and run initial checks.

## Setup Steps

1. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Verify Python environment**
   ```bash
   python3 --version  # 3.12+ required
   pip3 --version     # pip 23+ required
   ```

3. **Create required directories**
   ```bash
   mkdir -p data/raw data/processed docs/standards docs/research models checks reports
   ```

4. **Validate Docker**
   ```bash
   docker --version
   docker-compose --version
   docker-compose up -d  # Build dev container
   ```

5. **Verify all skills are present**
   - 18 skills in `skills/` directory
   - Each has SKILL.md and references/

## Cross-Skill Dependencies

- **data-ingest** (downstream) — data directories created here populated later
- **portfolio-deploy** (downstream) — setup is prerequisite for deployment
- **standards-research** (downstream) — docs/standards/ created here populated later

## Validation

After setup, all of these should succeed:
- `pip3 install -r requirements.txt` — no errors
- `python3 -c "import pymc; import numpy; import scipy"` — imports work
- `docker-compose config` — Docker compose valid
- `ls skills/*/SKILL.md | wc -l` → 18

## File Structure (deployment)
```
deploy/
├── setup.sh           One-command setup script
├── requirements/
│   ├── base.txt       Core dependencies
│   ├── dev.txt        Dev/test dependencies
│   └── docs.txt       Documentation dependencies
└── README.md          Setup documentation
```
