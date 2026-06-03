# Skill: Standards Research

**Purpose:** Search, extract, organize, and summarize safety standards and regulations relevant to AV safety research.

## Capabilities

1. **Standards search** — Search for relevant UL 4600, ISO, NHTSA, UK DVSA standards
2. **Standard extraction** — Extract key clauses, requirements, and metrics from standard texts
3. **Cross-referencing** — Map requirements across different standards (e.g., UL 4600 ↔ ISO 21448 ↔ NHTSA)
4. **Compliance mapping** — Build matrices linking project requirements to specific standard clauses

## Prerequisites

- Access to standards databases (ISO store, ANSI, NHTSA.gov)
- PDF/text parsing capabilities
- Cross-referencing framework

## Workflow

1. **Identify** relevant standards for a given safety question
2. **Extract** key requirements and metrics from each standard
3. **Cross-reference** overlapping requirements across standards
4. **Document** findings in `docs/standards/` with source URLs and clause references
5. **Update** compliance mapping when new standards are added

## Output Format

Each standard analysis should be documented in:
- `docs/standards/<standard-code>-analysis.md`
- Include: key clauses, relevant metrics, jurisdiction, date effective, cross-references

## Rules

- Always cite source URLs and clause numbers
- Note version/edition of each standard
- Flag any gaps where standards conflict or are silent
- Never assume; if a requirement isn't stated, mark it as unknown

## Reuse

This skill is used when:
- Starting any new safety analysis
- Validating requirements against known standards
- Building compliance matrices for portfolio
- Answering "what does the standard say about X?"
