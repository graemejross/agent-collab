# How to Add a New Agent

This guide walks through adding a new specialized agent to the multi-agent system.

## Overview

Adding a new agent requires:
1. Define the agent's role and capabilities
2. Create a registry entry
3. Create an API wrapper (if needed)
4. Create a watcher script
5. Test the agent
6. Commit to git

## Step 1: Define the Agent

Before coding, answer these questions:

| Question | Example Answer |
|----------|----------------|
| What is the agent's purpose? | Monitor backup job status |
| What model should it use? | Gemini Flash (cheap, fast checks) |
| What cost tier? | 1 (simple monitoring task) |
| What tools does it need? | SSH to backup server, read logs |
| What guardrails? | Read-only, no delete operations |
| What triggers it? | @backup-1 mentions |

## Step 2: Create Registry Entry

Create `/mnt/shared/collab/registry/agents/{agent-id}.json`:

```json
{
  "id": "backup-1",
  "model": "gemini-2.5-flash",
  "provider": "google",
  "capabilities": [
    "backup-monitoring",
    "job-status-checking",
    "alert-generation"
  ],
  "role": "specialist",
  "status": "active",
  "registered": "2026-01-11T12:00:00Z",
  "cost_tier": 1,
  "guardrails": {
    "read_only": true,
    "no_delete_operations": true,
    "servers": ["backup-server-1", "backup-server-2"]
  },
  "notes": "Backup monitoring specialist. Checks job status, alerts on failures."
}
```

## Step 3: Create API Wrapper (if needed)

If using a model not yet supported, create an exec wrapper.

**Example: `backup-exec` using Gemini**

```bash
#!/bin/bash
# Just use existing gemini-exec
exec /mnt/shared/collab/scripts/gemini-exec "$@"
```

Or create a new wrapper if needed (see `haiku-exec`, `sonnet-exec` for examples).

## Step 4: Create Watcher Script

Create `/mnt/shared/collab/scripts/{agent}-watcher`:

```bash
#!/bin/bash
#
# backup-watcher - Backup monitoring agent watcher
#

set -e

CHANNEL="${1:-agent-os-paper}"
CHANNEL_DIR="/mnt/shared/collab/channels/${CHANNEL}"
PRESENCE_DIR="/mnt/shared/collab/presence"
SCRIPTS_DIR="/mnt/shared/collab/scripts"
AGENT="backup-1"
LOG_FILE="/mnt/shared/collab/logs/backup-watcher.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE" >&2; }
log_info() { log "${CYAN}INFO${NC}: $1"; }
log_ok() { log "${GREEN}OK${NC}: $1"; }
log_err() { log "${RED}ERROR${NC}: $1"; }

mkdir -p "${PRESENCE_DIR}" "$(dirname "${LOG_FILE}")" 2>/dev/null || true

update_presence() {
    cat > "${PRESENCE_DIR}/${AGENT}.json" << EOF
{
  "agent_id": "${AGENT}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
  "state": "AWAKE",
  "substate": "${1:-IDLE}",
  "watcher_pid": $$,
  "channel": "${CHANNEL}"
}
EOF
}

is_for_us() {
    local file="$1"
    local to=$(jq -r '.to // "all"' "$file" 2>/dev/null)
    local text=$(jq -r '.content.text // ""' "$file" 2>/dev/null)

    [[ "$to" == "$AGENT" ]] && return 0
    echo "$text" | grep -q "@${AGENT}" && return 0
    echo "$text" | grep -qi "^${AGENT}" && return 0
    return 1
}

is_from_us() {
    local from=$(jq -r '.from // ""' "$1" 2>/dev/null)
    [[ "$from" == "$AGENT" ]]
}

get_context() {
    local context=""
    for f in $(ls -t "${CHANNEL_DIR}"/msg-*.json 2>/dev/null | head -5 | tac); do
        local from=$(jq -r '.from' "$f")
        local text=$(jq -r '.content.text // ""' "$f")
        context="${context}[${from}]: ${text}\n\n"
    done
    echo -e "$context"
}

invoke_agent() {
    local message_file="$1"
    local from=$(jq -r '.from' "$message_file")
    local text=$(jq -r '.content.text // ""' "$message_file")
    local context=$(get_context)

    local prompt="You are backup-1, a backup monitoring specialist.

ROLE: Monitor backup job status across servers.
GUARDRAILS: Read-only access. Cannot delete or modify backups.

CONTEXT:
${context}

REQUEST FROM ${from}:
${text}

Respond concisely with backup status information."

    log_info "Invoking agent for request from ${from}..."

    "${SCRIPTS_DIR}/gemini-exec" "$prompt" 2>&1 | head -30
}

post_response() {
    local response_text="$1"
    local in_reply_to="$2"

    python3 << EOF
import json
from datetime import datetime, timezone
from pathlib import Path
import secrets

now = datetime.now(timezone.utc)
msg_id = f"msg-{now.strftime('%Y%m%d-%H%M%S')}-backup-{secrets.token_hex(2)}"

msg = {
    "id": msg_id,
    "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
    "session_id": "${CHANNEL}",
    "from": "backup-1",
    "to": "all",
    "type": "backup_status",
    "content": {"text": """${response_text}""", "code": None, "artifacts": []},
    "metadata": {
        "mode": "watcher",
        "model": "gemini-2.5-flash",
        "role": "backup_specialist",
        "in_reply_to": "${in_reply_to}"
    }
}

Path("${CHANNEL_DIR}") / f"{msg_id}.json").write_text(json.dumps(msg, indent=2))
print(f"Posted: {msg_id}")
EOF
}

main() {
    log_info "Starting ${AGENT} watcher for channel: ${CHANNEL}"

    command -v inotifywait &>/dev/null || { log_err "inotifywait not found"; exit 1; }
    command -v jq &>/dev/null || { log_err "jq not found"; exit 1; }

    update_presence "IDLE"
    log_ok "Presence updated"

    declare -A processed
    for f in "${CHANNEL_DIR}"/msg-*.json; do
        [[ -f "$f" ]] && processed["$(basename "$f")"]=1
    done
    log_info "Marked ${#processed[@]} existing messages as read"

    inotifywait -m -e create -e moved_to "${CHANNEL_DIR}" --format '%f' 2>/dev/null | while read -r filename; do
        [[ "$filename" != msg-*.json ]] && continue
        [[ -n "${processed[$filename]}" ]] && continue
        processed["$filename"]=1

        local filepath="${CHANNEL_DIR}/${filename}"
        sleep 0.5

        is_from_us "$filepath" && continue
        is_for_us "$filepath" || continue

        log_info "New request: ${filename}"
        update_presence "WORKING"

        local msg_id=$(jq -r '.id' "$filepath")
        local response
        if response=$(invoke_agent "$filepath"); then
            [[ -n "$response" ]] && post_response "$response" "$msg_id"
        fi

        update_presence "IDLE"
    done
}

trap 'update_presence "OFFLINE"; exit 0' SIGINT SIGTERM
main "$@"
```

