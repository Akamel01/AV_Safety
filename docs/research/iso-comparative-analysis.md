# ISO Standards Comparative Analysis

**Source:** AV-SAFETY-CORE research integrated from APEX CONTROL workspace  
**Date:** 2026-06-16  
**Project:** AV-SAFETY-CORE  
**Researcher:** dir-research (Tier 2 Research Director)

---

## How Standards Complement Each Other

| Aspect | ISO 26262 | SOTIF | Combined Coverage |
|--------|-----------|-------|-------------------|
| Risk Type | Functional safety (malfunctions) | Performance limitations | Complete hazard coverage |
| Trigger | System failure | Normal operation limitations | All hazard sources |
| Systems Addressed | All E/E systems | Perception and decision systems | Full vehicle safety |
| Validation Focus | Failure modes | Edge cases, triggering conditions | Real-world scenarios |

---

## Overlaps and Gaps

### Overlaps
- Both standards require hazard analysis and risk assessment
- Both address validation and verification
- Both consider the complete system lifecycle

### Complementary Coverage
- **ISO 26262 gaps:** Performance limitations without faults
- **SOTIF gaps:** Hardware/software failures
- **Together:** Complete safety coverage

### Integration Points
- Safety goals from ISO 26262 may trigger SOTIF analysis
- SOTIF findings may require ASIL re-evaluation
- Common documentation structure facilitates integration

---

## Best Practices for AV_Safety

### Recommended Approach
1. **Start with ISO 26262:** Establish functional safety baseline for all E/E systems
2. **Apply SOTIF:** Analyze perception and decision systems for performance limitations
3. **Integrate Findings:** Create unified safety case covering both fault and performance risks
4. **Continuous Validation:** Validate against evolving edge cases and real-world data

### Key Integration Practices
- Unified hazard analysis covering both failure and performance modes
- Common risk assessment methodology across both standards
- Shared test framework with appropriate metrics for each domain
- Integrated traceability from safety goals to verification

---

## Recommendations for AV_Safety Collision Risk Framework

### Technical Recommendations
1. **Multi-Layer Risk Assessment:** Implement both fault detection (ISO 26262) and performance monitoring (SOTIF)
2. **Scenario-Based Validation:** Use SOTIF's 4-area model for edge case coverage
3. **Redundant Systems:** For high-risk collision scenarios, implement ISO 26262-compliant redundancy
4. **Statistical Validation:** Use SOTIF requirements for performance metrics under varying conditions

### Process Recommendations
1. **Integrated Team:** Combine functional safety and SOTIF expertise
2. **Unified Documentation:** Create shared safety case with appropriate sections for each standard
3. **Continuous Learning:** Use real-world data to update both standards compliance
4. **Cross-Verification:** Independent validation of both safety approaches

---

## Identified Gaps and Areas Needing Further Research

### Technical Gaps
1. **AI/ML Model Validation:** SOTIF guidance for deep learning systems needs expansion
2. **Cross-Standard Integration:** Framework for unified safety case development
3. **Cybersecurity Integration:** How ISO 21448 and ISO 21434 (cybersecurity) interact
4. **Edge Case Prioritization:** Methods for focusing validation on most critical scenarios

### Research Areas
1. **Quantitative Risk Assessment:** Statistical methods for SOTIF validation
2. **Real-World Scenario Capture:** Methods for identifying and cataloguing edge cases
3. **Automated Safety Validation:** Tools for continuous compliance checking
4. **Human Factor Integration:** Better understanding of foreseeable misuse patterns

---

## Summary and Key Takeaways

### Key Findings Summary

| Standard | Primary Focus | Critical For | Validation Approach |
|----------|---------------|--------------|---------------------|
| ISO 26262 | Functional safety (failures) | Hardware/software faults | Failure mode analysis, fault injection |
| ISO 21448 (SOTIF) | Performance limitations | Perception/decision systems | Edge case testing, statistical validation |

### Practical Recommendations for AV_Safety
1. **Implement Both Standards:** Complete safety requires covering both faults and performance limitations
2. **Integrated Team:** Combine functional safety engineers with SOTIF experts
3. **Unified Documentation:** Create shared safety case with appropriate sections for each standard
4. **Continuous Validation:** both standards require ongoing validation as new scenarios emerge

### Collision Risk Modeling Specific Guidance
- **Perception Systems:** Apply SOTIF for sensor limitation coverage; ISO 26262 for communication and processing faults
- **Decision Systems:** Apply SOTIF for algorithm edge cases; ISO 26262 for software fault tolerance
- **Output Systems:** Apply ISO 26262 for all E/E output systems; consider SOTIF for interface limitations

---

## References and Resources

### Standards Documents
- ISO 21448:2022 Road vehicles — Safety of the intended functionality
- ISO 26262-1:2018 Road vehicles — Functional safety — Part 1: Vocabulary
- ISO 26262-2:2018 Road vehicles — Functional safety — Part 2: Management of functional safety
- ISO 26262-3:2018 Road vehicles — Functional safety — Part 3: Concept phase

### Additional Resources
- SPK and Associates SOTIF Guide
- Walter Consulting SOTIF Explained
- Jama Software ASIL Overview
- Synopsys ASIL Definition

### Related Standards
- ISO 21434:2021 Road vehicles — Cybersecurity engineering
- ISO 17385:2020 Road vehicles — Software update for type approval
- AUTOSAR standards for software architecture

---

*This document was integrated from APEX CONTROL's AV-SAFETY-CORE research effort.*
