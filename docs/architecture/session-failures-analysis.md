# Session Failures — 2026-06-02 (16:30–17:30 PDT)

## Total Failures: 14 turns failed across the session

---

### FAILURE #1: Turn 97 — Massive Initial Overload
**Time:** ~16:31 PDT
**Trigger:** First real task — "create project, set up workspace"
**What happened:** Tried to create 8+ files, edit 2 workspace files, git init, commit all in one turn. Response was ~5000+ tokens.
**Error:** `request timed out`
**Root cause:** Exceeded turn budget. 8+ file ops + massive prose = model couldn't generate full response before timeout.
**Status:** ⚠️ Partial — some files wrote but turn failed, content was never delivered to user.

### FAILURE #2: Turn 109 — Large Multi-Block Edit
**Time:** ~16:32 PDT
**Trigger:** Attempting to fix investigation-plan.md
**What happened:** Sent 8 block edits in single edit call.
**Error:** `stopReason: "stop"` — content was never produced (turn cut off at boundary)
**Root cause:** Multi-block edits are expensive in token space. Combined with long explanation prose, the turn was too large.
**Status:** 🔴 7 of 8 edits silently failed. Only the first succeeded.

### FAILURE #3: Turn 115 — GitHub Auth Check Turn Cut-Off
**Time:** ~16:32 PDT
**Trigger:** Checking gh auth status before repo creation
**What happened:** exec call succeeded, but assistant turn failed before producing repo creation call.
**Error:** `stopReason: "stop"` (content truncated at turn boundary)
**Root cause:** The auth output (token visibility) was included in context, pushing response over limit. Need to keep assistant response short after tool results.
**Status:** ⚠️ Required extra turn to retry.

### FAILURE #4: Turn 117 — Continued auth check pattern
**Time:** ~16:33 PDT
**Trigger:** Same as #3
**Error:** `stopReason: "stop"`
**Root cause:** Same pattern — exec succeeded but response generation hit boundary before completion.
**Status:** 🔴 Wasted turn.

### FAILURE #5: Turn 121 — Repo creation + push attempt
**Time:** ~16:33 PDT
**Trigger:** Creating the repo and pushing
**What happened:** Repo was actually created (exec succeeded), but assistant produced a long response trying to explain + push simultaneously.
**Error:** `stopReason: "stop"`
**Root cause:** Trying to explain repo creation AND issue push command in same turn.
**Status:** 🔴 Wasted turn despite partial success.

### FAILURE #6: Turn 153 — Push + explanation combined
**Time:** ~16:34 PDT
**Trigger:** After repo creation, pushing code
**What happened:** exec succeeded, response hit boundary.
**Error:** `stopReason: "stop"`
**Root cause:** Same — exec output + explanation = too much for turn budget.
**Status:** 🔴 Wasted turn.

### FAILURE #7: Turn 155 — User complaint + assistant response
**Time:** ~16:35 PDT
**Trigger:** User said "you keep failing"
**What happened:** Assistant tried to respond to the complaint with explanation.
**Error:** `request timed out`
**Root cause:** The accumulated context from all previous failures made the turn even larger than usual. Model timed out before generating response.
**Status:** 🔴 Complete failure.

### FAILURE #8: Turn 163 — LLM Idle Timeout (120s)
**Time:** ~16:36 PDT
**Trigger:** User asked "how to restart openclaw"
**What happened:** LLM completely stopped responding. No tool calls at all.
**Error:** `LLM idle timeout (120s): no response from model`
**Root cause:** The model either crashed or went into an infinite loop. 120s of zero output = model is unresponsive, not just slow.
**Status:** 🔴 Complete model failure.

### FAILURE #9: Turn 165 — After idle timeout, model recovered
**Time:** ~16:37 PDT
**Trigger:** User repeated "how to restart openclaw"
**What happened:** Model recovered but response was cut off.
**Error:** `stopReason: "stop"`
**Root cause:** After recovery, accumulated context was enormous. Even a simple answer couldn't fit.
**Status:** 🔴 Partial failure.

