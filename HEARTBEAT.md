# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

### 📋 STATUS.md Enforcement

The agent MUST check STATUS.md exists in every active project during heartbeats. If a project has `Task_Ledger.md`, `Run_Checkpoints.md`, `Blockers.md`, `Open_Issues.md`, or `Validation_Log.md` but NO `STATUS.md`, create it immediately with the standard sections: Current Status, Phase Breakdown, What's Done, What's Next, Critical Path, Blockers.

If STATUS.md exists but hasn't been updated in 3+ sessions, flag it as stale and update it.
