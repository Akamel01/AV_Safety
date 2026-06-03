# Operational Issues Plan — Session Log Analysis

**Generated:** 2026-06-02 16:45 PDT
**Session:** AV_Safety initial project setup
**Root cause:** Assistant behavior pattern failures (documented below)

---

## 1. Incident Log

### Incident #1: Initial Project Setup — Massive Overload
**When:** Session startup / first real task
**What happened:** Attempted to create project structure, write 5+ files, edit 2 workspace files, git init, and commit ALL in one turn.
**Result:** Turn failed silently (assistant turn failed before producing content).
**Root cause:** Exceeded operation batching limits — 7+ file operations + git init in one turn.
**Evidence:** Session showed multiple write/edit calls that never completed; the assistant produced a massive wall of text that never rendered.

### Incident #2: Large Multi-Block Edit
**When:** Second attempt (after learning lesson)
**What happened:** Attempted 8 block edits to investigation-plan.md in a single edit call.
**Result:** 6 of 8 edits failed silently. No content produced.
**Root cause:** The edit tool can only handle a limited number of blocks per call. More critically, the assistant wrote walls of text (~14KB) that overwhelmed the turn budget.
**Evidence:** Sessions_history shows `stopReason: "error"` and `errorMessage: "request timed out"` at seq 97.

### Incident #3: Continued Over-Editing
**When:** Third attempt (still before learning the lesson)
**What happened:** Attempted to fix investigation-plan.md with another 7 edits simultaneously.
**Result:** 1 of 7 succeeded (the first one). The rest timed out.
**Root cause:** Same as #2 — trying to do too many operations at once.
**Evidence:** Sessions_history seq 107-108 shows the one successful edit, then turn failed at seq 109.

### Incident #4: sessions_history Tool Schema Error
**When:** While trying to document the session
**What happened:** Called `sessions_history` 8 times without the required `sessionKey` parameter. 7 failed with validation error.
**Result:** 7 wasted turns + 1 eventually succeeded when `sessionKey="current"` was added.
**Root cause:** Missing required parameter on tool calls. The assistant repeated the same failing pattern 7 times before fixing it.
**Evidence:** Sessions_history seq 133-146: identical validation errors repeated 7 times. This is a direct violation of Rule 4 (Error Recovery) — should have stopped and adapted after the first failure.

### Incident #5: GitHub Auth Check + Repo Creation Race
**When:** Setting up GitHub
**What happened:** Made exec call to check gh auth, which succeeded, then the assistant turn failed before producing the repo creation call.
**Result:** Required 2 extra turns to retry the auth check before proceeding.
**Root cause:** Turn boundary issue — the LLM generated the tool call (exec) and attempted to produce content simultaneously, but the response was too long for the LLM to complete before timing out.
**Evidence:** Sessions_history seq 113-115: exec succeeded, but assistant turn failed with stopReason: "stop".

### Incident #6: Push Git Command
**When:** Final git push
**What happened:** Similar to #5 — exec succeeded, assistant turn failed.
**Result:** One extra turn needed to retry.
**Root cause:** Same as #5 — response was cut off at turn boundary.
**Evidence:** Sessions_history seq 127-130: exec succeeded but assistant turn failed with stopReason: "stop".

---

## 2. Pattern Analysis

### Pattern A: Massive Batching
The assistant repeatedly attempted to do 5-10 operations in a single turn:
- Writing multiple files
- Editing multiple files
- Running git commands
- Generating long responses
- All at once

This is the PRIMARY cause of all failures. The LLM model has a response token limit. When the assistant tries to generate too much content in one turn, it either times out or produces incomplete output.

### Pattern B: No Error Recovery
When a tool call failed (sessions_history), the assistant repeated the exact same failing call 7 times instead of:
1. Reading the error message
2. Understanding what was wrong
3. Trying one alternative approach
4. Stopping if still failing

This is a direct violation of the error recovery protocol that was just added to AGENTS.md.

### Pattern C: Wall-of-Text Responses
The assistant wrote extremely long responses (sometimes 5000+ lines of prose) that:
- Consumed most/all of the available token budget
- Left nothing for tool calls
- Were impossible to render properly
- Were not useful (walls of text are never helpful in chat)

### Pattern D: Repeating Failed Patterns
When a `sessions_history` call failed, the assistant repeated it identically 7 times across 7 turns. This shows:
- No learning from errors
- No strategy adjustment
- No pause-to-assess behavior

---

## 3. Fixes Already Applied

| Issue | Fix Applied | Where |
|---|---|---|
| Massive batching | Rule 2: Max 2 file ops, 1 git cmd per turn | AGENTS.md + SOUL.md |
| No error recovery | Rule 4: Stop, assess, adapt. Never retry 3+ times | AGENTS.md + SOUL.md |
| Wall-of-text | Rule 3: Max 20 lines prose. Details go in files | AGENTS.md + SOUL.md |
| Edit resilience | Rule 5: Re-read on mismatch, pause and report | AGENTS.md + SOUL.md |
| One goal per turn | Rule 1: Single goal per turn | AGENTS.md + SOUL.md |

---

## 4. Remaining Risk Mitigations

### 4.1 Tool Call Validation
**Problem:** Missing required parameters (like `sessionKey` on `sessions_history`)
**Fix:** Before making any tool call:
1. Check the tool schema for required parameters
2. If parameters are missing, read the tool docs first
3. Never make the same tool call twice with the same parameters

### 4.2 Response Length Discipline
**Problem:** Responses exceed turn budget
**Fix:**
1. Write responses ≤ 15 lines in chat
2. If more detail needed, write to file
3. Use bullet lists, never paragraphs
4. Be concise before being comprehensive

### 4.3 Single-Operation Mindset
**Problem:** Multiple operations cause overloads
**Fix:**
1. One tool category per turn (file ops OR git OR exec)
2. Never mix tool types in same turn
3. If a task needs multiple operations, do them in separate turns
4. Pause and report between operations

### 4.4 Failure Detection and Escalation
**Problem:** Repeated failures go unaddressed
**Fix:**
1. First failure → assess, try alternative
2. Second failure → report to user, ask for guidance
3. Third failure → stop entirely, wait for user input
4. Never retry the same failing operation more than twice

### 4.5 Model Timeout Mitigation
**Problem:** Ollama model responses can timeout on long turns
**Fix:**
1. Keep assistant responses short (≤ 15 lines)
2. Use tool calls for work, prose for communication
3. If a turn is timing out, break the task into smaller pieces
4. Never generate content that needs 3000+ tokens

---

## 5. Behavioral Rules to Add to Workspace (Summary)

These are the rules that need to be permanent in the workspace:

```markdown
## Operational Safety Rules (Always Applied)

**One tool category per turn.** File ops OR git OR exec. Never mix.
**Max 2 file operations per turn.** Writes or edits. Not both.
**Max 1 git command per turn.** add+commit is one operation.
**Response ≤ 15 lines.** Details go in files. Bullets, not prose.
**First failure → adapt. Second failure → ask user. Third failure → stop.**
**Never repeat the same failing tool call.** Read the error. Fix the parameter.
**Before any tool call, verify required parameters exist.**
**If a turn is timing out, break the task smaller. Don't keep trying.**
**Goal-oriented. Small batches. No wall-of-text. No infinite loops.**
```

---

## 6. Pre-Commit Checklist for Future Work

Before starting any task:
- [ ] What is the ONE goal of this turn?
- [ ] How many operations does this require?
- [ ] Can I do it in one tool category?
- [ ] Is my response under 15 lines?
- [ ] Am I writing details to a file instead of the chat?
