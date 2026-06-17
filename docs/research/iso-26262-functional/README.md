# ISO 26262 (Functional Safety) - Road Vehicles

**Source:** AV-SAFETY-CORE research integrated from APEX CONTROL workspace  
**Date:** 2026-06-16  
**Project:** AV-SAFETY-CORE  
**Researcher:** dir-research (Tier 2 Research Director)

---

## Overview and Scope

**Published:** 2nd Edition (2018)  
**Focus:** Functional safety of automotive electrical and electronic systems  
**Applies to:** All E/E systems in road vehicles (brakes, steering, airbags, ADAS, etc.)

**Core Purpose:** Ensure software errors and system malfunctions don't lead to human injury.

**Key Principle:** Systematic approach to safety throughout entire lifecycle (concept → decommissioning).

---

## ASIL (Automotive Safety Integrity Level)

### Classification System
Four risk levels from A (lowest) to D (highest):

| ASIL Level | Risk Level | Example Systems | Requirements |
|------------|------------|-----------------|--------------|
| ASIL A | Lowest | Interior lighting control | Minimal safety measures |
| ASIL B | Medium | Rear camera | Basic safety procedures |
| ASIL C | High | ABS, airbags | Stringent development methods |
| ASIL D | Highest | EPS, AEB | Maximum safety rigor |

### ASIL Determination Factors
1. **Severity (S):** Range S0 (no injury) to S3 (fatal injuries)
2. **Exposure (E):** Range E0 (incredibly unlikely) to E4 (highly probable)
3. **Controllability (C):** Range C0 (controllable) to C3 (uncontrollable)

---

## Functional Safety Requirements

### Lifecycle Requirements
- **Management:** Safety management processes, organizational responsibilities
- **Concept Phase:** Hazard analysis, risk assessment, safety goals
- **Product Development:** System, hardware, and software development
- **Production:** Manufacturing quality control
- **Operation:** Deployment, maintenance, repair
- **Decommissioning:** End-of-life safety considerations

### Key Documentation
- Safety Manual
- Technical Safety Concept
- Software Safety Concept
- Test Plans and Reports
- Traceability Matrix

---

## Development Process (V-Model)

```
Requirements → System Design → Hardware Design → Software Design
                ↓                  ↓                  ↓
         Integration Test ← System Test ← Unit Test ← Code Review
```

**Left side:** Development activities  
**Right side:** Verification activities  
**Each stage requires ASIL-appropriate methods and artifacts**

---

## Applicability to AV_Safety

### Relevance to AV_Safety Project
ISO 26262 is essential for collision risk modeling because:

1. **System-Level Safety:** Ensures the overall collision risk assessment system functions correctly even when individual components fail.

2. **Redundancy Requirements:** For high-ASIL systems (AEB, collision avoidance), ISO 26262 requires redundant safety mechanisms.

3. **Fault Tolerance:** Defines how the system should respond to component failures during risk assessment.

4. **Hardware Metrics:** Specifies mandatory coverage metrics (SPFM, LFM) for safety-critical risk assessment hardware.

5. **Software Verification:** Requires comprehensive testing of collision risk algorithms at all levels.

---

## Related Resources

- **ISO 26262-1:2018** - Road vehicles — Functional safety — Part 1: Vocabulary
- **ISO 26262-2:2018** - Road vehicles — Functional safety — Part 2: Management
- **ISO 26262-3:2018** - Road vehicles — Functional safety — Part 3: Concept phase
- **ISO 26262-4:2018** - Road vehicles — Functional safety — Part 4: System development
- **ISO 26262-5:2018** - Road vehicles — Functional safety — Part 5: Hardware development
- **ISO 26262-6:2018** - Road vehicles — Functional safety — Part 6: Software development

---

*This document was integrated from APEX CONTROL's AV-SAFETY-CORE research effort.*
