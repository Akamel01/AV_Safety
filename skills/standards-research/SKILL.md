---
name: standards-research
description: "Search, extract, organize, and summarize safety standards and regulations relevant to AV safety research."
---

# Standards Research

Search, extract, organize, and summarize safety standards and regulations relevant to AV safety research.

## Standards Framework

### UL 4600 — Safety of the System for the Evaluation of the Autonomy of the Unmanned Systems
- **Section 6.2:** Risk Assessment Methodology
- **Section 7.1:** Hazard Identification
- **Section 10:** Safety Case Evidence
- **Key:** System safety, autonomy levels, hazard identification framework

### ISO 21448 (SOTIF) — Safety of the Intended Functionality
- **HARA:** Hazard Analysis and Risk Assessment
- **Section 5.3:** Perceived functional hazards
- **Section 6:** Performance limitations
- **Section 8:** Manipulation and misuse
- **Key:** No functional failure scenarios, performance boundaries, operational design domain

### ISO 26262 — Functional Safety
- **ASIL** (Automotive Safety Integrity Level) classification
- **Safety goals and requirements** (Part 2)
- **Technical safety requirements** (Part 4)
- **Key:** QM, ASIL-A through ASIL-D, safety mechanisms

### ISO 21002 — Safety of Automated Road Transport Systems
- **Scope:** ARTS (Automated Road Transport Systems)
- **Key:** Operational design domain, fallback strategies, validation requirements

### NHTSA Publications
- **NHTSA AV Safety Framework:** 12-phase evaluation process
- **FMVSS (Federal Motor Vehicle Safety Standards):** vehicle-specific requirements
- **NHTSA FARS:** Fatality Analysis Reporting System — crash data
- **NHTSA CISS:** Crash Investigation Sampling System
- **NHTSA ES-28:** Injury severity correlation (BANSYSE)

### Transport Canada (Canada)
- **Transport Canada AV Guidelines**
- **CMFwiki Canada:** Crash Modification Factors database
- **ICBC (British Columbia):** Auto insurance crash data

### DfT GB / Highways England (England)
- **DfT GB Road Casualties Statistics**
- **JACArP (Joint Automobile Collision Analysis and Research Project)**
- **UK AV Standards**
- **JCTC guidance**

## Cross-Referencing Framework

| Requirement | UL 4600 | ISO 21448 | ISO 26262 | NHTSA |
|---|-|-|-|-|
| Hazard Identification | Sec 7.1 | HARA | Part 2, Sec 8.4 | AV Framework |
| Risk Assessment | Sec 6.2 | Sec 5.3, HARA | Part 2 | ES-28 |
| Validation | Sec 10 | Sec 12 | Part 11 | FMVSS |
| Fallback Strategy | Sec 8 | Sec 6 | Part 4 | AV Framework |
| ODD Definition | Sec 3.2 | Sec 5.2 | — | AV Framework |

## Compliance Mapping Matrix

For each project requirement R_i:
1. Identify all applicable standards and clauses
2. Map compliance status: compliant / non-compliant / unknown
3. Document gaps and assumptions
4. Track updates when standards are revised

## Workflow

1. **Identify** relevant standards for a given safety question
2. **Extract** key requirements and metrics from each standard
3. **Cross-reference** overlapping requirements across standards
4. **Document** findings in `docs/standards/` with source URLs and clause references
5. **Update** compliance mapping when new standards are added

## Output Format

Each standard analysis documented in:
- `docs/standards/<standard-code>-analysis.md`
- Include: key clauses, relevant metrics, jurisdiction, date effective, cross-references

## Reuse Trigger

Use when:
- Starting any new safety analysis
- Validating requirements against known standards
- Building compliance matrices for portfolio
- Answering "what does the standard say about X?"

## File Structure
```
docs/standards/
├── ul-4600-analysis.md
├── iso-21448-analysis.md
├── iso-26262-analysis.md
├── iso-21002-analysis.md
├── nhtsa-av-framework.md
├── fmvss-index.md
├── transport-canada-avs.md
├── cmfwiki-canada.md
├── dft-gb-casualties.md
├── jacarp-england.md
└── cross-reference-matrix.md
```
