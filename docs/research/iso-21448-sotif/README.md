# ISO 21448 (SOTIF) - Safety of the Intended Functionality

**Source:** AV-SAFETY-CORE research integrated from APEX CONTROL workspace  
**Date:** 2026-06-16  
**Project:** AV-SAFETY-CORE  
**Researcher:** dir-research (Tier 2 Research Director)

---

## Overview and Scope

**Published:** 2022 (evolved from PAS 21448)  
**Focus:** Safety of the Intended Functionality  
**Applies to:** Advanced Driver Assistance Systems (ADAS) and autonomous functions at SAE Levels 1-2+

**Core Purpose:** Address hazards that arise **without system faults** - when systems work exactly as designed but still make wrong decisions.

**Key Distinction from ISO 26262:**
- **ISO 26262** → failure-based risks (malfunctions, hardware/software bugs)
- **SOTIF** → performance-based risks (limitations in intended functionality)

---

## Key Concepts and Terminology

### Triggering Conditions
Specific conditions that activate functional insufficiencies, leading to hazardous events.

**Examples for ADAS systems:**
- Direct sunlight into camera causing sensor saturation
- Pedestrian wearing clothing similar to background
- Construction zones with unusual lane markings
- Heavy rain reducing LiDAR range
- Cyclist hidden behind large vehicle

### Four-Area Scenario Classification

| Area | Description | Example |
|------|-------------|---------|
| Area 1 | Known safe scenarios | System operates correctly and safely |
| Area 2 | Known unsafe scenarios | System known to fail; mitigations implemented |
| Area 3 | Unknown unsafe scenarios | System might fail but not yet identified |
| Area 4 | Unknown safe scenarios | Not yet evaluated but happen to be safe |

### Functional Insufficiencies
Limitations in system algorithms, sensors, or actuators that cause unsafe outcomes despite correct operation.

### Reasonably Foreseeable Misuse
Hazardous behavior caused by operator actions that the system should anticipate (e.g., driver distraction, improper system use).

---

## Hazard Analysis and Risk Assessment

### Process Overview
1. Identify operational concepts and scenarios
2. Analyze functional insufficiencies in perception and decision-making
3. Evaluate triggering conditions
4. Assess hazard severity, exposure, and controllability
5. Determine SOTIF ASIL (if applicable)
6. Define safety goals and mitigation strategies

### Validation and Verification Methods

**Required Methods:**
- Rigorous testing in diverse real-world conditions
- Extensive simulation across edge cases
- Statistical analysis of performance metrics
- Background ground truth comparison
- User behavior studies for foreseeable misuse

### Key Metrics
- Detection rate under varying conditions
- False positive/negative rates
- Response time under stress
- Performance degradation curves

---

## Applicability to AV_Safety

### Direct Relevance to AV_Safety Project
SOTIF is critically important for collision risk modeling in AV_Safety because:

1. **Perception Limitations:** Collision risk models depend heavily on sensor fusion and object classification. SOTIF addresses scenarios where sensors work perfectly but provide insufficient or misleading data.

2. **Algorithmic Limitations:** Risk prediction algorithms may be correctly implemented but operate outside their validated domain (e.g., extreme weather, unusual road conditions).

3. **Edge Cases:** SOTIF provides the framework for identifying and mitigating edge cases that could lead to incorrect collision risk assessment.

4. **Validation Framework:** SOTIF's scenario classification (4-area model) directly applies to collision risk model validation.

---

## Related Resources

- **ISO 21448:2022** - Road vehicles — Safety of the intended functionality
- **SPK and Associates SOTIF Guide** - Comprehensive implementation guide
- **Walter Consulting SOTIF Explained** - Practical interpretation
- **Jama Software SOTIF Overview** - Industry perspective

---

*This document was integrated from APEX CONTROL's AV-SAFETY-CORE research effort.*
