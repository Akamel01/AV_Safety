# Hazard Analysis and Risk Assessment (HARA) - AV_Safety Project

**Date:** 2026-06-04
**Status:** Draft - Phase 1.1
**Goal:** To identify all potential operational hazards of the Autonomous Vehicle system and assess their severity to inform Safety Goal definition (Phase 1.2).

## 1. System Context

The AV\_Safety system is designed to operate in dynamic environments, executing high-level driving decisions from sensor inputs through actuation outputs. Failure modes arise from misinterpretation of sensor data, latency in decision making, or execution errors in low-level controllers.

## 2. Identified Hazards and Failure Modes

The following table lists potential failure modes discovered during the conceptual review of the operating envelope. Each mode leads to a specific hazardous event.

| Hazard ID | Hazard Description | Potential Failure Mode | Domain | Exposure |
| :--- | :--- | :--- | :--- | :--- |
| **H-001** | **Unintended Acceleration/Deceleration** | Faulty throttle command; stuck actuator; loss of braking response. | Actuation/Control | High |
| **H-002** | **Target Misidentification** | Misclassification of dynamic object (e.g., cyclist as static obstacle); tracking failure. | Sensing/Perception | High |
| **H-003** | **Failure to Respond** | Sensor failure causing missed object detection; computing deadlock. | Decision/Compute | High |
| **H-004** | **Erroneous Maneuver** | Executing a maneuver in an unintended state (e.g., sudden swerve into oncoming lane). | Planning/Control | Critical |
| **H-005** | **Loss of Control in Edge Case** | System operating outside modeled envelope (e.g., sudden severe weather, unprecedented object presence). | Environment/Compute | Critical |

## 3. Severity Ranking (S)

Severity is ranked based on the likelihood and magnitude of harm to vulnerable road users (VRUs) and occupants.

*   **S3 (Critical):** Leads to severe injury or fatality due to system failure (e.g., uncontrolled acceleration into a barrier).
*   **S2 (Severe):** Leads to serious injury but survivable if mitigated (e.g., high-speed near-miss requiring evasive action).
*   **S1 (Minor):** Leads to minor property damage or transient discomfort (e.g., unnecessary hard braking in clear conditions).

**Current Assessment:**
*   H-001 (Unintended Acceleration): **S3**
*   H-002 (Target Misidentification): **S3**
*   H-003 (Failure to Respond): **S3**
*   H-004 (Erroneous Maneuver): **S3**
*   H-005 (Loss of Control): **S3**

## 4. Moving to Safety Goals (Next Step)

All current high-level hazards are rated S3 (Critical). This dictates that the resulting Safety Goals derived from these hazards must also be implemented to the highest required integrity level, which we provisionally label ASIL D.

**Next Task:** Translate these S3 hazards into formalized, measurable Safety Goals (Phase 1.2) and define the specific ASIL requirements.