# Skills Database Assessment — 2026-06-05

## 1. Inventory Overview

| Category | Count | Location |
|---|---|---|
| AV_Safety project skills | 18 | `skills/` |
| Graphify (sub-module) | 1 | `.openclaw/skills/graphify/` |
| **Total** | **19** | — |

### SKILL.md Statistics

| Metric | Value |
|---|---|
| Total SKILL.md lines (project) | 2,057 |
| SKILL.md files | 19 |
| Total bytes (all SKILL.md) | ~79 KB |
| Average lines per SKILL.md | ~108 |
| Longest SKILL.md | `3d-animation` (148 lines) |
| Shortest SKILL.md | `project-setup` (62 lines) |
| Skills with `references/` | 17 / 18 |
| Skills with `scripts/` | 0 / 18 |
| Skills with `assets/` | 0 / 18 |

---

## 2. Full Skill Listing

| # | Skill | Lines | Descrip. Len. | Has refs? | Has scripts? | Status |
|---|---|---|---|---|---|---|
| 1 | **3d-animation** | 148 | 157 | Yes (2 files) | No | ✅ Built |
| 2 | **bayesian-analysis** | 59 | 175 | Yes (1 file) | No | ✅ Built |
| 3 | **bayesian-evt** | 128 | 197 | Yes (1 file) | No | ✅ Built |
| 4 | **collision-modeling** | 108 | 137 | Yes (1 file) | No | ✅ Built |
| 5 | **data-exploration** | 112 | 135 | Yes (1 file) | No | ✅ Built |
| 6 | **data-ingest** | 139 | 130 | Yes (1 file) | No | ✅ Built |
| 7 | **graphify** | 2,057 | 355 | No | No | ✅ Sub-module |
| 8 | **graphify-out** | 0 (dir) | — | No | No | 🔶 Stub |
| 9 | **indicator-computation** | 115 | 109 | Yes (1 file) | No | ✅ Built |
| 10 | **kinematics-engine** | 115 | 140 | Yes (1 file) | No | ✅ Built |
| 11 | **portfolio-deploy** | 63 | 130 | No | No | 🔲 Spec only |
| 12 | **portfolio-ui** | 135 | 156 | Yes (1 file) | No | 🔲 Spec only |
| 13 | **project-setup** | 62 | 148 | No | No | ✅ Built |
| 14 | **risk-metrics** | 121 | 117 | No | No | ✅ Built |
| 15 | **risk-quantification** | 120 | 141 | Yes (1 file) | No | 🔲 Spec only |
| 16 | **safety-thresholds** | 131 | 143 | Yes (1 file) | No | 🔲 Spec only |
| 17 | **scenario-taxonomy** | 106 | 115 | Yes (1 file) | No | ✅ Built |
| 18 | **standards-research** | 114 | 107 | No | No | ✅ Built |
| 19 | **statistical-validation** | 138 | 125 | Yes (1 file) | No | ✅ Built |
| 20 | **stochastic-simulation** | 148 | 144 | Yes (1 file) | No | ✅ Built |

---

## 3. Build Order (from project SKILL.md)

```
phase1 (Foundation) → phase2 (Analysis) → phase3 (Modeling) → phase4 (Portfolio)
```

| Phase | Skills | Count |
|---|---|---|
| **Foundation** | project-setup, standards-research, risk-metrics, bayesian-analysis, scenario-taxonomy, data-ingest, kinematics-engine | 7 |
| **Analysis** | indicator-computation, stochastic-simulation, data-exploration, bayesian-evt, 3d-animation, statistical-validation, collision-modeling | 7 |
| **Modeling** | safety-thresholds, risk-quantification | 2 |
| **Portfolio** | portfolio-ui, portfolio-deploy | 2 |

**Note:** The project SKILL.md lists a 5th-phase skill called **validation** (depends on collision-modeling + risk-quantification) that **does not exist** in the directory at all.

---

## 4. Dependency Graph (Cross-Skill References)

### Directed Edges

| From | Depends On |
|---|---|
| **indicator-computation** | kinematics-engine |
| **stochastic-simulation** | kinematics-engine |
| **bayesian-evt** | indicator-computation, stochastic-simulation |
| **3d-animation** | kinematics-engine, stochastic-simulation |
| **data-exploration** | data-ingest |
| **statistical-validation** | bayesian-evt, risk-metrics, collision-modeling |
| **collision-modeling** | bayesian-evt |
| **safety-thresholds** | risk-metrics, collision-modeling |
| **risk-quantification** | safety-thresholds, collision-modeling, stochastic-simulation, data-ingest, bayesian-evt, kinematics-engine |
| **portfolio-ui** | bayesian-evt, 3d-animation |
| **portfolio-deploy** | portfolio-ui |

### Diamond Dependency Alerts

