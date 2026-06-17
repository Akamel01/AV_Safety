# AV-SAFETY-CORE ISO Safety Standards Research

**Project:** AV-SAFETY-CORE  
**Task ID:** TASK-003  
**Assignee:** dir-research (Tier 2 Research Director)  
**Date Completed:** 2026-06-16  
**Status:** ✅ Completed  
**Source:** Integrated from APEX CONTROL workspace

## Executive Summary

This research provides a comprehensive analysis of ISO 21448 (SOTIF) and ISO 26262 (Functional Safety) standards for autonomous vehicle collision risk modeling. The research covers:

- Core concepts and terminology for both standards
- Hazard analysis and risk assessment methodologies
- Validation and verification approaches
- Practical applications for collision risk modeling
- Integration guidance for unified safety cases

## Document Contents

| Section | Content |
|---------|---------|
| **1. ISO 21448 (SOTIF)** | Safety of Intended Functionality, performance limitations, triggering conditions, 4-area model |
| **2. ISO 26262** | Functional safety, ASIL classification, V-model development, safety requirements |
| **3. Comparative Analysis** | How standards complement each other, overlaps, best practices |
| **4. Practical Applications** | AV safety systems, collision detection, perception, decision systems |
| **5. Recommendations** | Technical guidance, process recommendations, future research |

## Key Findings

### SOTIF vs ISO 26262 - Core Distinction

| Aspect | ISO 26262 | SOTIF |
|--------|-----------|-------|
| Risk Type | Malfunctions/failures | Performance limitations |
| Trigger | System fault | Normal operation limitation |
| Example | Brake system failure | Camera misinterprets object |
| Focus | Safety of the system | Safety of the functionality |

### ASIL Classification

| Level | Risk | Example Systems | Requirements |
|-------|------|-----------------|--------------|
| ASIL A | Lowest | Interior lighting | Minimal measures |
| ASIL B | Medium | Rear camera | Basic safety |
| ASIL C | High | ABS, airbags | Stringent methods |
| ASIL D | Highest | EPS, AEB | Maximum rigor |

### Critical Integration Points

1. **Unified Hazard Analysis:** Cover both failure modes and performance limitations
2. **Common Risk Assessment:** Use consistent methodology across standards
3. **Shared Test Framework:** Appropriate metrics for each domain
4. **Integrated Traceability:** From safety goals to verification

## Deliverables Created

- `README.md` - Comprehensive research document (~13KB)
- `av-safety-research/` directory - Research workspace

## Next Steps

1. **Review and Validation:** Team review of research findings
2. **Framework Integration:** Apply findings to collision risk model
3. **Documentation:** Update PROJECTS.md with AV-SAFETY-CORE status
4. **Task Completion:** Update tasks.json with TASK-003 status

## Research Quality

- Sources: Multiple authoritative industry resources
- Coverage: Both standards comprehensively analyzed
- Practicality: Focused on AV collision risk applications
- Integration: Clear guidance on combining both standards

---

**Contact:** dir-research for research questions or clarifications

---

*This document was integrated from APEX CONTROL's AV-SAFETY-CORE research effort. The full research package is available in `/Users/akamel/projects/AV_Safety/docs/research/`.*
