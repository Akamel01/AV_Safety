# AV_Safety Project Specification Baseline - V1.1

## Document Metadata
- **Status:** Baseline Defined (Executing Phase)
- **Author:** Claude Code (Synthesized)
- **Date:** 2026-06-04
- **Primary Goal:** To transition the AV\_Safety project from a theoretical, high-fidelity research model to a certifiable, executable engineering instrument.

## 🧭 Project Vision & Core Goal
The ultimate goal is to rigorously quantify the collision risk of autonomous vehicle systems, providing an evidence-backed comparison against leading international safety standards (UL 4600, ISO 21448, ISO 26262, NHTSA guidance).

## 🏗️ I. Current State Assessment (Audit Findings)
The codebase is soundly structured but incomplete in its executable compliance mechanisms.

**Strengths:**
- **Pipeline Integrity:** The 7-step pipeline (`Kinematics` $\to$ `Indicators` $\to$ `Modeling` $\to$ `Compliance`) is logically sound and highly advanced.
- **Technical Depth:** The use of Bayesian EVT, Monte Carlo, and ML ensemble models is cutting-edge.
- **Documentation:** Foundational theory (code conventions, models, standards mapping) is well-documented.

**Critical Gaps (Immediate Blockers):**
1.  **ISO 26262 Implementation (🔴 Critical):** ZERO executable code exists for ASIL classification, Safety Goals, HARA, and lifecycle management. This must be the immediate engineering focus.
2.  **Data Pipeline (🔴 Critical):** The system is theoretical. `data/raw` and `data/processed` are empty. The ingestion pipeline is not functional.
3.  **Validation Skill (🔴 Critical):** The `validation` skill exists as a conceptual requirement but has no implementation to verify the output.

## ⚙️ II. Executable Focus: Task Breakdown (The Plan)

All work is tracked under Task #1: **Comprehensive AV\_Safety Project Audit & UI Specification**. The execution is broken into parallel tasks:

*   **Task #2 (Skills Audit):** Continuous monitoring of the intellectual components. (Status: Completed initial high-level pass).
*   **Task #3 (Demo UI Review):** Defines the goal-facing execution target. (Status: Initial review complete).
*   **Task #4 (Synthesis):** The ongoing integration task.

**Next Logical Steps (The Execution Sequence):**
1.  **Foundation (Priority 1):** Begin coding the ISO 26262 framework (ASIL, HARA, Safety Goals).
2.  **Data Drive (Priority 2):** Implement the data ingestion pipeline.
3.  **Verification (Priority 3):** Implement the `validation` skill.

## 🖥️ III. UI Design & Deliverable Goal (The Target)

The goal of the UI is to translate the highly technical, multi-variable data outputs into an intuitive, actionable narrative. The UI must visually represent the compliance margin, the probability distributions, and the step-by-step pipeline flow.

**The successful delivery hinges on the parallel completion of the three core tasks:**
*   **Executable Code:** (The technical backbone)
*   **Data Driven:** (The fuel)
*   **Verified:** (The proof of concept)

---
*\[End of Specification Baseline]*