| Diamond Path | Risk |
|---|---|
| `risk-quantification` → `bayesian-evt` → `stochastic-simulation` | **LOW** — well-contained |
| `risk-quantification` → `data-ingest` → `statistical-validation` | **LOW** — data flow, stable |
| `risk-quantification` → `collision-modeling` → `bayesian-evt` | **MEDIUM** — cascading: if bayesian-evt changes, 4 downstream skills need updates |
| `risk-quantification` → `safety-thresholds` → `risk-metrics` | **MEDIUM** — risk-metrics is referenced by 5+ skills |
| `portfolio-ui` → `bayesian-evt` AND `portfolio-ui` → `3d-animation` | **LOW** — pair dependency, manageable |

### Orphaned / Missing References

- **validation** — listed in project SKILL.md build order, does not exist as a skill directory
- **graphify-out** — empty directory, no SKILL.md, appears to be an output artifact directory (not a skill)

---

## 5. Quality Assessment

### Frontmatter Quality

| Criteria | Score | Notes |
|---|---|---|
| Name format (hyphen-case, <64 chars) | 18/18 ✅ | All valid |
| Description specificity (107–197 chars) | 17/18 ✅ | All well-crafted; graphify (355 chars) is unusually long |
| Required fields present | 19/19 ✅ | Every SKILL.md has `name` + `description` |
| No extraneous fields | 19/19 ✅ | Clean frontmatter |

### Structural Quality (per skill-creator spec)

| Criteria | Score | Notes |
|---|---|---|
| Body <500 lines (progressive disclosure) | 19/19 ✅ | All within limit; graphify (2,057 lines) is a known outlier |
| References directory present | 17/18 ✅ | 2 project skills lack refs (project-setup, risk-metrics — acceptable for simple skills) |
| Scripts directory (recommendation) | 0/18 ❌ | **No skill has executable scripts.** Per skill-creator spec, `scripts/` are recommended for deterministic operations. |
| Assets directory (recommendation) | 0/18 ❌ | **No skill has assets.** templates, icons, or boilerplate code are absent. |
| agents/openai.yaml (metadata) | 0/18 ❌ | No skills have UI-facing metadata (display_name, short_description, default_prompt). |
| Cross-skill dependency docs | 14/18 ⚠️ | 4 skills (data-ingest, collision-modeling, safety-thresholds, stochastic-simulation) mention sibling skills in body but not in formal build order. |

---

## 6. Issues Summary

| # | Issue | Severity | Count | Details |
|---|---|---|---|---|
| 1 | **Spec-only skills** — SKILL.md exists but no implementation code backing it | **Medium** | 4 | portfolio-deploy, portfolio-ui, risk-quantification, safety-thresholds |
| 2 | **Missing "validation" skill** — referenced in project SKILL.md build order but doesn't exist | **Medium** | 1 | Depends on collision-modeling + risk-quantification |
| 3 | **No scripts/ directories** — zero executable code across 18 skills | **Low-Medium** | 18 | Violates skill-creator best practice for deterministic reliability |
| 4 | **No assets/ directories** — no templates, icons, or boilerplate | **Low** | 18 | Limits reusability |
| 5 | **No agents/openai.yaml** — no UI metadata for Codex CLI discovery | **Low** | 18 | Skilled skills won't surface in UI lists |
| 6 | **graphify-out** — empty directory misclassified as a skill | **Low** | 1 | Renamed to `graphify-out/` or remove |
| 7 | **Graph skill (2,057 lines)** — vastly exceeds 500-line progressive disclosure target | **Low** | 1 | Monolithic; should be split per skill-creator spec |
| 8 | **Diamond dependency on risk-metrics** — 5+ downstream skills depend on it | **Low** | 1 | Not breaking, but hard to track coupling |

---

## 7. Strengths

- **Descriptions are well-crafted** — 107–197 characters, specific enough for reliable triggering without being overly broad
- **Consistent reference pattern** — 17 of 18 skills use `references/implementation-details.md` (or domain-specific names) as the standard reference file
- **Logical build order** — foundation → analysis → modeling → portfolio flows naturally for a safety workflow
- **Cross-skill documentation** — most skills document their siblings and dependencies in-body
- **Naming conventions** — all valid hyphen-case, well under 64 chars
- **Clean frontmatter** — no extraneous fields, properly structured YAML

---

## 8. Recommendations (Prioritized)

### High Priority
1. **Implement the 4 spec-only skills** (portfolio-deploy, portfolio-ui, risk-quantification, safety-thresholds) or mark them as deprecated
2. **Create the missing "validation" skill** listed in the project build order
3. **Remove or rename `graphify-out/`** — it's not a skill, likely an output artifact directory

### Medium Priority
4. **Add `scripts/` directories** to skills that perform deterministic operations (data processing, simulation runs, PDF/image generation, etc.)
5. **Add `agents/openai.yaml`** to all 18 project skills for UI-level Codex CLI integration

### Low Priority
6. **Split the graphify skill** (2,057 lines) into a modular structure per progressive disclosure rules
7. **Document diamond dependencies** explicitly in the project SKILL.md build table

---

*Report generated: 2026-06-05 | Source: `AV_Safety/skills/`, `AV_Safety/.openclaw/skills/`, `AV_Safety/SKILL.md`*
