# Blockers — AV_Safety

**Last Updated:** 2026-06-07

---

## Active Blockers (2)

| ID | Issue | Impact | Blocker Details |
|----|-------|--------|-----------------|
| **BLK-001** | No external data source configured | Limits testing scope. Can't validate risk scoring against real-world crash data. | Requires FARS 2020 data access or similar. Awaiting. |
| **BLK-002** | No deployment target specified | Can't plan production rollout. Can't test staging vs production parity. | Requires container registry, hosting platform, DNS. Awaiting. |

---

## Blocked Items

- **CRIT-004** — Blocked by BLK-001 (can't test validation against real data)
- **Phase 6: Deployment** — Blocked by BLK-002 (no target to deploy to)
- **Integration Tests (TEST-001)** — Partially blocked by BLK-001 (can use synthetic data but real data preferred)

---

## Resolution Criteria

- **BLK-001:** Resolve when at least 1 external data source (FARS crash data, telemetry) is integrated into `/data/`
- **BLK-002:** Resolve when deployment target (container registry, hosting platform) is specified and accessible

---

*This blocker list is updated continuously. Last verified: 2026-06-07.*
