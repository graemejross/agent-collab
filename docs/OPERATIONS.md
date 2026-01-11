# Multi-Agent OS: Operations Guide

## Monitoring Agent Health

### Presence Files
Check `/mnt/shared/collab/presence/*.json` for agent status:

```bash
# Quick status of all agents
/mnt/shared/collab/scripts/who

# Detailed status of specific agent
cat /mnt/shared/collab/presence/codex-1.json
```

**Presence Fields:**
| Field | Meaning |
|-------|---------|
| `state` | AWAKE or OFFLINE |
| `substate` | IDLE, WORKING, ANALYZING |
| `timestamp` | Last heartbeat |
| `watcher_pid` | Process ID |

### Watcher Logs
Logs are stored in `/mnt/shared/collab/logs/`:

```bash
# View recent log entries
tail -50 /mnt/shared/collab/logs/codex-watcher.log

# Watch live
tail -f /mnt/shared/collab/logs/codex-watcher.log

# Search for errors
grep -i error /mnt/shared/collab/logs/*.log
```

### Message Bus Activity
Verify messages are flowing:

```bash
# Recent messages in channel
ls -lt /mnt/shared/collab/channels/agent-os-paper/ | head -10

# Watch for new messages
watch -n 2 'ls -lt /mnt/shared/collab/channels/agent-os-paper/ | head -5'

# Live channel view
/mnt/shared/collab/scripts/collab-watch agent-os-paper
```

## Common Operational Tasks

### Check Agent Status
```bash
/mnt/shared/collab/scripts/who
```

Expected output:
```
AGENT        STATE         CHANNEL           LAST SEEN
─────────────────────────────────────────────────────────
codex-1      AWAKE/IDLE    agent-os-paper    5 seconds ago
gemini-1     AWAKE/IDLE    agent-os-paper    3 seconds ago
docs-1       AWAKE/IDLE    agent-os-paper    8 seconds ago
ha-mgr-1     AWAKE/IDLE    agent-os-paper    2 seconds ago
```

### Start a Watcher
```bash
tmux new-session -d -s codex-watcher '/mnt/shared/collab/scripts/codex-watcher agent-os-paper'
```

### Stop a Watcher
```bash
tmux kill-session -t codex-watcher
```

### Restart a Watcher
```bash
tmux kill-session -t codex-watcher 2>/dev/null
sleep 2
tmux new-session -d -s codex-watcher '/mnt/shared/collab/scripts/codex-watcher agent-os-paper'
```

### List Running Watchers
```bash
tmux ls | grep watcher
```

### Attach to Watcher (view live)
```bash
tmux attach -t codex-watcher
# Press Ctrl-B D to detach
```

### Send Test Message
```bash
COLLAB_SESSION=agent-os-paper COLLAB_AGENT=human \
  /mnt/shared/collab/scripts/send-message codex-1 "Health check - please respond"
```

## Incident Response

### 1. Triage
- Identify affected agents and channels
- Capture timestamps and error snippets
- Check presence files for last known state
- Use triage-1 for severity classification:
  ```bash
  send-message triage-1 "Incident: codex-1 not responding to messages since 14:00"
  ```

### 2. Containment
- Stop only the misbehaving watcher (avoid global shutdown)
- Other agents continue operating
  ```bash
  tmux kill-session -t codex-watcher
  ```

### 3. Diagnosis
Check in order:
1. **Presence file** - Is agent marked OFFLINE?
2. **Watcher log** - Any errors?
3. **Last messages** - Did it process recent messages?
4. **API credentials** - Still valid?
5. **Disk space** - Channel directory full?

```bash
# Quick diagnostic
cat /mnt/shared/collab/presence/codex-1.json
tail -30 /mnt/shared/collab/logs/codex-watcher.log
ls -lt /mnt/shared/collab/channels/agent-os-paper/ | head -5
df -h /mnt/shared/collab
```

### 4. Recovery
```bash
# Restart the watcher
tmux kill-session -t codex-watcher 2>/dev/null
tmux new-session -d -s codex-watcher '/mnt/shared/collab/scripts/codex-watcher agent-os-paper'

# Verify it's running
sleep 3
/mnt/shared/collab/scripts/who | grep codex

# Re-send last message if needed
send-message codex-1 "Retry: <original request>"
```

### 5. Post-Incident
- Document root cause
- Update LESSONS-LEARNED if applicable
- Consider guardrail improvements
- Update monitoring if gap identified

## Health Check Script

Quick script to check all agents:

```bash
#!/bin/bash
# health-check.sh

echo "=== Agent Health Check ==="
echo ""

for agent in codex-1 gemini-1 docs-1 qc-1 triage-1 ha-mgr-1 bags-1; do
    presence="/mnt/shared/collab/presence/${agent}.json"
    if [[ -f "$presence" ]]; then
        state=$(jq -r '.state + "/" + .substate' "$presence")
        ts=$(jq -r '.timestamp' "$presence")
        echo "$agent: $state (last: $ts)"
    else
        echo "$agent: NO PRESENCE FILE"
    fi
done

echo ""
echo "=== Watcher Processes ==="
tmux ls 2>/dev/null | grep watcher || echo "No watchers running"
```

## Scheduled Tasks

### Daily Health Check
Add to cron:
```bash
0 9 * * * /mnt/shared/collab/scripts/health-check.sh >> /var/log/agent-health.log
```

### Log Rotation
Logs grow indefinitely; rotate weekly:
```bash
# /etc/logrotate.d/agent-collab
/mnt/shared/collab/logs/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

### Channel Archival
Archive old channels periodically:
```bash
/mnt/shared/collab/scripts/collab-snapshot agent-os-paper
```
