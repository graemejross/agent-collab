# Multi-Agent OS: Communication Protocols

## Message Format

All messages are JSON files with this schema:

```json
{
  "id": "msg-20260111-163315-claude-4c78",
  "timestamp": "2026-01-11T16:33:15.123Z",
  "session_id": "agent-os-paper",
  "from": "claude",
  "to": "codex",
  "type": "chat",
  "content": {
    "text": "Your message text here",
    "code": null,
    "artifacts": []
  },
  "metadata": {
    "mode": "chat",
    "turn": "claude",
    "in_reply_to": "msg-20260111-163300-codex-a1b2"
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique message identifier |
| `timestamp` | string | Yes | ISO-8601 UTC timestamp |
| `session_id` | string | Yes | Channel/session name |
| `from` | string | Yes | Sender agent ID |
| `to` | string | Yes | Recipient: agent ID or "all" |
| `type` | string | Yes | Message type (see below) |
| `content.text` | string | Yes | Message body |
| `content.code` | string | No | Code block if any |
| `content.artifacts` | array | No | File references |
| `metadata.mode` | string | No | "chat" or "watcher" |
| `metadata.in_reply_to` | string | No | Parent message ID |

### Message Types

| Type | Sender | Purpose |
|------|--------|---------|
| `chat` | Any | General conversation |
| `task_assign` | Supervisor | Work assignment |
| `task_result` | Worker | Completion report |
| `review_vote` | Verifier | Approval/rejection |
| `ha_report` | ha-mgr-1 | HA status update |
| `bag_analysis` | bags-1 | Bag journey report |
| `incident` | Any | Problem report |
| `docs` | docs-1 | Documentation update |
| `qc_review` | qc-1 | Quality check result |

## File Naming Convention

```
msg-{YYYYMMDD}-{HHMMSS}-{agent}-{hex4}.json
```

**Components:**
- `msg-` - Fixed prefix
- `YYYYMMDD` - Date in UTC
- `HHMMSS` - Time in UTC
- `agent` - Sender ID (e.g., claude, codex, supervisor, qc-1)
- `hex4` - 4-character random hex for uniqueness

**Examples:**
```
msg-20260111-163315-claude-4c78.json
msg-20260111-163321-codex-9099.json
msg-20260111-163326-supervisor-4e99.json
msg-20260111-155709-qc-1-b4f6.json
```

## Channel Semantics

### Directory Structure
```
/mnt/shared/collab/channels/{channel-name}/
├── msg-20260111-100000-claude-0001.json
├── msg-20260111-100030-codex-0002.json
└── msg-20260111-100045-gemini-0003.json
```

### Properties
- **Append-only**: Messages never modified after creation
- **Chronological**: Filename ordering = time ordering
- **Atomic writes**: Write to .tmp, then rename
- **Readable by all**: Any agent can read any channel

### Channel Types
| Channel | Purpose |
|---------|---------|
| `agent-os-paper` | Multi-agent OS development |
| `human-supervisor` | Human ↔ Supervisor (future) |
| `team-{name}` | Project-specific discussion |

## Addressing

### Direct Address
Set `"to": "agent-id"` to address a specific agent:
```json
{"to": "codex", "text": "@codex Please review this code"}
```

### Broadcast
Set `"to": "all"` for messages to everyone:
```json
{"to": "all", "text": "Team update: Phase 1 complete"}
```

### Mentions
Include `@agent-id` in text to get agent's attention:
```json
{"to": "all", "text": "@codex @gemini Please review"}
```

## Watcher Pattern

### Detection Logic (`is_for_us`)

Watchers respond when ANY of these match:
1. `to` field equals agent ID
2. Text contains `@{agent-id}` mention
3. Text starts with agent ID (fallback)

```bash
is_for_us() {
    local to=$(jq -r '.to' "$file")
    local text=$(jq -r '.content.text' "$file")

    [[ "$to" == "$AGENT" ]] && return 0
    echo "$text" | grep -q "@${AGENT}" && return 0
    echo "$text" | grep -qi "^${AGENT}" && return 0
    return 1
}
```

### Response Flow

```
1. Daemon polls channel directory (2s cycle, NFS-compatible)
2. Daemon reads new file, checks is_for_us()
3. If not for us: log and skip
4. If from us: skip (prevent loops)
5. Gather context (recent messages, memory)
6. Build prompt with role and guardrails
7. Call CLI (codex exec, claude --print, etc.)
8. Extract response text
9. Post response as new message (atomic write + NATS dual-write)
10. Update presence to IDLE
```

> **Note:** We use polling instead of `inotifywait` because inotifywait doesn't
> work reliably on NFS mounts (misses file creation events).

### Avoiding Loops

Watchers skip messages they sent:
```bash
is_from_us() {
    local from=$(jq -r '.from' "$file")
    [[ "$from" == "$AGENT" ]]
}
```

## send-message Script

### Usage
```bash
# Direct to agent
./send-message.py --agent supervisor --channel agent-os-paper --to codex --text "Please review this"

# Broadcast
./send-message.py --agent supervisor --channel agent-os-paper --to all --text "Team announcement"
```

### Agent ID Patterns

| Type | Pattern | Examples |
|------|---------|----------|
| Core Workers | `{model}` | `claude`, `codex`, `gemini` |
| Supervisor | `supervisor` | `supervisor` |
| Specialists | `{role}-{n}` | `qc-1`, `docs-1`, `bags-1` |

**Deprecated:** `claude-1`, `codex-1`, `gemini-1` (legacy, no longer used)

## Presence Protocol

### Heartbeat File
```json
{
  "agent_id": "codex",
  "timestamp": "2026-01-11T16:30:00.000Z",
  "state": "AWAKE",
  "substate": "IDLE",
  "watcher_pid": 12345,
  "channel": "agent-os-paper"
}
```

### State Transitions
```
START → AWAKE/IDLE
AWAKE/IDLE → AWAKE/WORKING (message received)
AWAKE/WORKING → AWAKE/IDLE (response posted)
AWAKE/* → OFFLINE (watcher shutdown)
```

### Checking Presence
```bash
# List all agents
/mnt/shared/collab/scripts/who

# Check specific agent
cat /mnt/shared/collab/signals/presence/codex.json
```

## Error Handling

### Failed Invocations
- Watcher logs error to `/mnt/shared/collab/logs/{watcher}.log`
- No response posted to channel
- Presence remains AWAKE/IDLE (ready for retry)

### Malformed Messages
- Watcher logs warning
- Message skipped
- No crash (graceful degradation)

### Model API Errors
- Error logged with details
- Retry not automatic (human intervention)
- Presence updated to IDLE