### FAILURE #10: Turn 147-150 — sessions_history repeated failure (7 turns)
**Time:** ~16:33 PDT
**Trigger:** Trying to capture session failures for documentation
**What happened:** Called `sessions_history` 8 times without required `sessionKey="current"` parameter. First 7 failed with validation error.
**Error:** `Validation failed for tool "sessions_history": sessionKey: must have required properties sessionKey`
**Root cause:** Missing required parameter. Worst case: repeated the same failing call 7 times instead of adapting after first failure.
**Status:** 🔴 7 wasted turns of identical failures.

### FAILURE #11: Turn 151 — Pre-commit checklist append
**Time:** ~16:35 PDT
**Trigger:** Attempting to update AGENTS.md with pre-commit checklist
**What happened:** exec command for appending to AGENTS.md succeeded (no output = success), but turn cut off.
**Error:** `stopReason: "stop"`
**Root cause:** Context was already enormous from accumulated turns.
**Status:** ⚠️ File was updated but user never saw confirmation.

### FAILURE #12: Turn 155 again — request timeout on "you keep failing"
**Time:** ~16:37 PDT
**Trigger:** User's second "you keep failing"
**What happened:** Another request timeout
**Error:** `request timed out`
**Root cause:** Context window was now extremely large from accumulated turns + all previous tool outputs.
**Status:** 🔴 Complete failure.

### FAILURE #13: Turn 171 — Current turn (just completed)
**Time:** ~17:29 PDT
**Trigger:** "document all failures and pending fixes"
**What happened:** Attempted to compile the list
**Error:** (in progress — just captured sessions_history)
**Status:** ✅ This turn is producing results now because I'm being deliberate and concise.

---

## Summary of Failure Patterns

### Pattern 1: Context Bloat Cascade (PRIMARY ROOT CAUSE)
Every failed turn added to the context window without reducing it. Each subsequent turn became heavier because:
- All previous tool outputs are retained in context
- Failed turns still count toward context size
- The model has to "read" all previous context before generating new output
- Result: exponentially increasing turn cost → more timeouts → more context bloat → more timeouts

**Fix:** Stop and assess when context exceeds ~50% of model's capacity. Compaction or context reduction may be needed.

### Pattern 2: No Failure Recovery (AGENTS.md Rule 4 violation)
Turns #7-14 (sessions_history) are the worst example:
- First failure → should adapt (fix parameter)
- Second failure → should ask user for guidance  
- Third failure → should stop entirely
- Instead: same failing call repeated 7 times

**Fix:** Implement hard stop-after-2 at the behavioral level.

### Pattern 3: Multi-Operation Turns
Every early failure was caused by doing too many things at once:
- File writes + edits + git + long prose = too many tokens
- Edit calls with 8+ blocks = too many blocks
- exec output + explanation = too much for turn budget

**Fix:** One tool category per turn. Max 2 ops per category. Response ≤ 15 lines.

### Pattern 4: No Self-Compaction
When context grew large, no attempt was made to:
- Summarize/clean old context
- Use compaction (if available)
- Reduce working context
- Acknowledge the problem and start fresh

**Fix:** Monitor context usage. When >70%, pause and clean up.

---

## Pending Fixes

### Immediate (must do now)
1. ✅ Operational issues plan documented at `docs/architecture/fixing_operational_issues_plan.md` — DONE
2. ✅ AGENTS.md workflow discipline rules — DONE  
3. ✅ SOUL.md workflow rules — DONE
4. 🔲 **Verify pre-commit checklist was appended to AGENTS.md** (turn failed at #11, not confirmed)
5. 🔲 **Verify git config user identity is fixed** (user asked, never completed)
6. 🔲 **Build the kinematics engine skill** (planned but never reached)

### Behavioral (must follow going forward)
1. One tool category per turn (no mixing file/git/exec)
2. Max 2 file ops, 1 git cmd per turn
3. Response ≤ 15 lines always
4. First failure → adapt. Second failure → ask user. Third → stop.
5. Never repeat same failing tool call
6. Monitor context usage — clean up when >70%
7. Goal-oriented, small batches, no wall-of-text
8. Before any tool call, verify required parameters

### Systemic (OpenClaw-level considerations)
1. Model (qwen3.6:35b) seems to timeout more easily on long context — may need to switch model for complex tasks
2. No auto-compaction in place — context keeps growing across failures
3. LLM idle timeout (120s) is real — when model is unresponsive, user should be told immediately
4. Consider using a more stable/faster model for complex reasoning tasks
