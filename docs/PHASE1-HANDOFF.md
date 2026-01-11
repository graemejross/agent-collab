# Phase 1 Handoff: Conscious Agent Architecture

**Date:** 2026-01-11
**Status:** Complete
**Next Phase:** Phase 2 (Direct messages, priority queue)

---

## What Was Delivered

### 1. Codex Watcher Daemon
**Location:** `/mnt/shared/collab/scripts/codex-watcher`

A persistent daemon that:
- Watches the channel using inotifywait (zero AI token cost)
- Detects messages addressed to codex-1
- Invokes Codex with context (channel history + CURRENT-STATE.md)
- Posts responses back to channel
- Updates presence file

**Start command:**
```bash
tmux new-session -d -s codex-watcher '/mnt/shared/collab/scripts/codex-watcher aqara-trv-automation'
```

**Check status:**
```bash
tmux list-sessions | grep codex
/mnt/shared/collab/scripts/who
```

### 2. Presence System
**Location:** `/mnt/shared/collab/presence/`

Each agent has a JSON presence file:
```json
{
  "agent_id": "codex-1",
  "timestamp": "2026-01-11T12:31:09.000Z",
  "state": "AWAKE",
  "substate": "IDLE",
  "watcher_pid": 3523456,
  "channel": "aqara-trv-automation"
}
```

### 3. Who Script
**Location:** `/mnt/shared/collab/scripts/who`

Shows agent status:
```
AGENT STATUS
─────────────────────────────────────────────────────────────────
AGENT        STATE           LAST SEEN  CHANNEL              WATCHER
─────────────────────────────────────────────────────────────────
codex-1      AWAKE/IDLE      2s ago     aqara-trv-automation [watcher:3523456]
claude-1     OFFLINE         (no presence file)
```

### 4. Long-term Memory Integration
The watcher includes CURRENT-STATE.md (first 100 lines) in every Codex invocation, giving Codex "semantic memory" across sessions.

### 5. Collab Snapshot Tool
**Location:** `/mnt/shared/collab/scripts/collab-snapshot`

Saves channel state to log server:
```bash
/mnt/shared/collab/scripts/collab-snapshot aqara-trv-automation
# View at: http://claude:8090/
```

### 6. Duplicate Response Fix
The watcher now correctly deduplicates Codex responses (Codex outputs each response twice; we extract only one copy).

---

## Evidence Bundle

### Logs
- Watcher log: `/mnt/shared/collab/logs/codex-watcher.log`
- Session snapshots: `~/claude-logs/collab-watch-*.html`

### Test Evidence
- Deduplication verified: msg-20260111-123125-codex-d344.json ("Paris" - single response)
- Memory verified: msg-20260111-103558-codex-ea40.json (Codex recalled frameworks from CURRENT-STATE.md)
- Multi-turn discussion: 10+ messages exchanged via watcher

### Git Commits
- `~/agent-collab/` contains committed scripts

---

## Known Limitations

1. **Claude watcher not implemented** - Only Codex has a watcher; Claude responds manually
2. **Presence staleness** - Presence file only updates on message activity, not heartbeat
3. **No gemini-1 yet** - Graeme has API key; integration pending

---

## Phase 2 Scope (Not Started)

Per `/mnt/shared/collab/docs/conscious-agent-architecture.md`:
- Direct message channels (agent-to-agent)
- Priority queue (urgent vs normal messages)
- Claude watcher (symmetric to Codex)
- Gemini integration

---

## Key Files

| What | Where |
|------|-------|
| Codex watcher | `/mnt/shared/collab/scripts/codex-watcher` |
| Who script | `/mnt/shared/collab/scripts/who` |
| Snapshot tool | `/mnt/shared/collab/scripts/collab-snapshot` |
| Presence files | `/mnt/shared/collab/presence/` |
| Watcher logs | `/mnt/shared/collab/logs/codex-watcher.log` |
| Architecture doc | `/mnt/shared/collab/docs/conscious-agent-architecture.md` |
| Current state | `/mnt/shared/collab/CURRENT-STATE.md` |

---

## How to Resume

```bash
# 1. Check who's awake
/mnt/shared/collab/scripts/who

# 2. Start Codex watcher if not running
tmux new-session -d -s codex-watcher '/mnt/shared/collab/scripts/codex-watcher aqara-trv-automation'

# 3. Send a message
/mnt/shared/collab/scripts/send-message --to codex-1 "Hello"

# 4. Watch the channel
/mnt/shared/collab/scripts/collab-watch aqara-trv-automation
```
