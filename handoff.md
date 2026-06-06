# 🌐 AV_Safety Project: Technical & Procedural Manifesto

This document serves as the singular, authoritative source of truth for the AV\_Safety project. It defines not only the project's goal but also the rigorous methodology and constraints under which all work must occur.

## 🎯 Project Mandate (The WHY)
**Goal:** To rigorously quantify the collision risk of autonomous vehicle systems and provide an evidence-backed technical comparison against international standards (UL 4600, ISO 21448 SOTIF, ISO 26262, NHTSA guidance).
**Core Question:** *How safe is "safe enough" for autonomous vehicles?*

## ⚙️ Development Methodology & Constraints (The HOW)
All work must adhere to the following operational mandates:

*   **Evidence-First:** Every claim must be traceable to data or a verified source. If data is missing, state it and ask for it.
*   **No Assumptions:** All technical assumptions must be cited.
*   **Concise by Default:** Keep responses brief ($\le$ 20 lines). Detailed technical proofs belong in dedicated files.
*   **Singular Focus:** One goal per turn. Do not juggle unrelated tasks.
*   **File Operational Limits:** Maximum of 2 file operations (Read/Write/Edit) per turn.
*   **Code Review:** Continuous review of code structure and logic before implementation.

## 🏗️ Project Structure & Artifacts (The WHAT)

| Directory/File | Purpose | Content Focus | Status |
| :--- | :--- | :--- | :--- |
| `src/` | **Active Codebase** | The running implementation of the safety lifecycle (Kinematics, Thresholds, etc.). | **In Development** |
| `docs/` | **Research & Plans** | Architecture decisions, simulation reports, and research notes. | **Stable Baseline** |
| `skills/` | **Tool Definitions** | The 18 defined micro-services (e.g., `collision-modeling`, `bayesian-analysis`). | **Mature** |
| `tests/` | **Validation Suite** | Test harnesses and scripts for automated verification. | **Minimal/Evolving** |

### ⚡ Current Phase Focus: Safety Thresholds Implementation
The current engineering effort is concentrated on making `src/safety_thresholds/baseline_estimator.py` the executable Safety Gate. This component validates the physics simulation against the ISO 26262 derived limits.

## 🧭 Next Action: Proving Correctness
The conceptual models are complete. The next step is to prove the current implementation of the `BaselineEstimator` is correct and stable.

**GOAL:** Run the `test_baseline_integration.py` scenario.
**TASK:** Successfully pass a nominal scenario through the `BaselineEstimator` to validate its predictable, compliant output.

---
*(End of Project Charter)*