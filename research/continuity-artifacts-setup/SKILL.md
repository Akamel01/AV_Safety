---
name: continuity-artifacts-setup
description: Create and maintain handoff.md and progress_status.md for project continuity
category: data-science
---

# Continuity Artifacts Setup

## Purpose
Create and maintain mandatory continuity artifacts for long-running engineering sessions. These artifacts ensure:
- New sessions can resume quickly without losing context
- Progress is visible, auditable, and durable
- Decisions and risks are not lost across session boundaries

## Required Files
1. **`handoff.md`** — Continuity and onboarding document for new sessions
2. **`progress_status.md`** — Living operational dashboard

## handoff.md Sections
1. **What is This Project?** — Strategic objectives, success criteria
2. **Current State** — Phase, maturity, blockers, metrics
3. **Workspace Map** — Key folders, key files, read-first order
4. **Architecture / System Overview** — 3-layer structure, 7-step pipeline, dependencies, 13-layer readiness
5. **Decisions Log** — Major decisions with root cause, fix, evidence
6. **Validation / Testing State** — Tests, demo verification, production tests
7. **Open Issues** — Critical/medium/low priority issues
8. **Active Roadmap** — Immediate/short-term/medium-term goals
9. **Read First** — Ordered list of files for new sessions
10. **Session Recovery Procedure** — Step-by-step checklist for restarting

## progress_status.md Sections
1. **Executive Status** — Phase, last work, completion, health
2. **Phase Tracking** — Status, completion %, dependencies, notes per phase
3. **Completed Work** — Chronological list with what/why/root cause/fix/validation
4. **Current Work** — Active work, why it matters, next steps
5. **Upcoming Work** — Prioritized queue
6. **Blockers** — Active and resolved blockers with impact/mitigation
7. **Validation Status** — Unit tests, integration tests, demo verification, production tests
8. **13-Layer Readiness Dashboard** — Status, completion, risk, next actions per layer
9. **Metrics** — Skills, tests, scenarios, data, readiness tracking

## Update Rules
- Update both files after every work session
- Update handoff.md when: decision made, blocker discovered/resolved, milestone reached
- Update progress_status.md when: phase changes, completion %, metrics change, blockers change
- Never let these documents drift out of date

## Verification
After creating/updating:
1. Read both files to verify content
2. Check that timestamps are current
3. Verify that no old/outdated information remains
4. Ensure that new session recovery procedure is clear and actionable