Make it executable:
```bash
chmod +x /mnt/shared/collab/scripts/backup-watcher
```

## Step 5: Test the Agent

### Start the watcher
```bash
tmux new-session -d -s backup-watcher '/mnt/shared/collab/scripts/backup-watcher agent-os-paper'
```

### Check presence
```bash
/mnt/shared/collab/scripts/who
```

### Send test message
```bash
COLLAB_SESSION=agent-os-paper COLLAB_AGENT=human \
  /mnt/shared/collab/scripts/send-message backup-1 "What is the status of last night's backups?"
```

### Check response
```bash
ls -lt /mnt/shared/collab/channels/agent-os-paper/msg-*.json | head -3
```

### View watcher log
```bash
tail -20 /mnt/shared/collab/logs/backup-watcher.log
```

## Step 6: Commit to Git

```bash
cd ~/agent-collab

# Copy files
cp /mnt/shared/collab/scripts/backup-watcher .
cp /mnt/shared/collab/registry/agents/backup-1.json registry/agents/

# Create issue first!
gh issue create --title "Add backup-1 monitoring agent" --body "..."

# Commit
git add backup-watcher registry/agents/backup-1.json
git commit -m "Add backup-1 monitoring agent

Fixes #N

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push
```

## Checklist

- [ ] Registry entry created with correct schema
- [ ] Watcher script created and executable
- [ ] API wrapper available (existing or new)
- [ ] Presence updates working
- [ ] Message detection working (is_for_us)
- [ ] Response posting working
- [ ] Tested with sample message
- [ ] Guardrails documented
- [ ] GitHub issue created
- [ ] Committed and pushed
- [ ] AGENT-SPEC.md updated

## Common Patterns

### Using Different Models

| Model | Exec Script | When to Use |
|-------|-------------|-------------|
| Gemini Flash | `gemini-exec` | Quick checks, triage |
| Claude Haiku | `haiku-exec` | Documentation, formatting |
| Claude Sonnet | `sonnet-exec` | Complex analysis |
| Codex | SSH + `codex exec` | Code generation |

### Adding Domain Context

Include domain-specific context in the prompt:
```bash
local glossary=$(cat /path/to/GLOSSARY.md | head -50)
local prompt="...
DOMAIN GLOSSARY:
${glossary}
..."
```

### Structured Output

For agents that need structured responses:
```bash
local prompt="...
OUTPUT FORMAT:
STATUS: OK|WARNING|ERROR
DETAILS: <explanation>
ACTION: <recommended action>
..."
```
